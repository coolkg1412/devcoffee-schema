from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from .base import BaseEvent

__all__ = [
    "User",
    "AuthenticationMethod",
    "Authentication",
    "Client",
    "AuthenticationPayload",
    "UserAuthenticationSucceededEvent",
]


class User(BaseModel):
    id: UUID = Field(..., description="User's unique identifier (uuid)")
    email: str = Field(..., description="User's email")
    first_name: str = Field(..., alias="firstName", description="User's first name")
    last_name: str = Field(..., alias="lastName", description="User's last name")
    language: str | None = Field(default=None, description="User's language")
    timezone: str | None = Field(default=None, description="User's timezone")
    date_joined: datetime | None = Field(default=None, alias="dateJoined", description="User's joined date.")

    model_config = ConfigDict(populate_by_name=True)


class AuthenticationMethod(StrEnum):
    PASSWORD = "PASSWORD"
    OIDC = "OIDC"
    REMEMBER_TOKEN = "REMEMBER_TOKEN"
    API_KEY = "API_KEY"


class Authentication(BaseModel):
    method: AuthenticationMethod
    provider: str | None = Field(
        default=None, description="OIDC provider that authenticated the user. e.g. google, github"
    )


class Client(BaseModel):
    ip: str | None = Field(default=None, description="IP address of the client")
    user_agent: str | None = Field(default=None, description="User agent of the client")
    device: str | None = Field(default=None, description="Device identifier of the client")


class AuthenticationPayload(BaseModel):
    user: User
    authentication: Authentication
    client: Client


class UserAuthenticationSucceededEvent(BaseEvent):
    data: AuthenticationPayload
