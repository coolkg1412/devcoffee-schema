from datetime import datetime
from typing import Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

__all__ = [
    "EventData",
    "BaseEvent",
]


class EventData(BaseModel):
    """Base for every event payload. `extra="allow"` keeps unknown keys when an event is parsed with the bare
    `BaseEvent` (e.g. a generic consumer that does not know the concrete event type)."""

    model_config = ConfigDict(extra="allow")


DataT = TypeVar("DataT", bound=EventData)


class BaseEvent(BaseModel, Generic[DataT]):
    event_id: UUID = Field(..., description="Unique identifier of the event (uuid)")
    trace_id: UUID | None = Field(default=None, description="Trace identifier for distributed tracing (uuid)")
    event_time: datetime = Field(..., description="When the token was issued")
    event_name: str = Field(default="token.issued", description="The name of the event")
    producer: str = Field(..., description="Service that produced the event")
    data: DataT = Field(..., description="Event payload data")

    def __str__(self) -> str:
        return f"{self.event_name} ({self.event_id})"

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.event_name} {self.event_id}>"
