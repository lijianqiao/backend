"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: exceptions.py
@DateTime: 2025-12-30 11:56:00
@Docs: 自定义业务异常 (Custom Domain Exceptions).
"""

from typing import Any


class CustomException(Exception):
    """
    业务逻辑基础异常类。
    """

    def __init__(self, code: int, message: str, details: Any = None):
        self.code = code
        self.message = message
        self.details = details


class NotFoundException(CustomException):
    """
    资源不存在异常 (404).
    """

    def __init__(self, message: str = "Not Found"):
        super().__init__(code=404, message=message)


class ForbiddenException(CustomException):
    """
    禁止访问异常 (403).
    """

    def __init__(self, message: str = "Forbidden"):
        super().__init__(code=403, message=message)


class UnauthorizedException(CustomException):
    """
    未授权异常 (401).
    """

    def __init__(self, message: str = "Unauthorized"):
        super().__init__(code=401, message=message)


class BadRequestException(CustomException):
    """
    无效请求异常 (400).
    """

    def __init__(self, message: str = "Bad Request"):
        super().__init__(code=400, message=message)


class ValidationError(CustomException):
    """
    数据验证错误 (422).
    """

    def __init__(self, message: str = "Validation Error", details: Any = None):
        super().__init__(code=422, message=message, details=details)
