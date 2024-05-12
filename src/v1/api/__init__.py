from fastapi import APIRouter

from core.auth import api_key as api_key_auth

from . import aircraft, flights

router = APIRouter(dependencies=[api_key_auth])

router.include_router(aircraft.router, prefix="/aircraft", tags=["Aircraft"])
router.include_router(flights.router, prefix="/flights", tags=["Flights"])
