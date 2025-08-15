"""
Data models for token usage tracking and analytics.
"""

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class ModelType(str, Enum):
    """Claude model types for usage tracking."""
    OPUS = "claude-3-opus"
    SONNET = "claude-3-sonnet"
    SONNET_35 = "claude-3.5-sonnet"
    HAIKU = "claude-3-haiku"
    UNKNOWN = "unknown"


class TokenType(str, Enum):
    """Types of token usage."""
    INPUT = "input"
    OUTPUT = "output"
    CACHE_CREATION = "cache_creation"
    CACHE_READ = "cache_read"


class UsageEntry(BaseModel):
    """Individual token usage entry."""
    model_config = {"protected_namespaces": []}
    
    id: str = Field(..., description="Unique usage entry ID")
    instance_id: str = Field(..., description="Instance that generated the usage")
    session_id: Optional[str] = Field(None, description="Chat session ID")
    message_id: Optional[str] = Field(None, description="Message ID if applicable")
    timestamp: datetime = Field(default_factory=datetime.now, description="When the usage occurred")
    
    # Model information
    model: ModelType = Field(..., description="Claude model used")
    claude_model_version: Optional[str] = Field(None, description="Specific model version")
    
    # Token counts
    input_tokens: int = Field(default=0, description="Input tokens used")
    output_tokens: int = Field(default=0, description="Output tokens generated")
    cache_creation_tokens: int = Field(default=0, description="Tokens used for cache creation")
    cache_read_tokens: int = Field(default=0, description="Tokens read from cache")
    
    # Cost information
    input_cost: float = Field(default=0.0, description="Cost of input tokens in USD")
    output_cost: float = Field(default=0.0, description="Cost of output tokens in USD")
    cache_creation_cost: float = Field(default=0.0, description="Cost of cache creation in USD")
    cache_read_cost: float = Field(default=0.0, description="Cost of cache reads in USD")
    total_cost: float = Field(default=0.0, description="Total cost in USD")
    
    # Context
    conversation_turns: int = Field(default=1, description="Number of turns in conversation")
    context_window_size: Optional[int] = Field(None, description="Context window size used")
    
    # Metadata
    user_agent: Optional[str] = Field(None, description="User agent string")
    ip_address: Optional[str] = Field(None, description="Client IP address")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }


class UsageAggregation(BaseModel):
    """Aggregated usage statistics."""
    model_config = {"protected_namespaces": []}
    
    period_start: datetime = Field(..., description="Start of aggregation period")
    period_end: datetime = Field(..., description="End of aggregation period")
    instance_id: Optional[str] = Field(None, description="Instance ID if filtered")
    
    # Token totals
    total_input_tokens: int = Field(default=0, description="Total input tokens")
    total_output_tokens: int = Field(default=0, description="Total output tokens")
    total_cache_creation_tokens: int = Field(default=0, description="Total cache creation tokens")
    total_cache_read_tokens: int = Field(default=0, description="Total cache read tokens")
    total_tokens: int = Field(default=0, description="Grand total tokens")
    
    # Cost totals
    total_input_cost: float = Field(default=0.0, description="Total input cost")
    total_output_cost: float = Field(default=0.0, description="Total output cost")
    total_cache_creation_cost: float = Field(default=0.0, description="Total cache creation cost")
    total_cache_read_cost: float = Field(default=0.0, description="Total cache read cost")
    total_cost: float = Field(default=0.0, description="Grand total cost")
    
    # Usage counts
    total_requests: int = Field(default=0, description="Total number of requests")
    total_sessions: int = Field(default=0, description="Total number of sessions")
    unique_instances: int = Field(default=0, description="Number of unique instances")
    
    # Model breakdown
    claude_model_usage: Dict[str, Dict[str, Any]] = Field(default_factory=dict, description="Usage by model")
    
    # Efficiency metrics
    avg_tokens_per_request: float = Field(default=0.0, description="Average tokens per request")
    avg_cost_per_request: float = Field(default=0.0, description="Average cost per request")
    cache_hit_rate: float = Field(default=0.0, description="Cache hit rate percentage")
    
    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }


