"""
API router for Claude Code instance management.
"""

import logging
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, status

from models.instance import Instance, InstanceCreate, InstanceUpdate, InstanceHealth
from services.instance_service import InstanceService
from auth import get_current_user_optional

logger = logging.getLogger(__name__)

router = APIRouter()

# Global instance service (injected from main.py)
async def get_instance_service() -> InstanceService:
    """Dependency to get instance service."""
    from main import instance_service
    return instance_service


@router.get("/", response_model=List[Instance])
async def get_instances(
    service: InstanceService = Depends(get_instance_service),
    current_user: dict = Depends(get_current_user_optional)
):
    """Get all Claude Code instances."""
    try:
        instances = await service.get_all_instances()
        logger.info(f"Retrieved {len(instances)} instances")
        return instances
    except Exception as e:
        logger.error(f"Error retrieving instances: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve instances"
        )


@router.get("/{instance_id}", response_model=Instance)
async def get_instance(
    instance_id: str,
    service: InstanceService = Depends(get_instance_service),
    current_user: dict = Depends(get_current_user_optional)
):
    """Get a specific Claude Code instance by ID."""
    try:
        instance = await service.get_instance(instance_id)
        if not instance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Instance {instance_id} not found"
            )
        return instance
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving instance {instance_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve instance"
        )


@router.post("/", response_model=Instance, status_code=status.HTTP_201_CREATED)
async def create_instance(
    instance_create: InstanceCreate,
    service: InstanceService = Depends(get_instance_service),
    current_user: dict = Depends(get_current_user_optional)
):
    """Create a new Claude Code instance."""
    try:
        instance = await service.create_instance(instance_create)
        logger.info(f"Created instance: {instance.name} ({instance.id})")
        return instance
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating instance: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create instance"
        )


@router.put("/{instance_id}", response_model=Instance)
async def update_instance(
    instance_id: str,
    instance_update: InstanceUpdate,
    service: InstanceService = Depends(get_instance_service),
    current_user: dict = Depends(get_current_user_optional)
):
    """Update an existing Claude Code instance."""
    try:
        instance = await service.update_instance(instance_id, instance_update)
        if not instance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Instance {instance_id} not found"
            )
        logger.info(f"Updated instance: {instance.name} ({instance.id})")
        return instance
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating instance {instance_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update instance"
        )


@router.delete("/{instance_id}")
async def delete_instance(
    instance_id: str,
    service: InstanceService = Depends(get_instance_service),
    current_user: dict = Depends(get_current_user_optional)
):
    """Delete a Claude Code instance."""
    try:
        success = await service.delete_instance(instance_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Instance {instance_id} not found"
            )
        logger.info(f"Deleted instance: {instance_id}")
        return {"message": f"Instance {instance_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting instance {instance_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete instance"
        )


@router.post("/{instance_id}/health", response_model=InstanceHealth)
async def check_instance_health(
    instance_id: str,
    service: InstanceService = Depends(get_instance_service),
    current_user: dict = Depends(get_current_user_optional)
):
    """Check health of a specific Claude Code instance."""
    try:
        instance = await service.get_instance(instance_id)
        if not instance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Instance {instance_id} not found"
            )
        
        health_result = await service.check_instance_health(instance)
        
        health_response = InstanceHealth(
            instance_id=instance_id,
            status=health_result["status"],
            response_time_ms=health_result.get("response_time_ms"),
            error_message=health_result.get("error")
        )
        
        return health_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking health for instance {instance_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check instance health"
        )


@router.post("/health/all")
async def check_all_instances_health(
    service: InstanceService = Depends(get_instance_service),
    current_user: dict = Depends(get_current_user_optional)
):
    """Check health of all Claude Code instances."""
    try:
        health_results = await service.check_all_instances_health()
        
        health_responses = []
        for instance_id, result in health_results.items():
            health_responses.append(InstanceHealth(
                instance_id=instance_id,
                status=result["status"],
                response_time_ms=result.get("response_time_ms"),
                error_message=result.get("error")
            ))
        
        return health_responses
        
    except Exception as e:
        logger.error(f"Error checking health for all instances: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check instances health"
        )


@router.post("/discover/docker")
async def discover_docker_instances(
    service: InstanceService = Depends(get_instance_service),
    current_user: dict = Depends(get_current_user_optional)
):
    """Discover Docker containers running Claude Code."""
    try:
        discovered = await service.discover_docker_instances()
        logger.info(f"Discovered {len(discovered)} Docker instances")
        return {
            "discovered_count": len(discovered),
            "instances": discovered
        }
    except Exception as e:
        logger.error(f"Error discovering Docker instances: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to discover Docker instances"
        )


@router.post("/refresh/docker")
async def refresh_docker_instances(
    service: InstanceService = Depends(get_instance_service),
    current_user: dict = Depends(get_current_user_optional)
):
    """Refresh Docker instances by re-discovering containers."""
    try:
        refreshed = await service.refresh_docker_instances()
        logger.info(f"Refreshed Docker instances, found {len(refreshed)}")
        return {
            "refreshed_count": len(refreshed),
            "instances": refreshed
        }
    except Exception as e:
        logger.error(f"Error refreshing Docker instances: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to refresh Docker instances"
        )


@router.get("/stats/summary")
async def get_instance_stats(
    service: InstanceService = Depends(get_instance_service),
    current_user: dict = Depends(get_current_user_optional)
):
    """Get statistics about all instances."""
    try:
        stats = await service.get_instance_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting instance stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get instance statistics"
        )