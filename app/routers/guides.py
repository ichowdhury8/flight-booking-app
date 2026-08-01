"""GET /api/guides/{iata_code} — standalone Arrival Guide lookup.

The happy path doesn't need this: POST /api/bookings already embeds the guide in
its response. It exists so the custom feature stays independently testable.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Airport, ArrivalGuide
from ..schemas import GuideOut, to_guide_out

router = APIRouter(prefix="/api/guides", tags=["guides"])


def load_guide(db: Session, iata_code: str) -> ArrivalGuide | None:
    return (
        db.query(ArrivalGuide)
        .join(Airport, ArrivalGuide.airport_id == Airport.id)
        .filter(Airport.iata_code == iata_code.upper())
        .first()
    )


@router.get("/{iata_code}", response_model=GuideOut)
def get_guide(iata_code: str, db: Session = Depends(get_db)) -> GuideOut:
    guide = load_guide(db, iata_code)
    if guide is None:
        raise HTTPException(
            status_code=404, detail="No arrival guide for that airport."
        )
    return to_guide_out(guide)
