"""
API router for Docker container management.
"""

import logging
import os
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, status

from auth import get_current_user_optional

logger = logging.getLogger(__name__)

router = APIRouter()

# Global Docker manager will be set by main.py
docker_manager = None

def set_docker_manager(manager):
    global docker_manager
    docker_manager = manager

def get_docker_manager():
    return docker_manager


@router.get("/status")
async def get_docker_status(current_user: dict = Depends(get_current_user_optional)):
    """Get Docker daemon status."""
    try:
        from docker_manager import DockerManager
        test_mgr = DockerManager()
        is_available = test_mgr.is_available()
        
        return {
            "available": is_available,
            "status": "connected" if is_available else "disconnected", 
            "platform": "windows" if os.name == 'nt' else "linux"
        }
    except Exception as e:
        logger.error(f"Error checking Docker status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check Docker status: {str(e)}"
        )


@router.post("/reconnect")
async def reconnect_docker(
    current_user: dict = Depends(get_current_user_optional)
):
    """Retry Docker daemon connection."""
    try:
        success = get_docker_manager().retry_connection()
        if success:
            return {
                "success": True,
                "message": "Successfully reconnected to Docker daemon",
                "status": "connected"
            }
        else:
            return {
                "success": False,
                "message": "Failed to reconnect to Docker daemon",
                "status": "disconnected"
            }
    except Exception as e:
        logger.error(f"Error reconnecting to Docker: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reconnect to Docker"
        )


@router.get("/containers", response_model=List[Dict[str, Any]])
async def list_containers(
    current_user: dict = Depends(get_current_user_optional)
):
    """List all Docker containers."""
    try:
        if not get_docker_manager().is_available():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Docker is not available"
            )
        
        containers = await get_docker_manager().list_all_containers()
        return containers
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing containers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list containers"
        )


@router.get("/containers/claude")
async def discover_claude_containers(
    current_user: dict = Depends(get_current_user_optional)
):
    """Discover containers that might be running Claude Code."""
    try:
        if not get_docker_manager().is_available():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Docker is not available"
            )
        
        instances = await get_docker_manager().discover_claude_containers()
        return {
            "discovered_count": len(instances),
            "instances": instances
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error discovering Claude containers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to discover Claude containers"
        )


@router.get("/containers/{container_id}")
async def get_container_info(
    container_id: str,
    current_user: dict = Depends(get_current_user_optional)
):
    """Get detailed information about a specific container."""
    try:
        if not get_docker_manager().is_available():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Docker is not available"
            )
        
        container_info = await get_docker_manager().get_container_info(container_id)
        
        if "error" in container_info:
            if "not found" in container_info["error"].lower():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=container_info["error"]
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=container_info["error"]
                )
        
        return container_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting container info for {container_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get container information"
        )


@router.post("/containers/{container_id}/start")
async def start_container(
    container_id: str,
    current_user: dict = Depends(get_current_user_optional)
):
    """Start a stopped container."""
    try:
        if not get_docker_manager().is_available():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Docker is not available"
            )
        
        result = await get_docker_manager().start_container(container_id)
        
        if not result["success"]:
            if "not found" in result["error"].lower():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=result["error"]
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=result["error"]
                )
        
        logger.info(f"Started container {container_id}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting container {container_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start container"
        )


@router.post("/containers/{container_id}/stop")
async def stop_container(
    container_id: str,
    current_user: dict = Depends(get_current_user_optional)
):
    """Stop a running container."""
    try:
        if not get_docker_manager().is_available():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Docker is not available"
            )
        
        result = await get_docker_manager().stop_container(container_id)
        
        if not result["success"]:
            if "not found" in result["error"].lower():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=result["error"]
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=result["error"]
                )
        
        logger.info(f"Stopped container {container_id}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error stopping container {container_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to stop container"
        )