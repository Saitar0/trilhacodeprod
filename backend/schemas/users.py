# ruff: noqa: EXE002

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


def _check_password_bytes(value: str) -> str:
    if len(value.encode("utf-8")) > 72:
        raise ValueError("A senha não pode exceder 72 bytes")
    return value


class RegisterIn(BaseModel):
    name: str = Field(min_length=2)
    email: EmailStr
    password: str = Field(min_length=12, max_length=72)

    _password_bytes = field_validator("password")(_check_password_bytes)


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class EmailIn(BaseModel):
    email: EmailStr


class TokenIn(BaseModel):
    token: str = Field(min_length=32, max_length=256)


class PasswordResetIn(TokenIn):
    password: str = Field(min_length=12, max_length=72)

    _password_bytes = field_validator("password")(_check_password_bytes)


class PasswordChangeIn(BaseModel):
    current_password: str
    password: str = Field(min_length=12, max_length=72)

    _password_bytes = field_validator("password")(_check_password_bytes)


class ProfileIn(BaseModel):
    name: str | None = None
    profile: dict | None = None


class RoleIn(BaseModel):
    role: str


class UserOut(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str
