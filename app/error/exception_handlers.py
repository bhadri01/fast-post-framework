from fastapi import Request, FastAPI, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.exc import DBAPIError
from fastapi.exceptions import RequestValidationError
from app.utils.response_utils import send_json_response


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
                "field": ".".join(map(str, error["loc"][1:])),  # Join field path
                "message": error["msg"]
            })

        # Format response with errors in the "error" key
        return send_json_response(
            status_code=422,
            message="Validation failed.",
            status=False,
            data=None,  # No data in case of an error
            error=errors
        )
def unexpected_exception_handlers(app: FastAPI):
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        detail = exc.detail if isinstance(exc.detail, str) else json.dumps(exc.detail)
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "message": "An error occurred",
                "status": False,
                "data": None,
                "error": detail,
            },
        )
