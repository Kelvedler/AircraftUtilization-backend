from typing import Literal
from pydantic import EmailStr, Field, AnyUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Contact(BaseSettings):
    email: EmailStr = Field(default="developer@example.com", alias="CONTACT_EMAIL")


class App(BaseSettings):
    title: Literal["Aircraft Utilization"] = "Aircraft Utilization"
    version: Literal["0.1.0"] = "0.1.0"
    description: Literal[
        """
    Aircraft flights data based on ADS-B signal.

    Bringing up OpenSky: A large-scale ADS-B sensor network for research
    Matthias Schäfer, Martin Strohmeier, Vincent Lenders, Ivan Martinovic, Matthias Wilhelm
    ACM/IEEE International Conference on Information Processing in Sensor Networks, April 2014
    """
    ] = """
    Aircraft flights data based on ADS-B signal.

    Bringing up OpenSky: A large-scale ADS-B sensor network for research
    Matthias Schäfer, Martin Strohmeier, Vincent Lenders, Ivan Martinovic, Matthias Wilhelm
    ACM/IEEE International Conference on Information Processing in Sensor Networks, April 2014
    """
    contact: Contact = Contact()
    host: str = Field(default="127.0.0.1", alias="HOST")
    port: int = Field(default=8000, alias="PORT")


class Logging(BaseSettings):
    default: str = Field(default="INFO")
    system: str = Field(default="WARNING")


class MongoDb(BaseSettings):
    url: AnyUrl = Field(default="mongodb://local_user:local_pass@127.0.0.1:27017")
    db: str = Field(default="aircraft-utilization")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_nested_delimiter="_")

    app: App = App()
    logging: Logging = Logging()
    mongodb: MongoDb = MongoDb()
    postgres_url: AnyUrl = Field(
        default="postgresql://local_user:local_pass@127.0.0.1:5433/local_db"
    )
    items_per_page: Literal[50] = 50
    date_format: Literal["%Y-%m-%d"] = "%Y-%m-%d"


settings = Settings()

log_config = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "default": {"format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"}
    },
    "handlers": {
        "console": {
            "level": settings.logging.default,
            "class": "logging.StreamHandler",
            "formatter": "default",
        }
    },
    "loggers": {
        "v1": {
            "handlers": ["console"],
            "level": settings.logging.default,
            "propagate": False,
        },
        "core": {
            "handlers": ["console"],
            "level": settings.logging.default,
            "propagate": False,
        },
        "uvicorn.access": {
            "handlers": ["console"],
            "level": settings.logging.default,
            "propagate": False,
        },
        "uvicorn.error": {
            "handlers": ["console"],
            "level": settings.logging.default,
            "propagate": False,
        },
        "sqlalchemy.engine": {
            "handlers": ["console"],
            "level": settings.logging.system,
            "propagate": False,
        },
        "pymongo": {
            "handlers": ["console"],
            "level": settings.logging.system,
            "propagate": False,
        },
    },
}
