from datetime import date
from typing import Self

from fastapi.exceptions import HTTPException
from pydantic import BaseModel, Field
from pydantic.functional_validators import model_validator
from pydantic.types import NonNegativeInt, PositiveInt

from core.settings import settings


class Aircraft(BaseModel):
    icao24: str = Field(min_length=6, max_length=6, examples=["abc123"])
    flights_recorded: PositiveInt = Field(examples=[5])
    registration: list[str] | None = Field(examples=[["UR-ABC"]])
    model: list[str] | None = Field(examples=[["787-9 Dreamliner"]])
    manufacturer_icao: list[str] | None = Field(examples=[["BOEING"]])
    owner: list[str] | None = Field(examples=[["Dream Lease"]])
    operator: list[str] | None = Field(examples=[["Dream Air", "New Air"]])
    built: list[date] | None = Field(examples=[["2015-03-03"]])


class AircraftPage(BaseModel):
    pages_total: NonNegativeInt = Field(examples=[10])
    results: list[Aircraft]


class BuiltInterval(BaseModel):
    built_gte: date | None = Field(default=None, examples=["2020-01-01"])
    built_lte: date | None = Field(default=None, examples=["2020-01-10"])

    @model_validator(mode="after")
    def gte_lte(self) -> Self:
        if self.built_gte and self.built_lte and self.built_gte > self.built_lte:
            raise HTTPException(
                status_code=422,
                detail=[
                    {
                        "type": "built_gte_built_lte_value",
                        "loc": ["query", "built_gte", "built_lte"],
                        "msg": "built_gte should be less than built_lte",
                        "input": {
                            "built_gte": self.built_gte.strftime(settings.date_format),
                            "built_lte": self.built_lte.strftime(settings.date_format),
                        },
                    }
                ],
            )
        return self
