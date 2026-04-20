from flask import Blueprint, jsonify
from flask_limiter import limiter
from pydantic import BaseModel

from app import db

data_bp = Blueprint("data", __name__)


class AthleteResponse(BaseModel):
    id: str
    first_name: str
    last_name: str
    date_of_birth: str | None
    gender: str | None
    country_code: str | None

    class Config:
        from_attributes = True


class EventResponse(BaseModel):
    id: str
    name: str
    event_type: str
    category: str | None
    unit: str | None

    class Config:
        from_attributes = True


class PerformanceResponse(BaseModel):
    id: str
    athlete_id: str
    event_id: str
    mark_value: float
    competition_name: str | None
    competition_date: str | None
    is_personal_best: bool

    class Config:
        from_attributes = True


@data_bp.route("/athletes", methods=["GET"])
@limiter.limit("100 per hour")
def get_athletes():
    """Get all athletes."""
    from app import db

    athletes = db.execute(
        db.text(
            """
        SELECT id, first_name, last_name, date_of_birth, gender, country_code
        FROM athletes
        ORDER BY last_name, first_name
        """
        )
    ).fetchall()

    result = [
        {
            "id": str(row[0]),
            "first_name": row[1],
            "last_name": row[2],
            "date_of_birth": row[3].isoformat() if row[3] else None,
            "gender": row[4],
            "country_code": row[5],
        }
        for row in athletes
    ]

    return jsonify({"data": result, "count": len(result)})


@data_bp.route("/events", methods=["GET"])
@limiter.limit("100 per hour")
def get_events():
    """Get all events."""
    from app import db

    events = db.execute(
        db.text(
            """
        SELECT id, name, event_type, category, unit
        FROM events
        ORDER BY event_type, name
        """
        )
    ).fetchall()

    result = [
        {
            "id": str(row[0]),
            "name": row[1],
            "event_type": row[2],
            "category": row[3],
            "unit": row[4],
        }
        for row in events
    ]

    return jsonify({"data": result, "count": len(result)})


@data_bp.route("/performances", methods=["GET"])
@limiter.limit("100 per hour")
def get_performances():
    """Get performance metrics."""
    from app import db

    performances = db.execute(
        db.text(
            """
        SELECT 
            p.id,
            p.athlete_id,
            a.first_name,
            a.last_name,
            p.event_id,
            e.name as event_name,
            p.mark_value,
            p.competition_name,
            p.competition_date,
            p.is_personal_best
        FROM performances p
        JOIN athletes a ON p.athlete_id = a.id
        JOIN events e ON p.event_id = e.id
        ORDER BY p.competition_date DESC
        LIMIT 100
        """
        )
    ).fetchall()

    result = [
        {
            "id": str(row[0]),
            "athlete_id": str(row[1]),
            "athlete_name": f"{row[2]} {row[3]}",
            "event_id": str(row[4]),
            "event_name": row[5],
            "mark_value": float(row[6]),
            "competition_name": row[7],
            "competition_date": row[8].isoformat() if row[8] else None,
            "is_personal_best": row[9],
        }
        for row in performances
    ]

    return jsonify({"data": result, "count": len(result)})


@data_bp.route("/competitions", methods=["GET"])
@limiter.limit("100 per hour")
def get_competitions():
    """Get all competitions."""
    from app import db

    competitions = db.execute(
        db.text(
            """
        SELECT id, name, start_date, end_date, location, country_code, status
        FROM competitions
        ORDER BY start_date DESC
        """
        )
    ).fetchall()

    result = [
        {
            "id": str(row[0]),
            "name": row[1],
            "start_date": row[2].isoformat() if row[2] else None,
            "end_date": row[3].isoformat() if row[3] else None,
            "location": row[4],
            "country_code": row[5],
            "status": row[6],
        }
        for row in competitions
    ]

    return jsonify({"data": result, "count": len(result)})


@data_bp.route("/summary", methods=["GET"])
@limiter.limit("50 per hour")
def get_summary():
    """Get dashboard summary statistics."""
    from app import db

    athlete_count = db.execute(
        db.text("SELECT COUNT(*) FROM athletes")
    ).scalar() or 0

    event_count = db.execute(
        db.text("SELECT COUNT(*) FROM events")
    ).scalar() or 0

    performance_count = db.execute(
        db.text("SELECT COUNT(*) FROM performances")
    ).scalar() or 0

    competition_count = db.execute(
        db.text("SELECT COUNT(*) FROM competitions")
    ).scalar() or 0

    return jsonify(
        {
            "data": {
                "athletes": int(athlete_count),
                "events": int(event_count),
                "performances": int(performance_count),
                "competitions": int(competition_count),
            }
        }
    )
