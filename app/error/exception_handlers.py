from fastapi import Request, FastAPI, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.exc import DBAPIError
from fastapi.exceptions import RequestValidationError
import json


def error_exception_handlers(app: FastAPI):
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request, exc: RequestValidationError):
        """
        Custom handler for validation errors.
        """
        # Extract validation errors
        errors = []
        for error in exc.errors():
            errors.append({
                # Join field path
                "field": ".".join(map(str, error["loc"][1:])),
                "message": error["msg"],
                "input": error["input"],
            })

        # Format response with errors in the "error" key
        return JSONResponse(
            status_code=422,
            content={
                "message": errors,
                "status": False,
            },
        )


def http_exception_handlers(app: FastAPI):
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        detail = exc.detail if isinstance(
            exc.detail, str) else json.dumps(exc.detail)
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "message": detail,  # Use the detail directly as the message
                "status": False
            },
        )
