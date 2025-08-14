"""
Service for managing Claude Code instances.
"""

import json
import logging
import os
from typing import List, Optional, Dict, Any
from datetime import datetime

from models.instance import Instance, InstanceCreate, InstanceUpdate, InstanceType, InstanceStatus
from docker_manager import DockerManager
from claude_client import ClaudeCodeClient

logger = logging.getLogger(__name__)

INSTANCES_FILE = "instances.json"


class InstanceService:
    """Service for managing Claude Code instances."""
    
    def __init__(self):
        """Initialize the instance service."""
        self.instances: Dict[str, Instance] = {}
        self.docker_manager = DockerManager()
    
    async def load_instances(self) -> None:
        """Load instances from configuration file."""
        try:
            if os.path.exists(INSTANCES_FILE):
                with open(INSTANCES_FILE, 'r') as f:
                    data = json.load(f)
                    for instance_data in data.get('instances', []):
                        instance = Instance(**instance_data)
                        self.instances[instance.id] = instance
                logger.info(f"Loaded {len(self.instances)} instances from configuration")
        except Exception as e:
            logger.error(f"Error loading instances configuration: {e}")
    
    async def save_instances(self) -> None:
        """Save instances to configuration file."""
        try:
            data = {
                'instances': [instance.dict() for instance in self.instances.values()],
                'last_updated': datetime.now().isoformat()
            }
            with open(INSTANCES_FILE, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            logger.info(f"Saved {len(self.instances)} instances to configuration")
        except Exception as e:
            logger.error(f"Error saving instances configuration: {e}")
    
    async def discover_docker_instances(self) -> List[Instance]:
        """Discover Docker containers running Claude Code."""
        try:
            discovered = await self.docker_manager.discover_claude_containers()
            
            for instance in discovered:
                # Only add if not already exists
                if instance.id not in self.instances:
                    self.instances[instance.id] = instance
                    logger.info(f"Auto-discovered Docker instance: {instance.name}")
                else:
                    # Update container info for existing instances
                    existing = self.instances[instance.id]
                    existing.status = instance.status
                    existing.metadata.update(instance.metadata)
            
            return discovered
        except Exception as e:
            logger.error(f"Error discovering Docker instances: {e}")
            return []
    
    async def get_all_instances(self) -> List[Instance]:
        """Get all instances."""
        return list(self.instances.values())
    
    async def get_instance(self, instance_id: str) -> Optional[Instance]:
        """Get a specific instance by ID."""
        return self.instances.get(instance_id)
    
    async def create_instance(self, instance_create: InstanceCreate) -> Instance:
        """Create a new instance."""
        # Generate unique ID
        instance_id = f"{instance_create.type}_{instance_create.host}_{instance_create.port}"
        
        # Check if instance already exists
        if instance_id in self.instances:
            raise ValueError(f"Instance with ID {instance_id} already exists")
        
        # Create instance
        instance = Instance(
            id=instance_id,
            name=instance_create.name,
            type=instance_create.type,
            host=instance_create.host,
            port=instance_create.port,
            container_id=instance_create.container_id,
            metadata=instance_create.metadata
        )
        
        # Perform initial health check
        await self.check_instance_health(instance)
        
        # Add to instances
        self.instances[instance_id] = instance
        
        # Save configuration
        await self.save_instances()
        
        logger.info(f"Created new instance: {instance.name} ({instance_id})")
        return instance
    
    async def update_instance(self, instance_id: str, instance_update: InstanceUpdate) -> Optional[Instance]:
        """Update an existing instance."""
        instance = self.instances.get(instance_id)
        if not instance:
            return None
        
        # Update fields
        update_data = instance_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(instance, field, value)
        
        # Rebuild URL if host or port changed
        if 'host' in update_data or 'port' in update_data:
            protocol = "https" if instance.port == 443 else "http"
            instance.url = f"{protocol}://{instance.host}:{instance.port}"
        
        # Perform health check with updated info
        await self.check_instance_health(instance)
        
        # Save configuration
        await self.save_instances()
        
        logger.info(f"Updated instance: {instance.name} ({instance_id})")
        return instance
    
    async def delete_instance(self, instance_id: str) -> bool:
        """Delete an instance."""
        if instance_id in self.instances:
            instance = self.instances.pop(instance_id)
            await self.save_instances()
            logger.info(f"Deleted instance: {instance.name} ({instance_id})")
            return True
        return False
    
    async def check_instance_health(self, instance: Instance) -> Dict[str, Any]:
        """Check the health of a specific instance."""
        try:
            async with ClaudeCodeClient() as client:
                health_result = await client.health_check(instance)
                
                # Update instance status
                instance.status = health_result["status"]
                if health_result["status"] == InstanceStatus.ONLINE:
                    instance.last_seen = datetime.now()
                
                return health_result
                
        except Exception as e:
            logger.error(f"Error checking health for {instance.id}: {e}")
            instance.status = InstanceStatus.ERROR
            return {
                "status": InstanceStatus.ERROR,
                "error": str(e)
            }
    
    async def check_all_instances_health(self) -> Dict[str, Dict[str, Any]]:
        """Check health of all instances."""
        results = {}
        
        for instance_id, instance in self.instances.items():
            results[instance_id] = await self.check_instance_health(instance)
        
        # Save updated statuses
        await self.save_instances()
        
        return results
    
    async def get_instances_by_status(self, status: InstanceStatus) -> List[Instance]:
        """Get instances filtered by status."""
        return [instance for instance in self.instances.values() if instance.status == status]
    
    async def refresh_docker_instances(self) -> List[Instance]:
        """Refresh Docker instances by re-discovering containers."""
        # Remove existing Docker instances that are no longer running
        docker_instances = [inst for inst in self.instances.values() if inst.type == InstanceType.DOCKER]
        
        for instance in docker_instances:
            if instance.container_id:
                # Check if container still exists
                container_info = await self.docker_manager.get_container_info(instance.container_id)
                if "error" in container_info:
                    # Container no longer exists, remove instance
                    del self.instances[instance.id]
                    logger.info(f"Removed instance for non-existent container: {instance.name}")
        
        # Discover new containers
        return await self.discover_docker_instances()
    
    async def get_instance_stats(self) -> Dict[str, Any]:
        """Get statistics about instances."""
        total = len(self.instances)
        online = len([inst for inst in self.instances.values() if inst.status == InstanceStatus.ONLINE])
        offline = len([inst for inst in self.instances.values() if inst.status == InstanceStatus.OFFLINE])
        error = len([inst for inst in self.instances.values() if inst.status == InstanceStatus.ERROR])
        docker_count = len([inst for inst in self.instances.values() if inst.type == InstanceType.DOCKER])
        local_count = len([inst for inst in self.instances.values() if inst.type == InstanceType.LOCAL])
        
        return {
            "total": total,
            "online": online,
            "offline": offline,
            "error": error,
            "docker": docker_count,
            "local": local_count,
            "docker_available": self.docker_manager.is_available()
        }