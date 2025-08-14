"""
API router for chat functionality with Claude Code instances.
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, status, Query

from models.chat import ChatRequest, ChatResponse, ChatHistory, ChatMessage
from services.instance_service import InstanceService
from services.chat_service import ChatService
from auth import get_current_user_optional

logger = logging.getLogger(__name__)

router = APIRouter()

# Global services
async def get_instance_service() -> InstanceService:
    """Dependency to get instance service."""
    from main import instance_service
    return instance_service

chat_service = ChatService()


@router.post("/send", response_model=ChatResponse)
async def send_message(
    chat_request: ChatRequest,
    instance_service: InstanceService = Depends(get_instance_service),
    current_user: dict = Depends(get_current_user_optional)
):
    """Send a message to a Claude Code instance."""
    try:
        # Get the target instance
        instance = await instance_service.get_instance(chat_request.instance_id)
        if not instance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Instance {chat_request.instance_id} not found"
            )
        
        # Send the message
        response = await chat_service.send_message(instance, chat_request)
        
        logger.info(f"Sent message to instance {chat_request.instance_id}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending message to {chat_request.instance_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send message"
        )


@router.get("/history/{instance_id}", response_model=ChatHistory)
async def get_chat_history(
    instance_id: str,
    limit: Optional[int] = Query(None, description="Limit number of messages returned"),
    instance_service: InstanceService = Depends(get_instance_service),
    current_user: dict = Depends(get_current_user_optional)
):
    """Get chat history for a specific instance."""
    try:
        # Verify instance exists
        instance = await instance_service.get_instance(instance_id)
        if not instance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Instance {instance_id} not found"
            )
        
        # Get chat history
        history = await chat_service.get_chat_history(instance_id, limit)
        return history
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting chat history for {instance_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get chat history"
        )


@router.delete("/history/{instance_id}")
async def clear_chat_history(
    instance_id: str,
    instance_service: InstanceService = Depends(get_instance_service),
    current_user: dict = Depends(get_current_user_optional)
):
    """Clear chat history for a specific instance."""
    try:
        # Verify instance exists
        instance = await instance_service.get_instance(instance_id)
        if not instance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Instance {instance_id} not found"
            )
        
        # Clear chat history
        success = await chat_service.clear_chat_history(instance_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to clear chat history"
            )
        
        logger.info(f"Cleared chat history for instance {instance_id}")
        return {"message": f"Chat history cleared for instance {instance_id}"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error clearing chat history for {instance_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to clear chat history"
        )


@router.get("/messages/{instance_id}/recent", response_model=List[ChatMessage])
async def get_recent_messages(
    instance_id: str,
    count: int = Query(10, description="Number of recent messages to return"),
    instance_service: InstanceService = Depends(get_instance_service),
    current_user: dict = Depends(get_current_user_optional)
):
    """Get recent messages for a specific instance."""
    try:
        # Verify instance exists
        instance = await instance_service.get_instance(instance_id)
        if not instance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Instance {instance_id} not found"
            )
        
        # Get recent messages
        messages = await chat_service.get_recent_messages(instance_id, count)
        return messages
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting recent messages for {instance_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get recent messages"
        )


@router.get("/messages/{instance_id}/search", response_model=List[ChatMessage])
async def search_messages(
    instance_id: str,
    query: str = Query(..., description="Search query"),
    instance_service: InstanceService = Depends(get_instance_service),
    current_user: dict = Depends(get_current_user_optional)
):
    """Search messages in chat history for a specific instance."""
    try:
        # Verify instance exists
        instance = await instance_service.get_instance(instance_id)
        if not instance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Instance {instance_id} not found"
            )
        
        # Search messages
        messages = await chat_service.search_messages(instance_id, query)
        return messages
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching messages for {instance_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search messages"
        )


@router.get("/stats/{instance_id}")
async def get_chat_statistics(
    instance_id: str,
    instance_service: InstanceService = Depends(get_instance_service),
    current_user: dict = Depends(get_current_user_optional)
):
    """Get chat statistics for a specific instance."""
    try:
        # Verify instance exists
        instance = await instance_service.get_instance(instance_id)
        if not instance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Instance {instance_id} not found"
            )
        
        # Get chat statistics
        stats = await chat_service.get_chat_statistics(instance_id)
        return stats
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting chat statistics for {instance_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get chat statistics"
        )


@router.get("/export/{instance_id}")
async def export_chat_history(
    instance_id: str,
    format: str = Query("json", description="Export format (json or txt)"),
    instance_service: InstanceService = Depends(get_instance_service),
    current_user: dict = Depends(get_current_user_optional)
):
    """Export chat history for a specific instance."""
    try:
        # Verify instance exists
        instance = await instance_service.get_instance(instance_id)
        if not instance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Instance {instance_id} not found"
            )
        
        # Validate format
        if format not in ["json", "txt"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid format. Supported formats: json, txt"
            )
        
        # Export chat history
        exported_data = await chat_service.export_chat_history(instance_id, format)
        
        # Determine content type
        content_type = "application/json" if format == "json" else "text/plain"
        
        from fastapi.responses import Response
        return Response(
            content=exported_data,
            media_type=content_type,
            headers={
                "Content-Disposition": f"attachment; filename=chat_history_{instance_id}.{format}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting chat history for {instance_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export chat history"
        )