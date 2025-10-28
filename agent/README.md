# RegenAI Agent Module

## Overview
This module implements a LangGraph-based conversational AI agent that provides personalized agricultural recommendations to farmers based on their land characteristics.

## Architecture

### Components

#### 1. `main_agent.py`
Core LangGraph workflow implementation:
- **AgentState**: Dictionary-based state management
- **build_graph()**: Constructs the conversation workflow
- **get_agent()**: Returns compiled graph with memory checkpointer

**Workflow Steps:**
1. `enrich` - Enriches state with weather & market context
2. `reply` - Generates AI response using Gemini 2.0 Flash

#### 2. `tools.py`
Helper functions for data retrieval:
- `get_user_latest_form(db, user_id)` - Fetches user's most recent land form
- `fetch_weather_context(form)` - Gets weather data (placeholder)
- `fetch_market_context(form)` - Gets market trends (placeholder)

#### 3. `prompt.py`
Contains the system prompt for the AI agent:
- Defines agent's role as agronomy co-pilot
- Sets tone and response format expectations

## State Flow

```python
state = {
    "user_id": int,        # User ID from auth
    "form": dict,          # Latest land form data
    "message": str,        # User's chat message
    "context": dict,       # Enriched weather/market data
    "reply": str           # AI generated response
}
```

## LLM Configuration

Currently using **Gemini 2.0 Flash**:
```python
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    api_key=EnvironmentConfig.GEMINI_API_KEY,  # from GEMINI_API_KEY_ALI
    temperature=0.6,
)
```

### Why Gemini?
- Fast response times
- Good agricultural domain knowledge
- Cost-effective for production use
- Supports long context windows

### Switching to Other Models

**OpenAI:**
```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=EnvironmentConfig.OPENAI_API_KEY,
    temperature=0.6,
)
```

**Anthropic Claude:**
```python
from langchain_anthropic import ChatAnthropic

llm = ChatAnthropic(
    model="claude-3-sonnet-20240229",
    api_key=os.getenv("ANTHROPIC_API_KEY"),
    temperature=0.6,
)
```

## Memory Management

### Current: In-Memory (MemorySaver)
- Conversations persist during server runtime
- Lost on server restart
- Good for development/testing

### Production: PostgreSQL Checkpointer
```python
from langgraph.checkpoint.postgres import PostgresSaver

def get_agent():
    checkpointer = PostgresSaver.from_conn_string(
        EnvironmentConfig.get_database_url()
    )
    graph = build_graph()
    return graph.compile(checkpointer=checkpointer)
```

Benefits:
- Conversations persist across restarts
- Scalable across multiple server instances
- Can query/analyze conversation history

## Extending the Agent

### Adding New Tools

1. Create tool function in `tools.py`:
```python
def fetch_soil_analysis(location: str) -> Dict[str, Any]:
    # Call soil testing API
    return {"ph": 6.5, "nitrogen": "medium", ...}
```

2. Update workflow in `main_agent.py`:
```python
def enrich_context(state: AgentState) -> AgentState:
    form = state.get("form", {})
    weather = fetch_weather_context(form)
    market = fetch_market_context(form)
    soil = fetch_soil_analysis(form.get("location"))  # New!
    
    state["context"] = {
        "weather": weather,
        "market": market,
        "soil": soil  # New!
    }
    return state
```

### Adding Conditional Logic

Example: Route to different nodes based on user intent:
```python
from langgraph.graph import StateGraph, END

def route_query(state: AgentState) -> str:
    message = state.get("message", "").lower()
    if "weather" in message:
        return "weather_specialist"
    elif "market" in message or "price" in message:
        return "market_specialist"
    else:
        return "general"

graph = StateGraph(AgentState)
graph.add_node("router", route_query)
graph.add_node("weather_specialist", weather_handler)
graph.add_node("market_specialist", market_handler)
graph.add_node("general", general_handler)

graph.set_entry_point("router")
graph.add_conditional_edges(
    "router",
    route_query,
    {
        "weather_specialist": "weather_specialist",
        "market_specialist": "market_specialist",
        "general": "general"
    }
)
```

### Adding Multi-turn Planning

For complex queries requiring multiple steps:
```python
def plan_steps(state: AgentState) -> AgentState:
    query = state.get("message")
    # Use LLM to break down complex query
    plan = llm.invoke(f"Break this into steps: {query}")
    state["plan"] = parse_plan(plan)
    return state

def execute_step(state: AgentState) -> AgentState:
    plan = state.get("plan", [])
    if plan:
        current_step = plan.pop(0)
        result = execute(current_step)
        state["results"].append(result)
    return state

def should_continue(state: AgentState) -> str:
    if state.get("plan"):
        return "execute_step"
    else:
        return "summarize"
```

## Prompt Engineering

