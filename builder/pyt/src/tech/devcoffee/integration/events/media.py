from typing import Literal

from pydantic import BaseModel, Field

from .base import BaseEvent

__all__ = [
    "MediaAssetCreatedData",
    "MediaAssetCreatedEvent",
]


class MediaAssetCreatedData(BaseModel):
    asset_id: int = Field(..., description="The identifier of the media asset.")
    storage_provider: str = Field(..., description="The storage provider holding the media file.")
    file_path: str = Field(..., description="The stored path of the media file.")
    original_filename: str = Field(..., description="The original filename of the media file.")


class MediaAssetCreatedEvent(BaseEvent):
    event_version: int = Field(default=1, description="Schema version used by this event.")
    event_name: Literal["media.asset.created"] = Field(
        default="media.asset.created", description="The name of the event"
    )
    data: MediaAssetCreatedData
