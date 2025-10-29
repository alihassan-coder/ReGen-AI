from typing import Any, Dict, TypedDict
import logging
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_google_genai import ChatGoogleGenerativeAI
from config.env_config import EnvironmentConfig
from agent.tools import get_user_latest_form, fetch_weather_context, fetch_market_context, web_search

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class AgentState(TypedDict, total=False):
    """State schema for the agent graph"""
    user_id: int
    form: Dict[str, Any]
    message: str
    context: Dict[str, Any]
    reply: str
    conversation_history: list  # Store last 3 messages for context
    search_results: Dict[str, Any]  # Web search results to show in frontend


def build_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    # Validate API key
    if not EnvironmentConfig.GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY_ALI not found in environment")
        raise ValueError(
            "GEMINI_API_KEY_ALI not found in environment. "
            "Please set it in your .env file. "
            "Get your key from: https://makersuite.google.com/app/apikey"
        )
    
    logger.info(f"Initializing Gemini with API key: {EnvironmentConfig.GEMINI_API_KEY[:10]}...")

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        api_key=EnvironmentConfig.GEMINI_API_KEY,
        temperature=0.6,
    )

    def decide_search(state: AgentState) -> AgentState:
        """Decide if web search is needed based on the user's question"""
        user_message = state.get("message", "").lower()
        
        # Keywords that suggest need for current/real-time information
        search_keywords = [
            "current", "latest", "recent", "today", "now", "2024", "2025",
            "price", "market price", "cost", "news", "update",
            "weather forecast", "climate data", "research", "study"
        ]
        
        needs_search = any(keyword in user_message for keyword in search_keywords)
        
        if needs_search:
            logger.info(f"Web search needed for query: {user_message[:50]}")
            # Perform web search
            search_query = f"{user_message} Pakistan agriculture farming"
            search_data = web_search(search_query, max_results=3)
            
            return {
                **state,
                "search_results": search_data
            }
        else:
            logger.info("No web search needed")
            return {
                **state,
                "search_results": {}
            }
    
    def enrich_context(state: AgentState) -> AgentState:
        try:
            form = state.get("form", {})
            message = state.get("message", "")
            logger.info(f"Enriching context - form type: {type(form)}, has data: {bool(form)}, message: '{message[:50]}'")
            if form:
                logger.info(f"Form location: {form.get('location', 'N/A')}")
            weather = fetch_weather_context(form if isinstance(form, dict) else {})
            market = fetch_market_context(form if isinstance(form, dict) else {})
            
            # Return updated state with context added
            return {
                **state,  # Preserve all existing state
                "context": {"weather": weather, "market": market}
            }
        except Exception as e:
            logger.error(f"Error enriching context: {e}", exc_info=True)
            return {
                **state,
                "context": {"weather": {}, "market": {}}
            }

    def generate_reply(state: AgentState) -> AgentState:
        logger.info(f"generate_reply called - state keys: {list(state.keys())}")
        form = state.get("form", {})
        context = state.get("context", {})
        user_message = state.get("message", "")
        
        logger.info(f"User message: '{user_message}'")
        
        if not user_message:
            logger.warning("No user message found in state")
            return {
                **state,
                "reply": "I didn't receive your message. Please try again."
            }
        
        # Build context-aware prompt
        system = (
            "You are ReGenAI Assistant, a friendly AI farming advisor for Pakistan.\n\n"
            
            "**Core Rules:**\n"
            "1. **Be Conversational**: Chat naturally like a helpful friend\n"
            "2. **Stay Focused**: Answer ONLY what the user asks - don't give extra information\n"
            "3. **Be Brief**: Keep responses short (2-3 sentences for simple questions, 1 paragraph for advice)\n"
            "4. **REMEMBER EVERYTHING**: You MUST remember and use information from previous messages:\n"
            "   - If user says 'my name is X', remember X is their name\n"
            "   - If user asks 'what is my name?', answer with the exact name they told you\n"
            "   - Remember their preferences, questions, and any personal info they share\n"
            "5. **Personalize**: Reference their farm details and previous conversation when relevant\n\n"
            
            "**Response Guidelines:**\n"
            "- **Simple greetings** (hi, hello): Respond warmly in 1-2 sentences, ask how you can help\n"
            "- **Personal info** (my name is X): Acknowledge and remember it. Use it in future responses\n"
            "  Example: User says 'hi my name is alihassan' → Remember: name = alihassan\n"
            "  Later user asks 'what is my name?' → Answer: 'Your name is alihassan'\n"
            "- **Questions about you**: Briefly explain you're an AI farming assistant (1-2 sentences)\n"
            "- **Farming questions**: Give direct, practical answers. Use bullet points only if listing steps\n"
            "- **Follow-up questions**: Reference previous conversation naturally\n\n"
            
            "**Length Guidelines:**\n"
            "- Greetings/casual chat: 1-2 sentences\n"
            "- Simple questions: 2-3 sentences\n"
            "- Advice/recommendations: 1 short paragraph (4-5 sentences max)\n"
            "- Complex topics: 2 paragraphs maximum with bullet points if needed\n\n"
            
            "**What NOT to do:**\n"
            "- Don't give long explanations unless asked\n"
            "- Don't list everything you know about a topic\n"
            "- Don't repeat information already in conversation\n"
            "- Don't be overly formal - be friendly and natural"
        )
        
        # Add farm context if available
        farm_info = ""
        if form:
            details = []
            if form.get('location'):
                details.append(f"Location: {form.get('location')}")
            if form.get('soil_type'):
                details.append(f"Soil Type: {form.get('soil_type')}")
            if form.get('land_size'):
                details.append(f"Land Size: {form.get('land_size')} acres")
            if form.get('goal'):
                details.append(f"Farming Goal: {form.get('goal')}")
            if form.get('water_source'):
                details.append(f"Water Source: {form.get('water_source')}")
            if form.get('irrigation'):
                details.append(f"Irrigation: {form.get('irrigation')}")
            if form.get('specific_crop'):
                details.append(f"Interested in: {form.get('specific_crop')}")
            if form.get('fertilizers_preference'):
                details.append(f"Fertilizer Preference: {form.get('fertilizers_preference')}")
            
            if details:
                farm_info = "\n\n**User's Farm Profile:**\n" + "\n".join(f"- {d}" for d in details)
                farm_info += "\n\n(Use this information to personalize your advice)"
        
        context_info = ""
        if context:
            weather = context.get('weather', {})
            market = context.get('market', {})
            if weather:
                context_info += f"\n\nWeather Context: {weather.get('summary', 'N/A')}"
            if market:
                context_info += f"\n\nMarket Trends: {', '.join(market.get('demand_trends', []))}"
        
        # Build the complete prompt
        prompt_parts = [system]
        
        if farm_info:
            prompt_parts.append(farm_info)
        
        if context_info:
            prompt_parts.append(context_info)
        
        # Add web search results if available
        search_results = state.get("search_results", {})
        if search_results and search_results.get("success"):
            search_info = "\n\n**Web Search Results:**"
            if search_results.get("answer"):
                search_info += f"\nQuick Answer: {search_results['answer']}"
            
            for idx, result in enumerate(search_results.get("results", [])[:3], 1):
                search_info += f"\n\n{idx}. **{result['title']}**"
                search_info += f"\n   {result['content']}"
                search_info += f"\n   Source: {result['url']}"
            
            search_info += "\n\n(Use this current information to provide up-to-date advice)"
            prompt_parts.append(search_info)
            logger.info("Added web search results to prompt")
        
        # Add conversation history (last 3 exchanges only to manage context window)
        conversation_history = state.get("conversation_history", [])
        logger.info(f"Conversation history available: {len(conversation_history)} messages")
        if conversation_history:
            logger.info(f"History content: {conversation_history}")
            # Keep only last 3 exchanges (6 messages total: 3 user + 3 assistant)
            recent_history = conversation_history[-6:] if len(conversation_history) > 6 else conversation_history
            if recent_history:
                prompt_parts.append("\n\n**Previous Conversation (Remember this context!):**")
                for i, msg in enumerate(recent_history):
                    role = msg.get("role", "user")
                    content = msg.get("content", "")
                    if role == "user":
                        prompt_parts.append(f"\nUser said: {content}")
                    else:
                        prompt_parts.append(f"\nYou replied: {content}")
                
                prompt_parts.append("\n\n**CRITICAL INSTRUCTIONS - READ CAREFULLY:**")
                prompt_parts.append("\n1. Look at the conversation history above")
                prompt_parts.append("\n2. Extract key information:")
                prompt_parts.append("\n   - If user said 'hi my name is X' or 'my name is X', extract X as their name")
                prompt_parts.append("\n   - If user mentioned crops, preferences, or plans, remember them")
                prompt_parts.append("\n3. When user asks 'what is my name?', answer with the EXACT name from history")
                prompt_parts.append("\n4. NEVER say 'I don't know' or 'I don't have access' if the info is in the history above")
                prompt_parts.append("\n\nExample:")
                prompt_parts.append("\n  History shows: 'User said: hi my name is alihassan'")
                prompt_parts.append("\n  User asks: 'what is my name?'")
                prompt_parts.append("\n  Correct answer: 'Your name is alihassan' or 'You told me your name is alihassan'")
        
        # Add current message
        prompt_parts.append("\n\n---\n\n**Current User Message:**")
        prompt_parts.append(f"\n{user_message}")
        prompt_parts.append("\n\n**Your Response (remember to use conversation history):**")
        
        prompt = "".join(prompt_parts)
        
        # Log prompt size to monitor context window
        logger.info(f"Prompt size: {len(prompt)} characters, ~{len(prompt)//4} tokens")
        
        try:
            logger.info(f"Invoking LLM with prompt length: {len(prompt)}")
            ai = llm.invoke(prompt)
            logger.info(f"LLM response received: {bool(ai.content)}")
            reply = ai.content if ai.content else "I'm here to help! Could you please rephrase your question?"
        except Exception as e:
            logger.error(f"LLM invocation error: {type(e).__name__}: {str(e)}")
            error_msg = str(e)
            if "API key" in error_msg or "authentication" in error_msg.lower():
                reply = (
                    "API authentication failed. Please check your GEMINI_API_KEY_ALI in the .env file. "
                    f"Error: {error_msg[:200]}"
                )
            else:
                reply = (
                    "I'm experiencing technical difficulties right now. "
                    f"Error: {error_msg[:200]}"
                )
        
        # Update conversation history (keep only last 3 exchanges = 6 messages)
        updated_history = conversation_history.copy() if conversation_history else []
        updated_history.append({"role": "user", "content": user_message})
        updated_history.append({"role": "assistant", "content": reply})
        
        # Keep only last 6 messages (3 exchanges)
        if len(updated_history) > 6:
            updated_history = updated_history[-6:]
        
        logger.info(f"Returning state with reply length: {len(reply)}, history size: {len(updated_history)}")
        return {
            **state,
            "reply": reply,
            "conversation_history": updated_history
        }

    graph.add_node("search", decide_search)
    graph.add_node("enrich", enrich_context)
    graph.add_node("reply", generate_reply)
    graph.set_entry_point("search")
    graph.add_edge("search", "enrich")
    graph.add_edge("enrich", "reply")
    graph.add_edge("reply", END)

    return graph


def get_agent():
    # MemorySaver requires a thread_id (we pass per request via configurable)
    # Note: If checkpointer causes issues, we can compile without it
    try:
        memory = MemorySaver()
        graph = build_graph()
        compiled = graph.compile(checkpointer=memory)
        logger.info("Agent compiled successfully with checkpointer")
        return compiled
    except Exception as e:
        logger.error(f"Error compiling agent with checkpointer: {e}")
        # Fallback: compile without checkpointer
        graph = build_graph()
        compiled = graph.compile()
        logger.info("Agent compiled successfully without checkpointer (fallback)")
        return compiled

