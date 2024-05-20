from fastapi import APIRouter

from core.auth import api_key as api_key_auth

from . import aircraft, flights, metrics

router = APIRouter(dependencies=[api_key_auth])

router.include_router(aircraft.router, prefix="/aircraft", tags=["Aircraft"])
router.include_router(flights.router, prefix="/flights", tags=["Flights"])
router.include_router(metrics.router, prefix="/metrics", tags=["Metrics"])
