from fastapi import HTTPException
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR
import logging

logger = logging.getLogger(__name__)

class APIException(HTTPException):
    def __init__(self, status_code: int, detail: str, error_code: str = None):
        super().__init__(status_code=status_code, detail=detail)
        self.error_code = error_code

class ItemNotFoundError(APIException):
    def __init__(self, item_id: str):
        super().__init__(
            status_code=404,
            detail=f"Item with id '{item_id}' not found",
            error_code="ITEM_NOT_FOUND"
        )

class ValidationError(APIException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=400,
            detail=detail,
            error_code="VALIDATION_ERROR"
        )

async def api_exception_handler(request: Request, exc: APIException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.error_code or "API_ERROR",
                "message": exc.detail,
                "status_code": exc.status_code
            }
        }
    )

async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}")
    
    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
                "status_code": HTTP_500_INTERNAL_SERVER_ERROR
            }
        }
    )