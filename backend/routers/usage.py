"""
API endpoints for token usage tracking and analytics.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from fastapi.responses import FileResponse
import logging

from auth import get_current_user
from models.usage import (
    UsageEntry, UsageAggregation, UsageQuery, UsageStats, 
    ModelType, TokenType, UsageExport, ExportFormat
)
from services.usage_service import usage_tracker

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/usage", tags=["usage"])


@router.post("/track", response_model=UsageEntry)
async def track_usage(
    instance_id: str,
    model: ModelType,
    input_tokens: int = 0,
    output_tokens: int = 0,
    cache_creation_tokens: int = 0,
    cache_read_tokens: int = 0,
    session_id: Optional[str] = None,
    message_id: Optional[str] = None,
    user_agent: Optional[str] = None,
    conversation_turns: int = 1,
    context_window_size: Optional[int] = None,
    current_user: dict = Depends(get_current_user)
):
    """Track token usage for analytics."""
    try:
        entry = usage_tracker.track_usage(
            instance_id=instance_id,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cache_creation_tokens=cache_creation_tokens,
            cache_read_tokens=cache_read_tokens,
            session_id=session_id,
            message_id=message_id,
            user_agent=user_agent,
            conversation_turns=conversation_turns,
            context_window_size=context_window_size
        )
        return entry
    except Exception as e:
        logger.error(f"Failed to track usage: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to track usage: {str(e)}")


@router.get("/entries", response_model=List[UsageEntry])
async def get_usage_entries(
    start_date: Optional[datetime] = Query(None, description="Start date filter"),
    end_date: Optional[datetime] = Query(None, description="End date filter"),
    instance_id: Optional[str] = Query(None, description="Instance ID filter"),
    session_id: Optional[str] = Query(None, description="Session ID filter"),
    model: Optional[ModelType] = Query(None, description="Model filter"),
    offset: int = Query(0, description="Result offset"),
    limit: int = Query(100, description="Result limit"),
    current_user: dict = Depends(get_current_user)
):
    """Get usage entries with optional filtering."""
    try:
        query = UsageQuery(
            start_date=start_date,
            end_date=end_date,
            instance_id=instance_id,
            session_id=session_id,
            model=model,
            offset=offset,
            limit=limit
        )
        return usage_tracker.get_usage_entries(query)
    except Exception as e:
        logger.error(f"Failed to get usage entries: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get usage entries: {str(e)}")


@router.get("/aggregation", response_model=UsageAggregation)
async def get_usage_aggregation(
    start_date: Optional[datetime] = Query(None, description="Start date filter"),
    end_date: Optional[datetime] = Query(None, description="End date filter"),
    instance_id: Optional[str] = Query(None, description="Instance ID filter"),
    session_id: Optional[str] = Query(None, description="Session ID filter"),
    model: Optional[ModelType] = Query(None, description="Model filter"),
    group_by: str = Query("day", description="Grouping: hour, day, week, month"),
    current_user: dict = Depends(get_current_user)
):
    """Get aggregated usage statistics."""
    try:
        query = UsageQuery(
            start_date=start_date,
            end_date=end_date,
            instance_id=instance_id,
            session_id=session_id,
            model=model,
            group_by=group_by
        )
        return usage_tracker.get_usage_aggregation(query)
    except Exception as e:
        logger.error(f"Failed to get usage aggregation: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get usage aggregation: {str(e)}")


@router.get("/stats", response_model=UsageStats)
async def get_current_usage_stats(
    current_user: dict = Depends(get_current_user)
):
    """Get current usage statistics and quotas."""
    try:
        return usage_tracker.get_current_usage_stats()
    except Exception as e:
        logger.error(f"Failed to get usage stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get usage stats: {str(e)}")


@router.get("/timeline")
async def get_usage_timeline(
    days: int = Query(30, description="Number of days to include"),
    instance_id: Optional[str] = Query(None, description="Instance ID filter"),
    group_by: str = Query("day", description="Grouping: hour, day, week"),
    current_user: dict = Depends(get_current_user)
):
    """Get usage timeline data for charts."""
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        query = UsageQuery(
            start_date=start_date,
            end_date=end_date,
            instance_id=instance_id,
            group_by=group_by,
            limit=1000
        )
        
        entries = usage_tracker.get_usage_entries(query)
        
        # Group entries by time period
        timeline = {}
        
        for entry in entries:
            if group_by == "hour":
                period_key = entry.timestamp.replace(minute=0, second=0, microsecond=0).isoformat()
            elif group_by == "day":
                period_key = entry.timestamp.date().isoformat()
            elif group_by == "week":
                week_start = entry.timestamp - timedelta(days=entry.timestamp.weekday())
                period_key = week_start.date().isoformat()
            else:
                period_key = entry.timestamp.date().isoformat()
            
            if period_key not in timeline:
                timeline[period_key] = {
                    "period": period_key,
                    "total_tokens": 0,
                    "total_cost": 0.0,
                    "requests": 0,
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "cache_tokens": 0,
                    "models": {}
                }
            
            period_data = timeline[period_key]
            period_data["total_tokens"] += entry.input_tokens + entry.output_tokens
            period_data["total_cost"] += entry.total_cost
            period_data["requests"] += 1
            period_data["input_tokens"] += entry.input_tokens
            period_data["output_tokens"] += entry.output_tokens
            period_data["cache_tokens"] += entry.cache_creation_tokens + entry.cache_read_tokens
            
            # Track by model
            model_key = entry.model.value
            if model_key not in period_data["models"]:
                period_data["models"][model_key] = {"tokens": 0, "cost": 0.0, "requests": 0}
            
            period_data["models"][model_key]["tokens"] += entry.input_tokens + entry.output_tokens
            period_data["models"][model_key]["cost"] += entry.total_cost
            period_data["models"][model_key]["requests"] += 1
        
        # Convert to sorted list
        timeline_list = list(timeline.values())
        timeline_list.sort(key=lambda x: x["period"])
        
        return {
            "timeline": timeline_list,
            "summary": {
                "total_periods": len(timeline_list),
                "date_range": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                },
                "group_by": group_by
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get usage timeline: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get usage timeline: {str(e)}")


@router.get("/models")
async def get_model_usage_breakdown(
    days: int = Query(30, description="Number of days to analyze"),
    instance_id: Optional[str] = Query(None, description="Instance ID filter"),
    current_user: dict = Depends(get_current_user)
):
    """Get usage breakdown by model type."""
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        query = UsageQuery(
            start_date=start_date,
            end_date=end_date,
            instance_id=instance_id,
            limit=10000
        )
        
        aggregation = usage_tracker.get_usage_aggregation(query)
        
        # Calculate percentages and add additional metrics
        total_cost = aggregation.total_cost
        total_tokens = aggregation.total_tokens
        
        model_breakdown = {}
        for model, data in aggregation.model_usage.items():
            cost_percentage = (data["cost"] / total_cost * 100) if total_cost > 0 else 0
            token_percentage = (data["tokens"] / total_tokens * 100) if total_tokens > 0 else 0
            
            model_breakdown[model] = {
                **data,
                "cost_percentage": round(cost_percentage, 2),
                "token_percentage": round(token_percentage, 2),
                "avg_cost_per_request": data["cost"] / data["requests"] if data["requests"] > 0 else 0,
                "avg_tokens_per_request": data["tokens"] / data["requests"] if data["requests"] > 0 else 0,
            }
        
        return {
            "model_breakdown": model_breakdown,
            "summary": {
                "total_models": len(model_breakdown),
                "total_cost": total_cost,
                "total_tokens": total_tokens,
                "date_range": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get model breakdown: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get model breakdown: {str(e)}")


@router.post("/export")
async def export_usage_data(
    export_request: UsageExport,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Export usage data in specified format."""
    try:
        file_path = usage_tracker.export_usage_data(export_request)
        
        # Schedule cleanup of export file after download
        background_tasks.add_task(cleanup_export_file, file_path, delay_seconds=3600)  # 1 hour
        
        return {
            "success": True,
            "message": "Export completed successfully",
            "download_url": f"/usage/download/{file_path.split('/')[-1]}",
            "file_path": file_path
        }
        
    except Exception as e:
        logger.error(f"Failed to export usage data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to export usage data: {str(e)}")


