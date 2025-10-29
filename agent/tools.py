from typing import Any, Dict, Optional, List
from sqlalchemy.orm import Session
import os
import logging

logger = logging.getLogger(__name__)


def get_user_latest_form(db: Session, user_id: int) -> Dict[str, Any]:
    from models.tables_models import FormResponse

    form = (
        db.query(FormResponse)
        .filter(FormResponse.user_id == user_id)
        .order_by(FormResponse.id.desc())
        .first()
    )
    if not form:
        return {}
    # Convert SQLAlchemy object to dict
    return {
        "id": form.id,
        "user_id": form.user_id,
        "location": form.location,
        "area_type": form.area_type,
        "soil_type": form.soil_type,
        "water_source": form.water_source,
        "irrigation": form.irrigation,
        "temperature": form.temperature,
        "rainfall": form.rainfall,
        "sunlight": form.sunlight,
        "land_size": form.land_size,
        "goal": form.goal,
        "crop_duration": form.crop_duration,
        "specific_crop": form.specific_crop,
        "fertilizers_preference": form.fertilizers_preference,
        "last_planted_at": form.last_planted_at,
    }


def fetch_weather_context(form: Dict[str, Any]) -> Dict[str, Any]:
    # Placeholder for real weather integration; returns a minimal stub
    return {
        "location": form.get("location"),
        "summary": "Seasonal outlook suggests moderate temperatures and medium rainfall next 4-6 weeks",
    }


def fetch_market_context(form: Dict[str, Any]) -> Dict[str, Any]:
    # Placeholder for real market integration; returns a minimal stub
    goal = form.get("goal", "Profit")
    return {
        "goal": goal,
        "demand_trends": [
            "Wheat demand steady in regional mills",
            "Pulses prices rising in nearby wholesale markets",
        ],
    }


def web_search(query: str, max_results: int = 3) -> Dict[str, Any]:
    """
    Search the web using Tavily API for real-time information
    
    Args:
        query: The search query
        max_results: Maximum number of results to return (default: 3)
    
    Returns:
        Dict with search results and metadata
    """
    try:
        from tavily import TavilyClient
        from config.env_config import EnvironmentConfig
        
        tavily_api_key = os.getenv("TAVILY_API_KEY")
        
        if not tavily_api_key:
            logger.warning("TAVILY_API_KEY not found in environment")
            return {
                "success": False,
                "error": "Web search not configured",
                "results": []
            }
        
        logger.info(f"Performing web search for: {query}")
        
        client = TavilyClient(api_key=tavily_api_key)
        
        # Perform search
        response = client.search(
            query=query,
            max_results=max_results,
            search_depth="basic",
            include_answer=True,
            include_raw_content=False
        )
        
        # Extract relevant information
        results = []
        for result in response.get('results', []):
            results.append({
                "title": result.get('title', ''),
                "url": result.get('url', ''),
                "content": result.get('content', '')[:300] + "...",  # Limit content length
                "score": result.get('score', 0)
            })
        
        logger.info(f"Web search completed: {len(results)} results found")
        
        return {
            "success": True,
            "query": query,
            "answer": response.get('answer', ''),  # Tavily's AI-generated answer
            "results": results,
            "images": response.get('images', [])[:2] if response.get('images') else []
        }
        
    except ImportError:
        logger.error("Tavily package not installed. Install with: pip install tavily-python")
        return {
            "success": False,
            "error": "Tavily package not installed",
            "results": []
        }
    except Exception as e:
        logger.error(f"Web search error: {e}")
        return {
            "success": False,
            "error": str(e),
            "results": []
        }
