from datetime import date
from typing import Self

from fastapi import HTTPException
from pydantic import BaseModel, Field
from pydantic.functional_validators import model_validator
from pydantic.types import PositiveInt

from core.settings import settings
from core.types_ import ObjectId


class Flights(BaseModel):
    id: ObjectId = Field(examples=["662ac147afe88a374739f3e7"])
    icao24: str = Field(min_length=6, max_length=6, examples=["abc123"])
    duration_minutes: PositiveInt = Field(examples=[50])
    landed_at: PositiveInt = Field(examples=[946677600])


class LandedInterval(BaseModel):
    landed_gte: date | None = Field(default=None, examples=["2020-01-01"])
    landed_lte: date | None = Field(default=None, examples=["2020-01-10"])

    @model_validator(mode="after")
    def gte_lte(self) -> Self:
        if self.landed_gte and self.landed_lte and self.landed_gte > self.landed_lte:
            raise HTTPException(
                status_code=422,
                detail=[
                    {
                        "type": "landed_gte_landed_lte_value",
                        "loc": ["query", "landed_gte", "landed_lte"],
                        "msg": "landed_gte should be less than landed_lte",
                        "input": {
                            "landed_gte": self.landed_gte.strftime(
                                settings.date_format
                            ),
                            "landed_lte": self.landed_lte.strftime(
                                settings.date_format
                            ),
                        },
                    }
                ],
            )
        return self


class DurationInterval(BaseModel):
    duration_gte: PositiveInt | None = Field(default=None, lt=2400, examples=[10])
    duration_lte: PositiveInt | None = Field(default=None, lt=2400, examples=[10])

    @model_validator(mode="after")
    def gte_lte(self) -> Self:
        if (
            self.duration_gte
            and self.duration_lte
            and self.duration_gte > self.duration_lte
        ):
            raise HTTPException(
                status_code=422,
                detail=[
                    {
                        "type": "duration_gte_duration_lte_value",
                        "loc": ["query", "duration_gte", "duration_lte"],
                        "msg": "duration_gte should be less than duration_lte",
                        "input": {
                            "duration_gte": self.duration_gte,
                            "duration_lte": self.duration_lte,
                        },
                    }
                ],
            )
        return self
