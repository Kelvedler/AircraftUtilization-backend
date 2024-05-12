from pydantic import BaseModel, Field
from pydantic.types import NonNegativeInt


class Aircraft(BaseModel):
    icao24: str = Field(min_length=6, max_length=6, examples=["abc123"])
    flights_recorded: NonNegativeInt = Field(examples=[5])
