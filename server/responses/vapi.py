import datetime as dt
from typing import Union

from pydantic import BaseModel


# Vapi Message Structure Types
from typing import Optional, Any, List


class ToolCallFunction(BaseModel):
    name: str
    arguments: dict


class ToolCall(BaseModel):
    id: str
    type: str
    function: ToolCallFunction


class ToolCallListItem(BaseModel):
    id: str
    type: str
    function: ToolCallFunction


class ToolWithToolCallListItem(BaseModel):
    type: str
    function: dict
    server: dict
    messages: List[dict]
    toolCall: dict


class Artifact(BaseModel):
    messages: List[dict]
    messagesOpenAIFormatted: List[dict]


class Assistant(BaseModel):
    id: str
    orgId: str
    name: str
    voice: dict
    createdAt: str
    updatedAt: str
    model: dict
    firstMessage: str
    voicemailMessage: str
    endCallMessage: str
    transcriber: dict
    clientMessages: List[str]


class Call(BaseModel):
    id: str
    orgId: str
    createdAt: str
    updatedAt: str
    type: str
    cost: int
    monitor: dict
    transport: dict
    webCallUrl: str
    status: str
    assistantId: str
    assistantOverrides: dict


class Message(BaseModel):
    timestamp: int
    type: str
    toolCalls: List[ToolCall]
    toolCallList: List[ToolCallListItem]
    toolWithToolCallList: List[ToolWithToolCallListItem]
    artifact: Artifact
    call: Call
    assistant: Assistant


class VapiRequest(BaseModel):
    message: Message


# Tools Response Types
class TodoResponse(BaseModel):
    id: int
    title: str
    description: Union[str, None]
    completed: bool

    class Config:
        from_attributes = True


class ReminderResponse(BaseModel):
    id: int
    remainder_text: str
    importance: str

    class Config:
        from_attributes = True


class CalendarEventResponse(BaseModel):
    id: int
    title: str
    description: Union[str, None]
    event_from: dt.datetime
    event_to: dt.datetime

    class Config:
        from_attributes = True
