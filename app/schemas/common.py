from typing import TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ResponseBase[T](BaseModel):
    code: int = 200
    message: str = "Success"
    data: T | None = None
