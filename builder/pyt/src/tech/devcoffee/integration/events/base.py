from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

__all__=[
    "BaseEvent"
]

class BaseEvent(BaseModel):
    event_id: UUID = Field(..., description="Unique identifier of the event (uuid)")
    trace_id: UUID | None = Field(default=None, description="Trace identifier for distributed tracing (uuid)")
    event_time: datetime = Field(..., description="When the token was issued")
    event_name: str = Field(default="token.issued", description="The name of the event")
    producer: str = Field(..., description="Service that produced the event")
    data: dict[str, Any] = Field(..., description="Event payload data")

    def __str__(self) -> str:
        return f"{self.event_name} ({self.event_id})"

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.event_name} {self.event_id}>"