### Current Prompt Strategy
Simple, direct instruction in `generate_reply()`:
```python
system = (
    "You are an agronomy assistant. Use user's land details, "
    "recent weather, and market trends to recommend crops, "
    "target markets, and best options. Be concise, friendly, and actionable."
)
prompt = f"{system}\n\nUser land form: {form}\nContext: {context}\n\nUser: {user_message}\nAssistant:"
```

### Enhanced Prompt (Few-shot Learning)
```python
from agent.prompt import SYSTEM_PROMPT, EXAMPLE_CONVERSATIONS

prompt = f"""{SYSTEM_PROMPT}

Example conversations:
{EXAMPLE_CONVERSATIONS}

Current user's land:
{json.dumps(form, indent=2)}

Weather & Market Context:
{json.dumps(context, indent=2)}

Conversation:
User: {user_message}
Assistant:"""
```

### Structured Output
Force specific format using schema:
```python
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

class CropRecommendation(BaseModel):
    crop_name: str = Field(description="Recommended crop")
    reasoning: str = Field(description="Why this crop fits")
    planting_window: str = Field(description="When to plant")
    expected_yield: str = Field(description="Estimated harvest")
    market_potential: str = Field(description="Where to sell")

parser = JsonOutputParser(pydantic_object=CropRecommendation)
prompt = parser.get_format_instructions() + "\n\n" + user_query
ai_response = llm.invoke(prompt)
structured_output = parser.parse(ai_response.content)
```

## Testing

### Unit Tests
```python
# tests/test_agent_tools.py
def test_get_user_latest_form(db_session):
    user_id = 1
    form = get_user_latest_form(db_session, user_id)
    assert form["location"] == "Lahore"
    assert form["soil_type"] == "Loamy"

def test_fetch_weather_context():
    form = {"location": "Lahore"}
    weather = fetch_weather_context(form)
    assert "summary" in weather
```

### Integration Tests
```python
# tests/test_agent_integration.py
def test_agent_workflow():
    agent = get_agent()
    state = {
        "user_id": 1,
        "form": {...},
        "message": "What should I plant?"
    }
    result = agent.invoke(state, {"configurable": {"thread_id": "test-123"}})
    assert "reply" in result
    assert len(result["reply"]) > 0
```

## Performance Optimization

### Caching
Cache weather/market data to reduce API calls:
```python
from functools import lru_cache
from datetime import datetime, timedelta

@lru_cache(maxsize=100)
def fetch_weather_context_cached(location: str, date: str) -> Dict:
    # date parameter for cache invalidation
    return fetch_weather_api(location)

# In enrich_context:
today = datetime.now().strftime("%Y-%m-%d")
weather = fetch_weather_context_cached(form["location"], today)
```

### Async Processing
For non-blocking API calls:
```python
import asyncio
from langchain_google_genai import ChatGoogleGenerativeAI

async def enrich_context_async(state: AgentState) -> AgentState:
    form = state.get("form", {})
    
    # Fetch weather and market in parallel
    weather_task = asyncio.create_task(fetch_weather_async(form))
    market_task = asyncio.create_task(fetch_market_async(form))
    
    weather, market = await asyncio.gather(weather_task, market_task)
    
    state["context"] = {"weather": weather, "market": market}
    return state
```

## Monitoring & Logging

Add logging for debugging and analytics:
```python
import logging

logger = logging.getLogger(__name__)

def generate_reply(state: AgentState) -> AgentState:
    user_id = state.get("user_id")
    message = state.get("message")
    
    logger.info(f"User {user_id} query: {message}")
    
    try:
        ai = llm.invoke(prompt)
        reply = ai.content
        
        logger.info(f"Generated reply length: {len(reply)}")
        state["reply"] = reply
        
    except Exception as e:
        logger.error(f"LLM error for user {user_id}: {str(e)}")
        state["reply"] = "I'm having trouble right now. Please try again."
    
    return state
```

## Common Issues

### Issue: Agent gives generic responses
**Solution:** Ensure form data is being passed correctly. Add logging to verify.

### Issue: Slow response times
**Solutions:**
1. Use faster model (gpt-4o-mini instead of gpt-4)
2. Reduce context size
3. Cache external API calls
4. Consider streaming responses

### Issue: Context limit exceeded
**Solutions:**
1. Summarize long conversations
2. Only include last N messages
3. Use a model with larger context window

### Issue: Inconsistent recommendations
**Solutions:**
1. Lower temperature (e.g., 0.3)
2. Use structured output schemas
3. Add more specific examples in prompt
4. Implement response validation

## Best Practices

1. **Always validate user input** before passing to LLM
2. **Set reasonable token limits** to control costs
3. **Implement retry logic** for API failures
4. **Log all conversations** for improvement
5. **A/B test prompts** to optimize quality
6. **Monitor token usage** and costs
7. **Implement rate limiting** per user
8. **Cache expensive operations**
9. **Use streaming** for better UX
10. **Version your prompts** for reproducibility

