"""
Claude Code API client for communicating with Claude Code instances.
"""

import asyncio
import logging
import time
from typing import Optional, Dict, Any, AsyncGenerator
import aiohttp
from aiohttp import ClientTimeout, ClientError

from models.instance import Instance, InstanceStatus
from models.chat import ChatResponse

logger = logging.getLogger(__name__)


class ClaudeCodeClient:
    """Client for communicating with Claude Code instances."""
    
    def __init__(self, timeout: int = 30):
        """
        Initialize the Claude Code client.
        
        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = ClientTimeout(total=timeout)
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(timeout=self.timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def health_check(self, instance: Instance) -> Dict[str, Any]:
        """
        Perform health check on a Claude Code instance.
        
        Args:
            instance: The instance to check
            
        Returns:
            Health status information
        """
        start_time = time.time()
        
        try:
            if not self.session:
                self.session = aiohttp.ClientSession(timeout=self.timeout)
            
            # Try to ping the Claude Code instance health endpoint
            health_url = f"{instance.url}/health"
            
            async with self.session.get(health_url) as response:
                response_time = (time.time() - start_time) * 1000
                
                if response.status == 200:
                    data = await response.json()
                    return {
                        "status": InstanceStatus.ONLINE,
                        "response_time_ms": response_time,
                        "data": data
                    }
                else:
                    return {
                        "status": InstanceStatus.ERROR,
                        "response_time_ms": response_time,
                        "error": f"HTTP {response.status}: {response.reason}"
                    }
                    
        except asyncio.TimeoutError:
            response_time = (time.time() - start_time) * 1000
            return {
                "status": InstanceStatus.OFFLINE,
                "response_time_ms": response_time,
                "error": "Request timeout"
            }
            
        except ClientError as e:
            response_time = (time.time() - start_time) * 1000
            return {
                "status": InstanceStatus.ERROR,
                "response_time_ms": response_time,
                "error": str(e)
            }
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            logger.error(f"Unexpected error during health check for {instance.id}: {e}")
            return {
                "status": InstanceStatus.ERROR,
                "response_time_ms": response_time,
                "error": f"Unexpected error: {str(e)}"
            }
    
    async def send_message(
        self, 
        instance: Instance, 
        message: str, 
        context: Optional[list] = None
    ) -> ChatResponse:
        """
        Send a message to a Claude Code instance.
        
        Args:
            instance: Target instance
            message: Message to send
            context: Previous conversation context
            
        Returns:
            Response from Claude Code instance
        """
        start_time = time.time()
        
        try:
            if not self.session:
                self.session = aiohttp.ClientSession(timeout=self.timeout)
            
            # Prepare the request payload
            payload = {
                "message": message,
                "stream": False  # For now, disable streaming
            }
            
            if context:
                payload["context"] = context
            
            # Send the message to Claude Code instance
            chat_url = f"{instance.url}/chat"
            
            async with self.session.post(chat_url, json=payload) as response:
                response_time = (time.time() - start_time) * 1000
                
                if response.status == 200:
                    data = await response.json()
                    
                    return ChatResponse(
                        message_id=f"msg_{int(time.time())}_{instance.id}",
                        instance_id=instance.id,
                        content=data.get("content", data.get("response", "No response")),
                        response_time_ms=response_time,
                        metadata={"raw_response": data}
                    )
                else:
                    error_text = await response.text()
                    return ChatResponse(
                        message_id=f"err_{int(time.time())}_{instance.id}",
                        instance_id=instance.id,
                        content="",
                        response_time_ms=response_time,
                        error=f"HTTP {response.status}: {error_text}"
                    )
                    
        except asyncio.TimeoutError:
            response_time = (time.time() - start_time) * 1000
            return ChatResponse(
                message_id=f"err_{int(time.time())}_{instance.id}",
                instance_id=instance.id,
                content="",
                response_time_ms=response_time,
                error="Request timeout"
            )
            
        except ClientError as e:
            response_time = (time.time() - start_time) * 1000
            return ChatResponse(
                message_id=f"err_{int(time.time())}_{instance.id}",
                instance_id=instance.id,
                content="",
                response_time_ms=response_time,
                error=str(e)
            )
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            logger.error(f"Unexpected error sending message to {instance.id}: {e}")
            return ChatResponse(
                message_id=f"err_{int(time.time())}_{instance.id}",
                instance_id=instance.id,
                content="",
                response_time_ms=response_time,
                error=f"Unexpected error: {str(e)}"
            )
    
    async def send_message_stream(
        self, 
        instance: Instance, 
        message: str, 
        context: Optional[list] = None
    ) -> AsyncGenerator[str, None]:
        """
        Send a message to Claude Code instance with streaming response.
        
        Args:
            instance: Target instance
            message: Message to send
            context: Previous conversation context
            
        Yields:
            Streaming response chunks
        """
        try:
            if not self.session:
                self.session = aiohttp.ClientSession(timeout=self.timeout)
            
            payload = {
                "message": message,
                "stream": True
            }
            
            if context:
                payload["context"] = context
            
            chat_url = f"{instance.url}/chat"
            
            async with self.session.post(chat_url, json=payload) as response:
                if response.status == 200:
                    async for line in response.content:
                        if line:
                            yield line.decode('utf-8')
                else:
                    error_text = await response.text()
                    yield f"Error: HTTP {response.status}: {error_text}"
                    
        except Exception as e:
            logger.error(f"Error in streaming message to {instance.id}: {e}")
            yield f"Error: {str(e)}"
    
    async def get_instance_info(self, instance: Instance) -> Dict[str, Any]:
        """
        Get detailed information about a Claude Code instance.
        
        Args:
            instance: The instance to query
            
        Returns:
            Instance information
        """
        try:
            if not self.session:
                self.session = aiohttp.ClientSession(timeout=self.timeout)
            
            info_url = f"{instance.url}/info"
            
            async with self.session.get(info_url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": f"HTTP {response.status}: {response.reason}"}
                    
        except Exception as e:
            logger.error(f"Error getting info for {instance.id}: {e}")
            return {"error": str(e)}