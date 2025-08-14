"""
Service for managing chat functionality with Claude Code instances.
"""

import json
import logging
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

from models.chat import ChatMessage, ChatRequest, ChatResponse, ChatHistory, MessageRole, MessageStatus
from models.instance import Instance
from claude_client import ClaudeCodeClient

logger = logging.getLogger(__name__)

CHAT_HISTORY_DIR = "chat_history"


class ChatService:
    """Service for managing chat functionality."""
    
    def __init__(self):
        """Initialize the chat service."""
        self.chat_histories: Dict[str, ChatHistory] = {}
        self._ensure_history_dir()
    
    def _ensure_history_dir(self) -> None:
        """Ensure chat history directory exists."""
        os.makedirs(CHAT_HISTORY_DIR, exist_ok=True)
    
    def _get_history_file_path(self, instance_id: str) -> str:
        """Get file path for instance chat history."""
        return os.path.join(CHAT_HISTORY_DIR, f"{instance_id}.json")
    
    async def load_chat_history(self, instance_id: str) -> ChatHistory:
        """Load chat history for an instance."""
        if instance_id in self.chat_histories:
            return self.chat_histories[instance_id]
        
        history_file = self._get_history_file_path(instance_id)
        
        try:
            if os.path.exists(history_file):
                with open(history_file, 'r') as f:
                    data = json.load(f)
                    # Convert message data to ChatMessage objects
                    messages = [ChatMessage(**msg) for msg in data.get('messages', [])]
                    
                    history = ChatHistory(
                        instance_id=instance_id,
                        messages=messages,
                        created_at=datetime.fromisoformat(data.get('created_at', datetime.now().isoformat())),
                        updated_at=datetime.fromisoformat(data.get('updated_at', datetime.now().isoformat()))
                    )
            else:
                history = ChatHistory(instance_id=instance_id)
            
            self.chat_histories[instance_id] = history
            return history
            
        except Exception as e:
            logger.error(f"Error loading chat history for {instance_id}: {e}")
            history = ChatHistory(instance_id=instance_id)
            self.chat_histories[instance_id] = history
            return history
    
    async def save_chat_history(self, instance_id: str) -> None:
        """Save chat history for an instance."""
        if instance_id not in self.chat_histories:
            return
        
        history = self.chat_histories[instance_id]
        history.updated_at = datetime.now()
        
        history_file = self._get_history_file_path(instance_id)
        
        try:
            data = {
                'instance_id': history.instance_id,
                'messages': [msg.dict() for msg in history.messages],
                'created_at': history.created_at.isoformat(),
                'updated_at': history.updated_at.isoformat()
            }
            
            with open(history_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
                
        except Exception as e:
            logger.error(f"Error saving chat history for {instance_id}: {e}")
    
    async def send_message(self, instance: Instance, chat_request: ChatRequest) -> ChatResponse:
        """Send a message to a Claude Code instance."""
        # Load chat history
        history = await self.load_chat_history(instance.id)
        
        # Create user message
        user_message = ChatMessage(
            id=str(uuid.uuid4()),
            instance_id=instance.id,
            role=MessageRole.USER,
            content=chat_request.message,
            status=MessageStatus.SENT
        )
        
        # Add to history
        history.messages.append(user_message)
        
        try:
            # Send message to Claude Code instance
            async with ClaudeCodeClient() as client:
                # Prepare context from recent messages
                context = []
                if chat_request.context:
                    context = chat_request.context
                else:
                    # Use recent messages as context (last 10 messages)
                    recent_messages = history.messages[-10:] if len(history.messages) > 1 else []
                    for msg in recent_messages[:-1]:  # Exclude the current message
                        context.append({
                            "role": msg.role,
                            "content": msg.content
                        })
                
                response = await client.send_message(instance, chat_request.message, context)
                
                # Create assistant message
                assistant_message = ChatMessage(
                    id=response.message_id,
                    instance_id=instance.id,
                    role=MessageRole.ASSISTANT,
                    content=response.content,
                    status=MessageStatus.DELIVERED if not response.error else MessageStatus.ERROR,
                    metadata=response.metadata
                )
                
                # Add assistant response to history
                history.messages.append(assistant_message)
                
                # Update user message status
                user_message.status = MessageStatus.DELIVERED
                
                # Save history
                await self.save_chat_history(instance.id)
                
                return response
                
        except Exception as e:
            logger.error(f"Error sending message to {instance.id}: {e}")
            
            # Update user message status to error
            user_message.status = MessageStatus.ERROR
            user_message.metadata["error"] = str(e)
            
            # Save history with error
            await self.save_chat_history(instance.id)
            
            # Return error response
            return ChatResponse(
                message_id=str(uuid.uuid4()),
                instance_id=instance.id,
                content="",
                error=str(e)
            )
    
    async def get_chat_history(self, instance_id: str, limit: Optional[int] = None) -> ChatHistory:
        """Get chat history for an instance."""
        history = await self.load_chat_history(instance_id)
        
        if limit and len(history.messages) > limit:
            # Return limited history
            limited_messages = history.messages[-limit:]
            return ChatHistory(
                instance_id=instance_id,
                messages=limited_messages,
                created_at=history.created_at,
                updated_at=history.updated_at
            )
        
        return history
    
    async def clear_chat_history(self, instance_id: str) -> bool:
        """Clear chat history for an instance."""
        try:
            # Clear in-memory history
            if instance_id in self.chat_histories:
                self.chat_histories[instance_id].messages = []
                await self.save_chat_history(instance_id)
            
            # Remove history file
            history_file = self._get_history_file_path(instance_id)
            if os.path.exists(history_file):
                os.remove(history_file)
            
            logger.info(f"Cleared chat history for instance {instance_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing chat history for {instance_id}: {e}")
            return False
    
    async def get_recent_messages(self, instance_id: str, count: int = 10) -> List[ChatMessage]:
        """Get recent messages for an instance."""
        history = await self.load_chat_history(instance_id)
        return history.messages[-count:] if history.messages else []
    
    async def search_messages(self, instance_id: str, query: str) -> List[ChatMessage]:
        """Search messages in chat history."""
        history = await self.load_chat_history(instance_id)
        
        matching_messages = []
        query_lower = query.lower()
        
        for message in history.messages:
            if query_lower in message.content.lower():
                matching_messages.append(message)
        
        return matching_messages
    
    async def get_chat_statistics(self, instance_id: str) -> Dict[str, Any]:
        """Get chat statistics for an instance."""
        history = await self.load_chat_history(instance_id)
        
        total_messages = len(history.messages)
        user_messages = len([msg for msg in history.messages if msg.role == MessageRole.USER])
        assistant_messages = len([msg for msg in history.messages if msg.role == MessageRole.ASSISTANT])
        error_messages = len([msg for msg in history.messages if msg.status == MessageStatus.ERROR])
        
        return {
            "total_messages": total_messages,
            "user_messages": user_messages,
            "assistant_messages": assistant_messages,
            "error_messages": error_messages,
            "first_message": history.messages[0].timestamp.isoformat() if history.messages else None,
            "last_message": history.messages[-1].timestamp.isoformat() if history.messages else None,
            "created_at": history.created_at.isoformat(),
            "updated_at": history.updated_at.isoformat()
        }
    
    async def export_chat_history(self, instance_id: str, format: str = "json") -> str:
        """Export chat history in specified format."""
        history = await self.load_chat_history(instance_id)
        
        if format == "json":
            return json.dumps({
                "instance_id": instance_id,
                "messages": [msg.dict() for msg in history.messages],
                "exported_at": datetime.now().isoformat()
            }, indent=2, default=str)
        
        elif format == "txt":
            lines = [f"Chat History for Instance: {instance_id}", "=" * 50, ""]
            
            for message in history.messages:
                timestamp = message.timestamp.strftime("%Y-%m-%d %H:%M:%S")
                role = message.role.upper()
                lines.append(f"[{timestamp}] {role}: {message.content}")
                lines.append("")
            
            return "\n".join(lines)
        
        else:
            raise ValueError(f"Unsupported export format: {format}")