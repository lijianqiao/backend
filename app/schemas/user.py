"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: user.py
@DateTime: 2025-12-30 14:45:00
@Docs: 用户 User 相关 Schema 定义。
"""

from uuid import UUID

import phonenumbers
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


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
            # 默认尝试解析为中国大陆号码，如果输入不带 + 号
            parsed_number = phonenumbers.parse(v, "CN")
            if not phonenumbers.is_valid_number(parsed_number):
                raise ValueError("无效的手机号码")
            # 格式化为 E.164
            return phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
        except phonenumbers.NumberParseException as e:
            raise ValueError("手机号码格式错误") from e


class UserCreate(UserBase):
    password: str = Field(..., description="密码")


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


class UserResponse(UserBase):
    id: UUID

    model_config = ConfigDict(from_attributes=True)
