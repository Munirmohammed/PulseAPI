from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from ..core.db import get_db
from ..core.security import decode_token
from .. import models, schemas
from ..tasks import schedule_for_endpoint


router = APIRouter(prefix="/endpoints", tags=["endpoints"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return int(payload["sub"])  # user id


@router.post("/", response_model=schemas.EndpointOut, status_code=201)
def create_endpoint(
    payload: schemas.EndpointCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    ep = models.Endpoint(user_id=user_id, **payload.dict())
    db.add(ep)
    db.commit()
    db.refresh(ep)
    schedule_for_endpoint(ep)
    return ep


@router.get("/", response_model=list[schemas.EndpointOut])
def list_endpoints(db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    return db.query(models.Endpoint).filter(models.Endpoint.user_id == user_id).all()


@router.get("/{endpoint_id}", response_model=schemas.EndpointOut)
def get_endpoint(endpoint_id: int, db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    ep = (
        db.query(models.Endpoint)
        .filter(models.Endpoint.id == endpoint_id, models.Endpoint.user_id == user_id)
        .first()
    )
    if not ep:
        raise HTTPException(status_code=404, detail="Not found")
    return ep


@router.patch("/{endpoint_id}", response_model=schemas.EndpointOut)
def update_endpoint(
    endpoint_id: int,
    payload: schemas.EndpointUpdate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    ep = (
        db.query(models.Endpoint)
        .filter(models.Endpoint.id == endpoint_id, models.Endpoint.user_id == user_id)
        .first()
    )
    if not ep:
        raise HTTPException(status_code=404, detail="Not found")
    for k, v in payload.dict(exclude_unset=True).items():
        setattr(ep, k, v)
    db.commit()
    db.refresh(ep)
    schedule_for_endpoint(ep)
    return ep


@router.delete("/{endpoint_id}", status_code=204)
def delete_endpoint(endpoint_id: int, db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    ep = (
        db.query(models.Endpoint)
        .filter(models.Endpoint.id == endpoint_id, models.Endpoint.user_id == user_id)
        .first()
    )
    if not ep:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(ep)
    db.commit()
    # remove schedule if exists
    try:
        from ..celery_app import celery

        celery.conf.beat_schedule.pop(f"check_{endpoint_id}", None)
    except Exception:
        pass
    return None


