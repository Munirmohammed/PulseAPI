from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from ..core.db import get_db
from ..core.security import decode_token
from .. import models, schemas


router = APIRouter(prefix="/logs", tags=["logs"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_user_id(token: str = Depends(oauth2_scheme)) -> int:
    return int(decode_token(token)["sub"])  # type: ignore


@router.get("/endpoint/{endpoint_id}", response_model=list[schemas.HealthLogOut])
def endpoint_logs(endpoint_id: int, db: Session = Depends(get_db), _: int = Depends(get_user_id)):
    logs = (
        db.query(models.HealthLog)
        .filter(models.HealthLog.endpoint_id == endpoint_id)
        .order_by(models.HealthLog.created_at.desc())
        .limit(500)
        .all()
    )
    return logs


