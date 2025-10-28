# RegenAI Agent Setup - Complete Guide

## ✅ What Was Implemented

### 1. Database Schema Updates
- Added `user_id` foreign key to `form_responses` table
- All form operations are now scoped to authenticated users
- Migration completed successfully

### 2. LangGraph AI Agent
Built a conversational AI agent using LangGraph with:
- **Gemini 2.0 Flash** as the LLM (configured via `GEMINI_API_KEY_ALI`)
- **Memory persistence** using LangGraph's MemorySaver with thread-based conversations
- **Context enrichment** from user's land form data
- **Weather & market context** (currently placeholder - ready for real API integration)

### 3. Agent Architecture

```
User Request → Auth Check → Fetch Latest Form → LangGraph Agent
                                                      ↓
                                            ┌─────────────────┐
                                            │  Enrich Context │
                                            │  (weather, market)
                                            └─────────────────┘
                                                      ↓
                                            ┌─────────────────┐
                                            │  Generate Reply │
                                            │  (Gemini 2.0)   │
                                            └─────────────────┘
                                                      ↓
                                            Return reply + thread_id
```

### 4. Key Files Modified/Created

- ✅ `agent/main_agent.py` - LangGraph workflow
- ✅ `agent/tools.py` - Helper functions for form/weather/market data
- ✅ `agent/prompt.py` - System prompt
- ✅ `routes/agent_routes.py` - FastAPI chat endpoint
- ✅ `routes/forme_routes.py` - User-scoped CRUD
- ✅ `models/tables_models.py` - Added user_id FK
- ✅ `alembic/versions/4f1a2b3c4d5e_*.py` - Migration for user_id
- ✅ `pyproject.toml` - Added LangGraph dependencies

## 🚀 How to Run

### Step 1: Environment Variables
Create/update `.env` file:
```env
# Database (required)
DATABASE_URL=postgresql://user:pass@host:port/dbname
# or
NEON_DATABASE_URL=postgresql://user:pass@neon.host/dbname

# AI Model (required - using Gemini)
GEMINI_API_KEY_ALI=your_gemini_api_key_here

# Optional
OPENAI_API_KEY=your_openai_key  # Not used currently
```

### Step 2: Install Dependencies
```powershell
.\.venv\Scripts\pip.exe install -e .
```

### Step 3: Database Migration (ALREADY DONE ✅)
```powershell
.\.venv\Scripts\alembic.exe upgrade head
```

### Step 4: Start Server
```powershell
.\.venv\Scripts\uvicorn.exe main:app --reload
```

### Step 5: Test the Agent
```powershell
.\.venv\Scripts\python.exe test_agent.py
```

## 📡 API Usage

### 1. Register/Login
```http
POST /auth/register
Content-Type: application/json

{
  "first_name": "John",
  "last_name": "Farmer",
  "email": "john@example.com",
  "password": "secure123"
}
```

Response:
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

### 2. Create Land Form
```http
POST /forms
Authorization: Bearer <your_token>
Content-Type: application/json

{
  "location": "Lahore, Punjab",
  "area_type": "Plain",
  "soil_type": "Loamy",
  "water_source": "Tube well",
  "irrigation": "Yes",
  "temperature": "Moderate",
  "rainfall": "Medium",
  "sunlight": "Long hours",
  "land_size": "5 acres",
  "goal": "Profit",
  "crop_duration": "2–3 months",
  "specific_crop": "Wheat",
  "fertilizers_preference": "Organic preferred"
}
```

### 3. Chat with Agent
```http
POST /agent/chat
Authorization: Bearer <your_token>
Content-Type: application/json

{
  "message": "What crop should I plant next month?"
}
```

Response:
```json
{
  "reply": "Based on your 5-acre loamy plain land in Lahore with tube well irrigation...",
  "thread_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

### 4. Continue Conversation (Same Thread)
```http
POST /agent/chat
Authorization: Bearer <your_token>
Content-Type: application/json

{
  "message": "What about water requirements?",
  "thread_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

## 🔧 How the Agent Works

### Conversation Memory
- Each conversation has a unique `thread_id` (UUID)
- If you don't provide `thread_id`, a new conversation starts
- Reuse the same `thread_id` to continue a conversation
- Memory is stored in-memory (MemorySaver) - persists during server runtime

### Context Enrichment
The agent automatically:
1. Fetches your latest form data (location, soil, water, etc.)
2. Enriches with weather context (placeholder - ready for real API)
3. Enriches with market trends (placeholder - ready for real API)
4. Generates personalized crop/market recommendations

### Personalization
- All responses are based on YOUR land data
- Each user only sees their own forms
- Recommendations consider your specific goals (Profit/Climate-safe/Organic/Experiment)

## 🎯 Next Steps for Production

### 1. Real Weather Integration
Replace placeholder in `agent/tools.py`:
```python
def fetch_weather_context(form: Dict[str, Any]) -> Dict[str, Any]:
    # TODO: Call OpenWeather API or similar
    location = form.get("location")
    # api_key = EnvironmentConfig.OPENWEATHER_API_KEY
    # weather_data = requests.get(f"https://api.openweathermap.org/...")
    return {"location": location, "summary": "..."}
```

### 2. Real Market Integration
```python
def fetch_market_context(form: Dict[str, Any]) -> Dict[str, Any]:
    # TODO: Call agricultural market price APIs
    # Could integrate with govt agriculture dept APIs
    return {"demand_trends": [...]}
```

### 3. Persistent Memory
Replace `MemorySaver()` with PostgreSQL checkpoint:
```python
from langgraph.checkpoint.postgres import PostgresSaver

def get_agent():
    # Use DB for persistent conversation memory
    checkpointer = PostgresSaver.from_conn_string(DATABASE_URL)
    graph = build_graph()
    return graph.compile(checkpointer=checkpointer)
```

### 4. Enhanced Prompting
Update `agent/prompt.py` with domain-specific knowledge about:
- Regional crops for Pakistan/your target region
- Seasonal calendars
- Local market dynamics
- Organic vs conventional farming practices

### 5. Rate Limiting
Add rate limiting to prevent API abuse:
```python
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@router.post("/chat")
@limiter.limit("10/minute")
def chat(...):
    ...
```

## 🐛 Troubleshooting

### "column form_responses.user_id does not exist"
✅ **FIXED** - Migration was run successfully

### "Checkpointer requires thread_id"
✅ **FIXED** - Chat endpoint now generates UUID thread_id

### "GEMINI_API_KEY not set"
Check your `.env` file has `GEMINI_API_KEY_ALI=...`

### Agent returns empty response
Check:
1. User has created at least one form
2. Gemini API key is valid
3. Check server logs for LLM errors

## 📊 Current Status

✅ Database migration complete
✅ User-scoped forms working
✅ LangGraph agent configured
✅ Gemini 2.0 Flash integrated
✅ Thread-based conversation memory
✅ Chat endpoint secured with JWT
✅ Test script created

## 🎉 Ready to Use!

Your agent is now fully operational. Just:
1. Ensure server is running
2. Create a user account
3. Fill out the land form
4. Start chatting with the AI agronomist!

The agent will provide personalized crop recommendations, market insights, and farming advice based on your specific land characteristics.

