from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from .base import BaseEvent

__all__ = [
    "IssuedTokenData",
    "RevokedTokenData",
    "TokenIssuedEvent",
    "TokenRevokedEvent",
]


class IssuedTokenData(BaseModel):
    token: str = Field(..., description="The issued token string.")

    token_type: str = Field(
        ..., alias="tokenType", description="The type of the token issued (access_token, id_token)."
    )
    email: str = Field(..., description="The email of the user for whom the token was issued.")
    user_id: UUID = Field(..., alias="userId", description="The unique identifier of the user.")
    client_id: str = Field(
        ..., alias="clientId", description="The client identifier of the application that requested the token."
    )

    model_config = ConfigDict(populate_by_name=True)


class RevokedTokenData(BaseModel):
    token: str = Field(..., description="The revoked token string.")
    token_type: str = Field(
        ..., alias="tokenType", description="The type of the token revoked (access_token, id_token)."
    )
    email: str = Field(..., description="The email of the user for whom the token was revoked.")
    user_id: UUID = Field(..., alias="userId", description="The unique identifier of the user.")
    client_id: str = Field(
        ..., alias="clientId", description="The client identifier of the application that requested the token."
    )

    model_config = ConfigDict(populate_by_name=True)


class TokenIssuedEvent(BaseEvent):
    data: IssuedTokenData


class TokenRevokedEvent(BaseEvent):
    data: RevokedTokenData
