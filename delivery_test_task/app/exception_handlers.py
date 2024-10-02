from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

from fastapi.exceptions import RequestValidationError

from .main import app

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "HTTP Error", "message": exc.detail, "endpoint": str(request.url)}
    )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=400,
        content={"error": "Value Error", "message": str(exc), "endpoint": str(request.url)}
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    formatted_errors = []

    for error in errors:
        formatted_errors.append({
            "error": "Validation Error",
            "message": error['msg'],
            "field": ".".join([str(loc) for loc in error['loc']])
        })

    return JSONResponse(
        status_code=422,
        content={"error": formatted_errors, "message": "Unprocessable Entity", "endpoint": str(request.url)}
    )


@app.exception_handler(Exception)
async def internal_server_error_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "Something went wrong on the server",
            "endpoint": str(request.url)
        }
    )

