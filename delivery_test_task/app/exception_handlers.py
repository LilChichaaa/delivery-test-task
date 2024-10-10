from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from loguru import logger
import traceback

from .main import app

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Обработчик исключений HTTPException.
    Логирует запрос и все детали исключения.
    """
    logger.error(
        f"HTTP Error occurred!\n"
        f"Request URL: {request.url}\n"
        f"Method: {request.method}\n"
        f"Status Code: {exc.status_code}\n"
        f"Detail: {exc.detail}\n"
        f"Headers: {request.headers}"
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "HTTP Error", "message": exc.detail, "endpoint": str(request.url)}
    )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """
    Обработчик исключений ValueError.
    Логирует запрос, текст исключения и полный traceback.
    """
    logger.error(
        f"Value Error occurred!\n"
        f"Request URL: {request.url}\n"
        f"Method: {request.method}\n"
        f"Exception: {exc}\n"
        f"Headers: {request.headers}\n"
        f"Traceback: {traceback.format_exc()}"
    )

    return JSONResponse(
        status_code=400,
        content={"error": "Value Error", "message": str(exc), "endpoint": str(request.url)}
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Обработчик исключений RequestValidationError.
    Логирует запрос, детали ошибки валидации, проблемные поля и полный traceback.
    """
    errors = exc.errors()
    formatted_errors = []

    for error in errors:
        formatted_errors.append({
            "error": "Validation Error",
            "message": error['msg'],
            "field": ".".join([str(loc) for loc in error['loc']])
        })

    logger.error(
        f"Validation Error occurred!\n"
        f"Request URL: {request.url}\n"
        f"Method: {request.method}\n"
        f"Headers: {request.headers}\n"
        f"Errors: {formatted_errors}\n"
        f"Traceback: {traceback.format_exc()}"
    )

    return JSONResponse(
        status_code=422,
        content={"error": formatted_errors, "message": "Unprocessable Entity", "endpoint": str(request.url)}
    )


@app.exception_handler(Exception)
async def internal_server_error_handler(request: Request, exc: Exception):
    """
    Обработчик общих исключений.
    Логирует запрос, полную информацию об ошибке, стек вызовов и детали запроса.
    """
    logger.exception(
        f"Internal Server Error occurred!\n"
        f"Request URL: {request.url}\n"
        f"Method: {request.method}\n"
        f"Headers: {request.headers}\n"
        f"Exception Type: {type(exc).__name__}\n"
        f"Traceback: {traceback.format_exc()}"
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "Something went wrong on the server",
            "endpoint": str(request.url)
        }
    )
