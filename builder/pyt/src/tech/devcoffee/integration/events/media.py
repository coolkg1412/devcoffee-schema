from typing import Literal

from pydantic import ConfigDict, Field

from .base import BaseEvent, EventData

__all__ = [
    "MediaAssetCreatedData",
    "MediaAssetCreatedEvent",
]


class MediaAssetCreatedData(EventData):
    model_config = ConfigDict(extra="ignore")

    asset_id: int = Field(..., description="The identifier of the media asset.")
    file_id: int | None = Field(default=None, description="The identifier of the underlying media file, if available.")
    storage_provider: str = Field(..., description="The storage provider holding the media file.")
    file_path: str = Field(..., description="The stored path of the media file.")
    original_filename: str = Field(..., description="The original filename of the media file.")


class MediaAssetCreatedEvent(BaseEvent[MediaAssetCreatedData]):
    event_version: int = Field(default=2, description="Schema version used by this event.")
    event_name: Literal["media.asset.created"] = Field(
        default="media.asset.created", description="The name of the event"
    )
