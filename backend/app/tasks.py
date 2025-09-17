import time
import requests
from celery.schedules import schedule
from sqlalchemy.orm import Session
from .celery_app import celery
from .core.db import SessionLocal
from . import models


@celery.task
def run_check(endpoint_id: int) -> None:
    db: Session = SessionLocal()
    try:
        ep = db.query(models.Endpoint).get(endpoint_id)
        if not ep or not ep.is_active:
            return
        start = time.perf_counter()
        try:
            resp = requests.request(ep.method, ep.url, timeout=15)
            latency_ms = (time.perf_counter() - start) * 1000
            success = resp.status_code == ep.expected_status
            log = models.HealthLog(
                endpoint_id=ep.id,
                status_code=resp.status_code,
                success=success,
                latency_ms=latency_ms,
            )
        except Exception as exc:  # network errors
            latency_ms = (time.perf_counter() - start) * 1000
            log = models.HealthLog(
                endpoint_id=ep.id,
                status_code=0,
                success=False,
                latency_ms=latency_ms,
                error_message=str(exc),
            )
        db.add(log)
        db.commit()
    finally:
        db.close()


def schedule_for_endpoint(endpoint: models.Endpoint) -> None:
    # add/replace periodic task in beat schedule
    celery.conf.beat_schedule[f"check_{endpoint.id}"] = {
        "task": "app.tasks.run_check",
        "schedule": schedule(run_every=endpoint.interval_seconds),
        "args": (endpoint.id,),
    }


