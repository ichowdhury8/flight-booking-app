"""GET /api/airports — populates both search dropdowns."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Airport
from ..schemas import AirportOut

router = APIRouter(prefix="/api/airports", tags=["airports"])


@router.get("", response_model=list[AirportOut])
def list_airports(db: Session = Depends(get_db)) -> list[Airport]:
    return db.query(Airport).order_by(Airport.city).all()
