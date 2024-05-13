from typing import Annotated, Any, Dict, Optional
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from typing_extensions import Doc
from fastapi.exceptions import HTTPException
from starlette.status import HTTP_403_FORBIDDEN, HTTP_500_INTERNAL_SERVER_ERROR
from fastapi.encoders import jsonable_encoder


class HTTPUnauthorized(HTTPException):
    EXAMPLE = {
        "description": "Forbidden",
        "content": {
            "application/json": {
                "example": {
                    "detail": "Not authenticated",
                }
            }
        },
    }

    def __init__(
        self,
        status_code: Annotated[
            int,
            Doc(
                """
                    HTTP status code to send to the client.
                    """
            ),
        ] = HTTP_403_FORBIDDEN,
        detail: Annotated[
            Any,
            Doc(
                """
                    Any data to be sent to the client in the `detail` key of the JSON
                    response.
                    """
            ),
        ] = None,
        headers: Annotated[
            Optional[Dict[str, str]],
            Doc(
                """
                    Any headers to send to the client in the response.
                    """
            ),
        ] = None,
    ) -> None:
        if not detail:
            detail = "Not authenticated"
        super().__init__(status_code, detail, headers)


class HTTPInternal(HTTPException):
    EXAMPLE = {
        "description": "Internal",
        "content": {
            "application/json": {
                "example": {
                    "detail": [{"type": "internal", "msg": "Internal server error"}]
                }
            }
        },
    }

    def __init__(
        self,
        status_code: Annotated[
            int,
            Doc(
                """
                    HTTP status code to send to the client.
                    """
            ),
        ] = HTTP_500_INTERNAL_SERVER_ERROR,
        detail: Annotated[
            Any,
            Doc(
                """
                    Any data to be sent to the client in the `detail` key of the JSON
                    response.
                    """
            ),
        ] = None,
        headers: Annotated[
            Optional[Dict[str, str]],
            Doc(
                """
                    Any headers to send to the client in the response.
                    """
            ),
        ] = None,
    ) -> None:
        if not detail:
            detail = [{"type": "internal", "msg": "Internal server error"}]
        super().__init__(status_code, detail, headers)

    async def handler(self, request: Request, exc: Exception):
        return JSONResponse(
            status_code=self.status_code,
            content=jsonable_encoder(self.detail),
        )
