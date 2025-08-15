"""
Data models for chat and messaging functionality.
"""

from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class MessageRole(str, Enum):
    """Message roles in chat."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class MessageStatus(str, Enum):
    """Status of chat messages."""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    ERROR = "error"


class ChatMessage(BaseModel):
    """Individual chat message model."""
    id: str = Field(..., description="Unique message identifier")
    instance_id: str = Field(..., description="Target Claude Code instance ID")
    role: MessageRole = Field(..., description="Message role (user/assistant/system)")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.now, description="Message timestamp")
    status: MessageStatus = Field(default=MessageStatus.PENDING, description="Message status")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    model_config = {
        "use_enum_values": True,
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }


class ChatRequest(BaseModel):
    """Request model for sending messages to Claude Code instances."""
    instance_id: str = Field(..., description="Target instance ID")
    message: str = Field(..., min_length=1, description="Message to send")
    stream: bool = Field(default=False, description="Whether to stream the response")
    context: Optional[List[Dict[str, str]]] = Field(None, description="Previous conversation context")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional request metadata")


class ChatResponse(BaseModel):
    """Response model from Claude Code instances."""
    message_id: str = Field(..., description="Response message ID")
    instance_id: str = Field(..., description="Source instance ID")
    content: str = Field(..., description="Response content")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")
    response_time_ms: Optional[float] = Field(None, description="Response time in milliseconds")
    error: Optional[str] = Field(None, description="Error message if any")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional response metadata")
    
    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }


class ChatHistory(BaseModel):
    """Chat history for an instance."""
    instance_id: str = Field(..., description="Instance ID")
    messages: List[ChatMessage] = Field(default_factory=list, description="List of messages")
    created_at: datetime = Field(default_factory=datetime.now, description="History creation time")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update time")
    
    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }


class ChatSession(BaseModel):
    """Active chat session model."""
    session_id: str = Field(..., description="Unique session identifier")
    instance_id: str = Field(..., description="Associated instance ID")
    active: bool = Field(default=True, description="Whether session is active")
    created_at: datetime = Field(default_factory=datetime.now, description="Session creation time")
    last_activity: datetime = Field(default_factory=datetime.now, description="Last activity time")
    message_count: int = Field(default=0, description="Number of messages in session")
    
    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }