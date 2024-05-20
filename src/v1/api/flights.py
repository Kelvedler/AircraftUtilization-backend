from typing import Annotated
from fastapi import APIRouter, Query
from fastapi.param_functions import Depends

from core import crud, http_errors, schemas
from core.mongodb import MongodbConn

router = APIRouter()


@router.get(
    "/",
    response_model=schemas.FlightsPage,
    responses={
        403: http_errors.HTTPUnauthorized.EXAMPLE,
        500: http_errors.HTTPInternal.EXAMPLE,
    },
)
async def get_flights(
    mongodb: MongodbConn,
    page: Annotated[int, Query(ge=1, le=1_000_000)] = 1,
    icao24: Annotated[str | None, Query(min_length=6, max_length=6)] = None,
    model: Annotated[str | None, Query(min_length=3, max_length=50)] = None,
    manufacturer: Annotated[str | None, Query(min_length=3, max_length=50)] = None,
    owner: Annotated[str | None, Query(min_length=3, max_length=50)] = None,
    operator: Annotated[str | None, Query(min_length=3, max_length=50)] = None,
    landed_interval: schemas.LandedInterval = Depends(),
    duration_interval: schemas.DurationInterval = Depends(),
):
    flights = await crud.flights_get_page(
        page=page,
        icao24=icao24,
        model=model,
        manufacturer=manufacturer,
        owner=owner,
        operator=operator,
        landed_interval=landed_interval,
        duration_interval=duration_interval,
        db=mongodb,
    )
    return flights
