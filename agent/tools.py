from typing import Any, Dict, Optional
from sqlalchemy.orm import Session


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

