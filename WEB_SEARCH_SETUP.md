# Web Search Integration - Setup Guide

## ✅ What's Been Added

Your ReGenAI agent now has **intelligent web search** capabilities using Tavily API!

### Features:
- 🔍 **Automatic Search Detection**: Agent decides when to search based on keywords
- 🌐 **Real-time Information**: Gets current prices, weather, news, research
- 📊 **Visual Display**: Search results shown in beautiful cards in the frontend
- 🎯 **Smart Integration**: Search results are used to provide up-to-date advice

---

## 🚀 Installation Steps

### Step 1: Install Tavily Python Package

```bash
cd c:\Users\Ali Hassan\Desktop\regenai\releafai-backend
pip install tavily-python
```

### Step 2: Get Your Tavily API Key

1. Go to: https://tavily.com/
2. Sign up for a free account
3. Get your API key from the dashboard
4. Free tier includes: **1,000 searches/month**

### Step 3: Add API Key to .env File

Your `.env` file already has the placeholder. Just add your key:

```env
# In c:\Users\Ali Hassan\Desktop\regenai\releafai-backend\.env
TAVILY_API_KEY=tvly-your-actual-api-key-here
```

### Step 4: Restart Backend Server

```bash
# Stop the current server (Ctrl+C)
# Start it again
python -m uvicorn main:app --reload
```

---

## 🎯 How It Works

### When Does It Search?

The agent automatically searches when it detects these keywords in user questions:
- **Time-related**: current, latest, recent, today, now, 2024, 2025
- **Market-related**: price, market price, cost
- **Information**: news, update, research, study
- **Weather**: weather forecast, climate data

### Example Triggers:

✅ **"What is the current price of wheat in Pakistan?"**
- Triggers search: "current price wheat Pakistan agriculture farming"

✅ **"Latest research on drought-resistant crops"**
- Triggers search: "latest research drought-resistant crops Pakistan agriculture farming"

✅ **"Tell me today's weather forecast for Faisalabad"**
- Triggers search: "today weather forecast Faisalabad Pakistan agriculture farming"

❌ **"How do I plant wheat?"**
- No search needed (general knowledge)

---

## 📊 What Users See

### 1. Search Indicator
When search is triggered, users see a beautiful purple card:
```
🔍 Searching the web: "current wheat prices Pakistan agriculture farming"
```

### 2. Search Results
3 relevant results displayed with:
- **Title**: Article/page title
- **Content**: Brief excerpt (300 chars)
- **URL**: Clickable link to source

### 3. AI Response
Agent uses search results to provide current, accurate advice

---

## 🔧 Technical Flow

```
User asks: "What's the current wheat price?"
    ↓
[Search Node] - Detects "current" + "price" keywords
    ↓
[Tavily API] - Searches: "current wheat price Pakistan agriculture"
    ↓
[Returns] - 3 relevant results + AI-generated answer
    ↓
[Enrich Node] - Adds farm context
    ↓
[Reply Node] - LLM uses search results + farm data
    ↓
[Frontend] - Shows search results + AI response
```

---

## 📝 Example Conversation

**User**: "What is the current market price of wheat in Punjab?"

**Search Results Displayed**:
```
🔍 Searching the web: "current market price wheat Punjab Pakistan agriculture farming"

1. Punjab Wheat Prices Rise to PKR 3,500 per Maund
   Recent market data shows wheat prices in Punjab have increased...
   Source: agriculture.gov.pk

2. Wheat Market Update - January 2025
   Current wholesale rates for wheat in major Punjab markets...
   Source: pakissan.com

3. Agricultural Commodity Prices - Pakistan
   Latest pricing information for major crops including wheat...
   Source: dawn.com
```

**Agent Response**:
"Based on current market data, wheat prices in Punjab are around PKR 3,500 per maund. For your 5-acre farm in Faisalabad with loamy soil, this is good news if you're planning to harvest soon. Here's what you should consider:

1. **Timing**: Current prices are favorable...
2. **Storage**: If you can store safely...
3. **Quality**: Ensure moisture content is below 12%..."

---

## 🎨 Frontend Display

The search results appear as a gradient purple card with:
- Smooth slide-in animation
- Glassmorphism effect
- Hover effects on result cards
- Clickable URLs to sources

---

## ⚙️ Configuration

### Adjust Search Sensitivity

Edit `c:\Users\Ali Hassan\Desktop\regenai\releafai-backend\agent\main_agent.py`:

```python
# Line ~50: Add/remove keywords
search_keywords = [
    "current", "latest", "recent",  # Add more keywords here
    "price", "market price",
    # ... etc
]
```

### Change Number of Results

```python
# Line ~62: Change max_results
search_data = web_search(search_query, max_results=5)  # Default is 3
```

### Customize Search Query

```python
# Line ~61: Modify search query format
search_query = f"{user_message} Pakistan agriculture"  # Customize this
```

---

## 🐛 Troubleshooting

### "Web search not configured" Error
- Check if `TAVILY_API_KEY` is in `.env` file
- Restart the backend server

### "Tavily package not installed" Error
```bash
pip install tavily-python
```

### Search Not Triggering
- Check if your question contains trigger keywords
- Add custom keywords to `search_keywords` list

### API Rate Limit
- Free tier: 1,000 searches/month
- Upgrade at tavily.com for more

---

## 📊 Monitoring

Check backend logs to see when searches are performed:

```
INFO:agent.main_agent:Web search needed for query: current wheat price
INFO:agent.tools:Performing web search for: current wheat price Pakistan agriculture
INFO:agent.tools:Web search completed: 3 results found
INFO:agent.main_agent:Added web search results to prompt
```

---

## ✨ Benefits

1. **Up-to-date Information**: Real-time prices, weather, news
2. **Credible Sources**: Links to actual sources
3. **Better Advice**: Agent uses current data
4. **User Trust**: Transparent about where information comes from
5. **Automatic**: No manual search needed

---

## 🚀 Next Steps

1. Install Tavily: `pip install tavily-python`
2. Get API key from tavily.com
3. Add to `.env` file
4. Restart backend
5. Test with: "What's the current wheat price?"

Enjoy your intelligent web-searching farming assistant! 🌾
