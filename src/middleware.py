from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp

from fastapi.responses import JSONResponse
from fastapi import Request, Response

from typing import Any, Callable, Coroutine
from enum import Enum

class UMiddleware(BaseHTTPMiddleware):
    class DispatchErrorClass(Enum):
        NO_HEADER = -1
        INVALID_HEADER = -2
        AUTH = -3

    def __init__(self, app: ASGIApp, use_firebase_admin_auth: bool = False, firebase_app: Any = None) -> None:
        super().__init__(app)
        self._use_firebase_admin_auth: bool = use_firebase_admin_auth
        self._firebase_app: Any = firebase_app

        self._verify_id_token: Callable | None = None
        if self._use_firebase_admin_auth:
            from firebase_admin.auth import verify_id_token
            self._verify_id_token: Callable = verify_id_token

    def create_error_response(self, class_: DispatchErrorClass, message: str) -> JSONResponse:
        code: int
        if class_ == UMiddleware.DispatchErrorClass.NO_HEADER:
            code = 401
        elif class_ == UMiddleware.DispatchErrorClass.INVALID_HEADER:
            code = 401
        elif class_ == UMiddleware.DispatchErrorClass.AUTH:
            code = 403
        else:
            code = 418

        return JSONResponse({"error":{"code":code, "class":class_.name, "message":message}}, code, media_type="application/json")

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Coroutine[Any, Any, Response]:
        if self._use_firebase_admin_auth:
            print(f"Authenticating...")

            header: str | None = request.headers.get("Authorization", None)
            if header:
                split_header: list[str] = header.split(" ")

                if len(split_header) != 2:
                    print("Authentication unsuccessful: Header is invalid.")
                    return self.create_error_response(UMiddleware.DispatchErrorClass.INVALID_HEADER, "Authorization header is invalid.")
                token: str = split_header[1]

                try:
                    decoded_token: Any = self._verify_id_token(token, self._firebase_app, True)
                except Exception as error:
                    print(f"Authentication unsuccessful: {error}")
                    return self.create_error_response(UMiddleware.DispatchErrorClass.AUTH, str(error))
            else:
                print("Authentication unsuccessful: Header is None.")
                return self.create_error_response(UMiddleware.DispatchErrorClass.INVALID_HEADER, "Authorization header is None.")
        
            print("Authentication successful!")
        else:
            print("Authentication is disabled.")

        return await call_next(request)