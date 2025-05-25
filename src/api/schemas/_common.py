from typing import Any, List

from pydantic import BaseModel


class ValidationErrorDetail(BaseModel):
    type: str
    field: str
    message: str
    input: Any


class ValidationErrorResponse(BaseModel):
    details: List[ValidationErrorDetail]
