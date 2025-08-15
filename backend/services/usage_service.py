"""
Service for tracking and analyzing Claude Code token usage.
"""

import json
import os
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging
from collections import defaultdict

from models.usage import (
    UsageEntry, UsageAggregation, UsageQuery, UsageStats, 
    ModelType, TokenType, MODEL_PRICING, ExportFormat, UsageExport
)

logger = logging.getLogger(__name__)


class UsageTracker:
    """Token usage tracking and analytics service."""
    
    def __init__(self, data_dir: str = "usage_data"):
        """Initialize usage tracker with data directory."""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # File paths
        self.usage_file = self.data_dir / "usage_entries.jsonl"
        self.stats_file = self.data_dir / "usage_stats.json"
        self.config_file = self.data_dir / "usage_config.json"
        
        # Initialize files if they don't exist
        self._initialize_files()
        
        # Load configuration
        self.config = self._load_config()
    
    def _initialize_files(self):
        """Initialize data files if they don't exist."""
        if not self.usage_file.exists():
            self.usage_file.touch()
        
        if not self.stats_file.exists():
            initial_stats = {
                "total_entries": 0,
                "last_updated": datetime.now().isoformat(),
                "data_version": "1.0"
            }
            with open(self.stats_file, 'w') as f:
                json.dump(initial_stats, f, indent=2)
        
        if not self.config_file.exists():
            default_config = {
                "token_quota": None,
                "cost_quota": 100.0,  # $100 default
                "request_quota": None,
                "billing_period": "monthly",  # monthly, weekly, daily
                "timezone": "UTC",
                "auto_cleanup_days": 365,  # Keep 1 year of data
                "pricing": MODEL_PRICING
            }
            with open(self.config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
    
    def _load_config(self) -> Dict[str, Any]:
        """Load usage tracking configuration."""
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return {}
    
    def _save_config(self):
        """Save configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
    
    def calculate_cost(self, model: ModelType, input_tokens: int = 0, output_tokens: int = 0,
                      cache_creation_tokens: int = 0, cache_read_tokens: int = 0) -> Dict[str, float]:
        """Calculate costs for given token usage."""
        pricing = self.config.get("pricing", MODEL_PRICING).get(model)
        if not pricing:
            logger.warning(f"No pricing found for model {model}")
            return {
                "input_cost": 0.0,
                "output_cost": 0.0,
                "cache_creation_cost": 0.0,
                "cache_read_cost": 0.0,
                "total_cost": 0.0
            }
        
        input_cost = (input_tokens / 1000) * pricing["input_price_per_1k"]
        output_cost = (output_tokens / 1000) * pricing["output_price_per_1k"]
        cache_creation_cost = (cache_creation_tokens / 1000) * pricing["cache_creation_price_per_1k"]
        cache_read_cost = (cache_read_tokens / 1000) * pricing["cache_read_price_per_1k"]
        
        total_cost = input_cost + output_cost + cache_creation_cost + cache_read_cost
        
        return {
            "input_cost": round(input_cost, 6),
            "output_cost": round(output_cost, 6),
            "cache_creation_cost": round(cache_creation_cost, 6),
            "cache_read_cost": round(cache_read_cost, 6),
            "total_cost": round(total_cost, 6)
        }
    
    def track_usage(self, instance_id: str, model: ModelType, input_tokens: int = 0,
                   output_tokens: int = 0, cache_creation_tokens: int = 0,
                   cache_read_tokens: int = 0, session_id: Optional[str] = None,
                   message_id: Optional[str] = None, **kwargs) -> UsageEntry:
        """Track a new usage entry."""
        
        # Calculate costs
        costs = self.calculate_cost(model, input_tokens, output_tokens, 
                                  cache_creation_tokens, cache_read_tokens)
        
        # Create usage entry
        entry = UsageEntry(
            id=str(uuid.uuid4()),
            instance_id=instance_id,
            session_id=session_id,
            message_id=message_id,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cache_creation_tokens=cache_creation_tokens,
            cache_read_tokens=cache_read_tokens,
            **costs,
            **kwargs
        )
        
        # Save to file
        try:
            with open(self.usage_file, 'a') as f:
                f.write(entry.model_dump_json() + '\n')
            
            logger.info(f"Tracked usage: {entry.total_tokens} tokens, ${entry.total_cost:.4f}")
            return entry
            
        except Exception as e:
            logger.error(f"Failed to save usage entry: {e}")
            raise
    
    def get_usage_entries(self, query: UsageQuery) -> List[UsageEntry]:
        """Get usage entries based on query parameters."""
        entries = []
        
        try:
            with open(self.usage_file, 'r') as f:
                for line in f:
                    if line.strip():
                        entry_data = json.loads(line)
                        entry = UsageEntry(**entry_data)
                        
                        # Apply filters
                        if self._matches_query(entry, query):
                            entries.append(entry)
            
            # Sort by timestamp (newest first)
            entries.sort(key=lambda x: x.timestamp, reverse=True)
            
            # Apply pagination
            start_idx = query.offset
            end_idx = start_idx + query.limit
            return entries[start_idx:end_idx]
            
        except Exception as e:
            logger.error(f"Failed to read usage entries: {e}")
            return []
    
    def _matches_query(self, entry: UsageEntry, query: UsageQuery) -> bool:
        """Check if entry matches query filters."""
        if query.start_date and entry.timestamp < query.start_date:
            return False
        if query.end_date and entry.timestamp > query.end_date:
            return False
        if query.instance_id and entry.instance_id != query.instance_id:
            return False
        if query.session_id and entry.session_id != query.session_id:
            return False
        if query.model and entry.model != query.model:
            return False
        
        return True
    
    def get_usage_aggregation(self, query: UsageQuery) -> UsageAggregation:
        """Get aggregated usage statistics."""
        entries = self.get_usage_entries(UsageQuery(
            start_date=query.start_date,
            end_date=query.end_date,
            instance_id=query.instance_id,
            session_id=query.session_id,
            model=query.model,
            limit=10000  # Get all matching entries
        ))
        
        if not entries:
            return UsageAggregation(
                period_start=query.start_date or datetime.now() - timedelta(days=30),
                period_end=query.end_date or datetime.now(),
                instance_id=query.instance_id
            )
        
        # Calculate aggregations
        total_input_tokens = sum(e.input_tokens for e in entries)
        total_output_tokens = sum(e.output_tokens for e in entries)
        total_cache_creation_tokens = sum(e.cache_creation_tokens for e in entries)
        total_cache_read_tokens = sum(e.cache_read_tokens for e in entries)
        
        total_input_cost = sum(e.input_cost for e in entries)
        total_output_cost = sum(e.output_cost for e in entries)
        total_cache_creation_cost = sum(e.cache_creation_cost for e in entries)
        total_cache_read_cost = sum(e.cache_read_cost for e in entries)
        
        # Model breakdown
        model_usage = defaultdict(lambda: {
            "tokens": 0, "cost": 0.0, "requests": 0,
            "input_tokens": 0, "output_tokens": 0
        })
        
        for entry in entries:
            model_data = model_usage[entry.model.value]
            model_data["tokens"] += entry.input_tokens + entry.output_tokens
            model_data["cost"] += entry.total_cost
            model_data["requests"] += 1
            model_data["input_tokens"] += entry.input_tokens
            model_data["output_tokens"] += entry.output_tokens
        
        # Calculate efficiency metrics
        total_requests = len(entries)
        total_tokens = total_input_tokens + total_output_tokens
        total_cost = total_input_cost + total_output_cost + total_cache_creation_cost + total_cache_read_cost
        
        avg_tokens_per_request = total_tokens / total_requests if total_requests > 0 else 0
        avg_cost_per_request = total_cost / total_requests if total_requests > 0 else 0
        
        # Cache hit rate
        cache_requests = sum(1 for e in entries if e.cache_read_tokens > 0)
        cache_hit_rate = (cache_requests / total_requests * 100) if total_requests > 0 else 0
        
        # Unique sessions and instances
        unique_sessions = len(set(e.session_id for e in entries if e.session_id))
        unique_instances = len(set(e.instance_id for e in entries))
        
        return UsageAggregation(
            period_start=query.start_date or min(e.timestamp for e in entries),
            period_end=query.end_date or max(e.timestamp for e in entries),
            instance_id=query.instance_id,
            total_input_tokens=total_input_tokens,
            total_output_tokens=total_output_tokens,
            total_cache_creation_tokens=total_cache_creation_tokens,
            total_cache_read_tokens=total_cache_read_tokens,
            total_tokens=total_tokens,
            total_input_cost=total_input_cost,
            total_output_cost=total_output_cost,
            total_cache_creation_cost=total_cache_creation_cost,
            total_cache_read_cost=total_cache_read_cost,
            total_cost=total_cost,
            total_requests=total_requests,
            total_sessions=unique_sessions,
            unique_instances=unique_instances,
            model_usage=dict(model_usage),
            avg_tokens_per_request=avg_tokens_per_request,
            avg_cost_per_request=avg_cost_per_request,
            cache_hit_rate=cache_hit_rate
        )
    
    def get_current_usage_stats(self) -> UsageStats:
        """Get current period usage statistics and projections."""
        now = datetime.now()
        
        # Determine current billing period
        billing_period = self.config.get("billing_period", "monthly")
        if billing_period == "monthly":
            period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if now.month == 12:
                period_end = period_start.replace(year=now.year + 1, month=1) - timedelta(seconds=1)
            else:
                period_end = period_start.replace(month=now.month + 1) - timedelta(seconds=1)
        elif billing_period == "weekly":
            days_since_monday = now.weekday()
            period_start = (now - timedelta(days=days_since_monday)).replace(hour=0, minute=0, second=0, microsecond=0)
            period_end = period_start + timedelta(days=7) - timedelta(seconds=1)
        else:  # daily
            period_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            period_end = period_start + timedelta(days=1) - timedelta(seconds=1)
        
        # Get current period usage
        query = UsageQuery(start_date=period_start, end_date=period_end)
        aggregation = self.get_usage_aggregation(query)
        
        # Get quotas from config
        token_quota = self.config.get("token_quota")
        cost_quota = self.config.get("cost_quota")
        request_quota = self.config.get("request_quota")
        
        # Calculate usage percentages
        token_usage_percent = (aggregation.total_tokens / token_quota * 100) if token_quota else 0
        cost_usage_percent = (aggregation.total_cost / cost_quota * 100) if cost_quota else 0
        request_usage_percent = (aggregation.total_requests / request_quota * 100) if request_quota else 0
        
        # Calculate projections (based on current usage rate)
        days_in_period = (period_end - period_start).days + 1
        days_elapsed = (now - period_start).days + 1
        
        if days_elapsed > 0:
            daily_cost = aggregation.total_cost / days_elapsed
            daily_tokens = aggregation.total_tokens / days_elapsed
            
            projected_monthly_cost = daily_cost * 30
            projected_monthly_tokens = int(daily_tokens * 30)
        else:
            daily_cost = 0
            daily_tokens = 0
            projected_monthly_cost = 0
            projected_monthly_tokens = 0
        
        # Determine trend (compare with previous period)
        prev_period_start = period_start - (period_end - period_start + timedelta(seconds=1))
        prev_period_end = period_start - timedelta(seconds=1)
        prev_query = UsageQuery(start_date=prev_period_start, end_date=prev_period_end)
        prev_aggregation = self.get_usage_aggregation(prev_query)
        
        if prev_aggregation.total_cost > 0:
            cost_change = (aggregation.total_cost - prev_aggregation.total_cost) / prev_aggregation.total_cost
            if cost_change > 0.1:
                trend_direction = "increasing"
            elif cost_change < -0.1:
                trend_direction = "decreasing"
            else:
                trend_direction = "stable"
        else:
            trend_direction = "stable"
        
        return UsageStats(
            current_period_start=period_start,
            current_period_end=period_end,
            current_tokens=aggregation.total_tokens,
            current_cost=aggregation.total_cost,
            current_requests=aggregation.total_requests,
            token_quota=token_quota,
            cost_quota=cost_quota,
            request_quota=request_quota,
            token_usage_percent=token_usage_percent,
            cost_usage_percent=cost_usage_percent,
            request_usage_percent=request_usage_percent,
            projected_monthly_cost=projected_monthly_cost,
            projected_monthly_tokens=projected_monthly_tokens,
            daily_average_cost=daily_cost,
            daily_average_tokens=int(daily_tokens),
            trend_direction=trend_direction
        )
    
    def export_usage_data(self, export_request: UsageExport) -> str:
        """Export usage data in specified format."""
        # Get data based on query
        entries = self.get_usage_entries(export_request.query)
        
        # Generate filename if not provided
        if not export_request.filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_request.filename = f"claude_usage_export_{timestamp}"
        
        export_path = self.data_dir / f"{export_request.filename}.{export_request.format.value}"
        
        if export_request.format == ExportFormat.JSON:
            export_data = {
                "export_info": {
                    "timestamp": datetime.now().isoformat(),
                    "query": export_request.query.model_dump(),
                    "total_entries": len(entries)
                }
            }
            
            if export_request.include_raw_data:
                export_data["usage_entries"] = [entry.model_dump() for entry in entries]
            
            if export_request.include_aggregations:
                export_data["aggregation"] = self.get_usage_aggregation(export_request.query).model_dump()
            
            with open(export_path, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
        
        elif export_request.format == ExportFormat.CSV:
            import csv
            
            with open(export_path, 'w', newline='') as f:
                if entries:
                    fieldnames = list(entries[0].model_dump().keys())
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    for entry in entries:
                        writer.writerow(entry.model_dump())
        
        return str(export_path)
    
    def cleanup_old_data(self, days_to_keep: int = None):
        """Clean up old usage data."""
        if days_to_keep is None:
            days_to_keep = self.config.get("auto_cleanup_days", 365)
        
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        # Read all entries and keep only recent ones
        recent_entries = []
        try:
            with open(self.usage_file, 'r') as f:
                for line in f:
                    if line.strip():
                        entry_data = json.loads(line)
                        entry_timestamp = datetime.fromisoformat(entry_data["timestamp"])
                        if entry_timestamp >= cutoff_date:
                            recent_entries.append(line)
            
            # Rewrite file with recent entries only
            with open(self.usage_file, 'w') as f:
                f.writelines(recent_entries)
            
            logger.info(f"Cleaned up usage data, kept {len(recent_entries)} recent entries")
            
        except Exception as e:
            logger.error(f"Failed to cleanup old data: {e}")


# Global usage tracker instance
usage_tracker = UsageTracker()