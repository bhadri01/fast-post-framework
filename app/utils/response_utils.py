from fastapi.responses import JSONResponse

def send_json_response(status_code: int, message: str, status: bool = False, data=None, error=None):
    """
    A utility function to format JSON responses.
    """
    return JSONResponse(
        status_code=status_code,
        content={
            "message": message,
            "status": status,
            "data": data,
            "error": error,
        },
    )