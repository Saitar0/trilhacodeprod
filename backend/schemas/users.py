# ruff: noqa: EXE002

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterIn(BaseModel):
    name: str = Field(min_length=2)
    email: EmailStr
    password: str = Field(min_length=6)


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class ProfileIn(BaseModel):
    name: str | None = None
    profile: dict | None = None


class RoleIn(BaseModel):
    role: str


class UserOut(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str
