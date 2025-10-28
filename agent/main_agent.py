from typing import Any, Dict
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_google_genai import ChatGoogleGenerativeAI
from config.env_config import EnvironmentConfig
from agent.tools import get_user_latest_form, fetch_weather_context, fetch_market_context


class AgentState(dict):
    pass


def build_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        api_key=EnvironmentConfig.GEMINI_API_KEY,
        temperature=0.6,
    )

    def enrich_context(state: AgentState) -> AgentState:
        form = state.get("form", {})
        weather = fetch_weather_context(form)
        market = fetch_market_context(form)
        state["context"] = {"weather": weather, "market": market}
        return state

    def generate_reply(state: AgentState) -> AgentState:
        form = state.get("form")
        context = state.get("context", {})
        user_message = state.get("message", "")
        system = (
            "You are an agronomy assistant. Use user's land details, recent weather, and market trends to recommend crops, target markets, and best options. Be concise, friendly, and actionable."
        )
        prompt = f"{system}\n\nUser land form: {form}\nContext: {context}\n\nUser: {user_message}\nAssistant:"
        ai = llm.invoke(prompt)
        state["reply"] = ai.content
        return state

    graph.add_node("enrich", enrich_context)
    graph.add_node("reply", generate_reply)
    graph.set_entry_point("enrich")
    graph.add_edge("enrich", "reply")
    graph.add_edge("reply", END)

    return graph


def get_agent():
    # MemorySaver requires a thread_id (we pass per request via configurable)
    memory = MemorySaver()
    graph = build_graph()
    return graph.compile(checkpointer=memory)

