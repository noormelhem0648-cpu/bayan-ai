"""Users can contribute Gemini API keys to widen the free-tier pool."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import ContributedKey, User
from app.schemas.system import ContributeKeyRequest

router = APIRouter()


@router.post("/contribute", status_code=201)
def contribute_key(
    data: ContributeKeyRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    key = ContributedKey(
        user_id=user.id, key_value=data.key_value, label=data.label, is_active=True
    )
    db.add(key)
    db.commit()
    return {"detail": "Thank you for contributing a key"}