class UsageQuery(BaseModel):
    """Query parameters for usage analytics."""
    start_date: Optional[datetime] = Field(None, description="Start date for query")
    end_date: Optional[datetime] = Field(None, description="End date for query")
    instance_id: Optional[str] = Field(None, description="Filter by instance ID")
    session_id: Optional[str] = Field(None, description="Filter by session ID")
    model: Optional[ModelType] = Field(None, description="Filter by model type")
    
    # Aggregation options
    group_by: Optional[str] = Field("day", description="Grouping: hour, day, week, month")
    include_cache: bool = Field(True, description="Include cache usage in results")
    
    # Pagination
    offset: int = Field(default=0, description="Result offset")
    limit: int = Field(default=100, description="Result limit")
    
    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }


class UsageStats(BaseModel):
    """Current usage statistics and quotas."""
    current_period_start: datetime = Field(..., description="Current billing period start")
    current_period_end: datetime = Field(..., description="Current billing period end")
    
    # Current period usage
    current_tokens: int = Field(default=0, description="Tokens used this period")
    current_cost: float = Field(default=0.0, description="Cost this period")
    current_requests: int = Field(default=0, description="Requests this period")
    
    # Quotas and limits
    token_quota: Optional[int] = Field(None, description="Token quota per period")
    cost_quota: Optional[float] = Field(None, description="Cost quota per period")
    request_quota: Optional[int] = Field(None, description="Request quota per period")
    
    # Usage percentages
    token_usage_percent: float = Field(default=0.0, description="Percentage of token quota used")
    cost_usage_percent: float = Field(default=0.0, description="Percentage of cost quota used")
    request_usage_percent: float = Field(default=0.0, description="Percentage of request quota used")
    
    # Projections
    projected_monthly_cost: float = Field(default=0.0, description="Projected monthly cost")
    projected_monthly_tokens: int = Field(default=0, description="Projected monthly tokens")
    
    # Recent trends
    daily_average_cost: float = Field(default=0.0, description="Daily average cost")
    daily_average_tokens: int = Field(default=0, description="Daily average tokens")
    trend_direction: str = Field(default="stable", description="Usage trend: increasing, decreasing, stable")
    
    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }


class ExportFormat(str, Enum):
    """Export format options."""
    JSON = "json"
    CSV = "csv"
    XLSX = "xlsx"


class UsageExport(BaseModel):
    """Usage data export request."""
    format: ExportFormat = Field(..., description="Export format")
    query: UsageQuery = Field(..., description="Data query parameters")
    include_raw_data: bool = Field(True, description="Include raw usage entries")
    include_aggregations: bool = Field(True, description="Include aggregated statistics")
    filename: Optional[str] = Field(None, description="Custom filename")
    
    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }


# Model pricing configuration (can be updated via API)
MODEL_PRICING = {
    ModelType.OPUS: {
        "input_price_per_1k": 0.015,
        "output_price_per_1k": 0.075,
        "cache_creation_price_per_1k": 0.0225,  # 1.5x input price
        "cache_read_price_per_1k": 0.0015,      # 0.1x input price
    },
    ModelType.SONNET_35: {
        "input_price_per_1k": 0.003,
        "output_price_per_1k": 0.015,
        "cache_creation_price_per_1k": 0.0045,
        "cache_read_price_per_1k": 0.0003,
    },
    ModelType.SONNET: {
        "input_price_per_1k": 0.003,
        "output_price_per_1k": 0.015,
        "cache_creation_price_per_1k": 0.0045,
        "cache_read_price_per_1k": 0.0003,
    },
    ModelType.HAIKU: {
        "input_price_per_1k": 0.00025,
        "output_price_per_1k": 0.00125,
        "cache_creation_price_per_1k": 0.000375,
        "cache_read_price_per_1k": 0.000025,
    },
}