@router.get("/download/{filename}")
async def download_export_file(
    filename: str,
    current_user: dict = Depends(get_current_user)
):
    """Download exported usage data file."""
    try:
        file_path = usage_tracker.data_dir / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Export file not found")
        
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type='application/octet-stream'
        )
        
    except Exception as e:
        logger.error(f"Failed to download export file: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to download export file: {str(e)}")


@router.get("/pricing")
async def get_model_pricing(
    current_user: dict = Depends(get_current_user)
):
    """Get current model pricing information."""
    return {
        "pricing": usage_tracker.config.get("pricing", {}),
        "currency": "USD",
        "last_updated": datetime.now().isoformat()
    }


@router.put("/pricing")
async def update_model_pricing(
    pricing_data: Dict[str, Dict[str, float]],
    current_user: dict = Depends(get_current_user)
):
    """Update model pricing information."""
    try:
        usage_tracker.config["pricing"] = pricing_data
        usage_tracker._save_config()
        
        return {
            "success": True,
            "message": "Pricing updated successfully",
            "pricing": pricing_data
        }
        
    except Exception as e:
        logger.error(f"Failed to update pricing: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update pricing: {str(e)}")


@router.get("/config")
async def get_usage_config(
    current_user: dict = Depends(get_current_user)
):
    """Get usage tracking configuration."""
    return usage_tracker.config


@router.put("/config")
async def update_usage_config(
    config_data: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Update usage tracking configuration."""
    try:
        usage_tracker.config.update(config_data)
        usage_tracker._save_config()
        
        return {
            "success": True,
            "message": "Configuration updated successfully",
            "config": usage_tracker.config
        }
        
    except Exception as e:
        logger.error(f"Failed to update config: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update config: {str(e)}")


@router.delete("/cleanup")
async def cleanup_old_usage_data(
    background_tasks: BackgroundTasks,
    days_to_keep: int = Query(365, description="Number of days of data to keep"),
    current_user: dict = Depends(get_current_user)
):
    """Clean up old usage data."""
    try:
        background_tasks.add_task(usage_tracker.cleanup_old_data, days_to_keep)
        
        return {
            "success": True,
            "message": f"Cleanup scheduled to keep {days_to_keep} days of data"
        }
        
    except Exception as e:
        logger.error(f"Failed to schedule cleanup: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to schedule cleanup: {str(e)}")


async def cleanup_export_file(file_path: str, delay_seconds: int = 3600):
    """Background task to cleanup export files."""
    import asyncio
    import os
    
    await asyncio.sleep(delay_seconds)
    
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Cleaned up export file: {file_path}")
    except Exception as e:
        logger.error(f"Failed to cleanup export file {file_path}: {e}")