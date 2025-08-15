"""
Data models for Claude Code instances.
"""

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator


class InstanceType(str, Enum):
    """Types of Claude Code instances."""
    LOCAL = "local"
    DOCKER = "docker"


class InstanceStatus(str, Enum):
    """Status of Claude Code instances."""
    ONLINE = "online"
    OFFLINE = "offline"
    ERROR = "error"
    UNKNOWN = "unknown"


class Instance(BaseModel):
    """Claude Code instance model."""
    id: str = Field(..., description="Unique instance identifier")
    name: str = Field(..., description="Human-readable instance name")
    type: InstanceType = Field(..., description="Type of instance (local or docker)")
    host: str = Field(default="localhost", description="Host address")
    port: int = Field(..., description="Port number")
    status: InstanceStatus = Field(default=InstanceStatus.UNKNOWN, description="Current status")
    url: Optional[str] = Field(None, description="Full URL to the instance")
    container_id: Optional[str] = Field(None, description="Docker container ID if applicable")
    last_seen: Optional[datetime] = Field(None, description="Last successful connection")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    @field_validator('url', mode='before')
    @classmethod
    def build_url(cls, v, info):
        """Automatically build URL from host and port if not provided."""
        if not v and info.data:
            host = info.data.get('host')
            port = info.data.get('port')
            if host and port:
                protocol = "https" if port == 443 else "http"
                return f"{protocol}://{host}:{port}"
        return v
    
    model_config = {
        "use_enum_values": True,
        "json_encoders": {
            datetime: lambda v: v.isoformat() if v else None
        }
    }


class InstanceCreate(BaseModel):
    """Model for creating new instances."""
    name: str = Field(..., min_length=1, max_length=100, description="Instance name")
    type: InstanceType = Field(default=InstanceType.LOCAL, description="Instance type")
    host: str = Field(default="localhost", description="Host address")
    port: int = Field(..., ge=1, le=65535, description="Port number")
    container_id: Optional[str] = Field(None, description="Docker container ID")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class InstanceUpdate(BaseModel):
    """Model for updating existing instances."""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Instance name")
    host: Optional[str] = Field(None, description="Host address")
    port: Optional[int] = Field(None, ge=1, le=65535, description="Port number")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class InstanceHealth(BaseModel):
    """Health check response for an instance."""
    instance_id: str
    status: InstanceStatus
    response_time_ms: Optional[float] = None
    error_message: Optional[str] = None
    last_checked: datetime = Field(default_factory=datetime.now)
    
    model_config = {
        "use_enum_values": True,
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }