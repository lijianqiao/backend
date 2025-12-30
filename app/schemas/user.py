"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: user.py
@DateTime: 2025-12-30 14:45:00
@Docs: 用户 User 相关 Schema 定义。
"""

import re
from uuid import UUID

import phonenumbers
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.core.config import settings


def validate_password_strength(password: str) -> str:
    """
    验证密码强度。
    如果开启密码复杂度验证，需要：大小写字母 + 数字 + 特殊字符 且 >= 8 位
    否则仅要求 >= 6 位
    """
    if settings.PASSWORD_COMPLEXITY_ENABLED:
        if len(password) < 8:
            raise ValueError("密码长度至少为 8 位")
        if not re.search(r"[a-z]", password):
            raise ValueError("密码必须包含小写字母")
        if not re.search(r"[A-Z]", password):
            raise ValueError("密码必须包含大写字母")
        if not re.search(r"\d", password):
            raise ValueError("密码必须包含数字")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            raise ValueError('密码必须包含特殊字符 (!@#$%^&*(),.?":{}|<>)')
    else:
        if len(password) < 6:
            raise ValueError("密码长度至少为 6 位")
    return password


class UserBase(BaseModel):
    username: str = Field(..., description="用户名")
    email: EmailStr | None = Field(None, description="邮箱")
    phone: str = Field(..., description="手机号")
    nickname: str | None = Field(None, description="昵称")
    gender: str | None = Field(None, description="性别")
    is_active: bool = Field(True, description="是否激活")
    is_superuser: bool = Field(False, description="是否为超级管理员")

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """
        验证手机号格式 (支持国际化，默认推断或需加区号，这里假设中国大陆 +86 或用户输入带区号)
        """
        try:
            parsed_number = phonenumbers.parse(v, "CN")
            if not phonenumbers.is_valid_number(parsed_number):
                raise ValueError("无效的手机号码")
            return phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
        except phonenumbers.NumberParseException as e:
            raise ValueError("手机号码格式错误") from e


class UserCreate(UserBase):
    password: str = Field(..., description="密码")

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        return validate_password_strength(v)


class UserUpdate(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    nickname: str | None = None
    gender: str | None = None
    password: str | None = None
    is_active: bool | None = None
    is_superuser: bool | None = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str | None) -> str | None:
        if v is None:
            return None
        try:
            parsed_number = phonenumbers.parse(v, "CN")
            if not phonenumbers.is_valid_number(parsed_number):
                raise ValueError("无效的手机号码")
            return phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
        except phonenumbers.NumberParseException as e:
            raise ValueError("手机号码格式错误") from e

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str | None) -> str | None:
        if v is None:
            return None
        return validate_password_strength(v)


class UserResponse(UserBase):
    id: UUID

    model_config = ConfigDict(from_attributes=True)


class ChangePasswordRequest(BaseModel):
    """
    用户修改密码请求。
    """

    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., description="新密码")

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        return validate_password_strength(v)


class ResetPasswordRequest(BaseModel):
    """
    管理员重置用户密码请求。
    """

    new_password: str = Field(..., description="新密码")

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        return validate_password_strength(v)
