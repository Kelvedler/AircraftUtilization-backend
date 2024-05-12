from typing import Annotated, List
from fastapi import APIRouter, Query
from core import crud

from core.mongodb import MongodbConn
from core.schemas import Aircraft

router = APIRouter()


@router.get("/", response_model=List[Aircraft])
async def get_aircraft(
    mongodb: MongodbConn,
    page: Annotated[int, Query(ge=1, le=1000)] = 1,
):
    aircraft = await crud.aircraft_get_page(page=page, db=mongodb)
    return aircraft
