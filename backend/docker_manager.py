"""
Docker manager for discovering and managing Claude Code containers.
"""

import logging
import subprocess
import json
import os
from typing import List, Dict, Any, Optional
import docker
from docker.errors import DockerException, APIError, NotFound

from models.instance import Instance, InstanceType, InstanceStatus

logger = logging.getLogger(__name__)


class DockerManager:
    """Manager for Docker operations and Claude Code container discovery."""
    
    def __init__(self):
        """Initialize Docker manager."""
        self.client: Optional[docker.DockerClient] = None
        self.use_cli_fallback = False
        self._connect()
    
    def _connect(self) -> bool:
        """
        Connect to Docker daemon with Windows Docker Desktop support.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Try multiple connection methods for Windows Docker Desktop
            connection_methods = [
                # Default connection (works on Linux and some Windows setups)
                lambda: docker.from_env(),
                # Windows Docker Desktop named pipe
                lambda: docker.DockerClient(base_url='npipe:////./pipe/docker_engine'),
                # Windows Docker Desktop TCP (if enabled)
                lambda: docker.DockerClient(base_url='tcp://localhost:2375'),
                # Windows Docker Desktop TCP with TLS (if enabled)
                lambda: docker.DockerClient(base_url='tcp://localhost:2376', tls=True),
            ]
            
            for i, method in enumerate(connection_methods):
                try:
                    self.client = method()
                    # Test connection
                    self.client.ping()
                    logger.info(f"Successfully connected to Docker daemon (method {i+1})")
                    return True
                except Exception as e:
                    logger.debug(f"Connection method {i+1} failed: {e}")
                    continue
            
            # If all methods fail, try CLI fallback
            logger.warning("Failed to connect to Docker daemon with Python library, trying CLI fallback")
            if self._test_docker_cli():
                logger.info("Docker CLI is available, using CLI fallback mode")
                self.use_cli_fallback = True
                return True
            else:
                logger.warning("Docker CLI also not available")
                self.client = None
                return False
            
        except Exception as e:
            logger.error(f"Unexpected error connecting to Docker: {e}")
            self.client = None
            return False
    
    def _test_docker_cli(self) -> bool:
        """Test if Docker CLI is available."""
        try:
            result = subprocess.run(['docker', 'version'], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except Exception:
            return False
    
    def is_available(self) -> bool:
        """Check if Docker is available and connected."""
        if self.use_cli_fallback:
            return self._test_docker_cli()
        
        if self.client is None:
            return False
        
        # Test if connection is still alive
        try:
            self.client.ping()
            return True
        except Exception:
            # Connection lost, try to reconnect
            logger.info("Docker connection lost, attempting to reconnect...")
            return self._connect()
    
    def retry_connection(self) -> bool:
        """Manually retry Docker connection."""
        logger.info("Manually retrying Docker connection...")
        return self._connect()
    
    async def discover_claude_containers(self) -> List[Instance]:
        """
        Discover running containers that might be Claude Code instances.
        
        Returns:
            List of discovered instances
        """
        if not self.is_available():
            logger.warning("Docker not available for container discovery")
            return []
        
        if self.use_cli_fallback:
            return await self._discover_claude_containers_cli()
        
        instances = []
        
        try:
            # Get all running containers
            containers = self.client.containers.list(all=False)
            
            for container in containers:
                # Look for containers that might be Claude Code instances
                if self._is_claude_container(container):
                    instance = await self._container_to_instance(container)
                    if instance:
                        instances.append(instance)
            
            logger.info(f"Discovered {len(instances)} Claude Code containers")
            return instances
            
        except APIError as e:
            logger.error(f"Docker API error during discovery: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error during container discovery: {e}")
            return []
    
    async def _discover_claude_containers_cli(self) -> List[Instance]:
        """Discover Claude containers using Docker CLI."""
        instances = []
        
        try:
            # Get all containers via CLI
            result = subprocess.run(
                ['docker', 'ps', '--all', '--format', 'json'],
                capture_output=True, text=True, timeout=30
            )
            
            if result.returncode != 0:
                logger.error(f"Docker CLI ps failed: {result.stderr}")
                return []
            
            # Parse container data
            for line in result.stdout.strip().split('\n'):
                if not line.strip():
                    continue
                    
                try:
                    container_data = json.loads(line)
                    if self._is_claude_container_cli(container_data):
                        instance = await self._container_data_to_instance(container_data)
                        if instance:
                            instances.append(instance)
                            
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse container JSON: {e}")
                except Exception as e:
                    logger.error(f"Error processing container data: {e}")
            
            logger.info(f"Discovered {len(instances)} Claude Code containers via CLI")
            return instances
            
        except subprocess.TimeoutExpired:
            logger.error("Docker CLI command timed out")
            return []
        except Exception as e:
            logger.error(f"Error discovering containers via CLI: {e}")
            return []
    
    def _is_claude_container(self, container) -> bool:
        """
        Determine if a container is likely a Claude Code instance.
        
        Args:
            container: Docker container object
            
        Returns:
            True if container appears to be Claude Code
        """
        try:
            # Check container name for Claude-related keywords
            name = container.name.lower()
            if any(keyword in name for keyword in ['claude', 'anthropic', 'claude-code']):
                return True
            
            # Check image name
            image_tags = getattr(container.image, 'tags', [])
            for tag in image_tags:
                tag_lower = tag.lower()
                if any(keyword in tag_lower for keyword in ['claude', 'anthropic']):
                    return True
            
            # Check for exposed ports that Claude Code typically uses
            ports = container.attrs.get('NetworkSettings', {}).get('Ports', {})
            for port_spec in ports.keys():
                port = port_spec.split('/')[0]
                if port in ['8000', '8080', '3000', '5000']:  # Common Claude Code ports
                    return True
            
            # Check environment variables
            env_vars = container.attrs.get('Config', {}).get('Env', [])
            for env_var in env_vars:
                if any(keyword in env_var.lower() for keyword in ['claude', 'anthropic']):
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking if container is Claude instance: {e}")
            return False
    
    def _is_claude_container_cli(self, container_data: Dict[str, Any]) -> bool:
        """
        Determine if a container is likely a Claude Code instance (CLI version).
        
        Args:
            container_data: Container data from Docker CLI JSON
            
        Returns:
            True if container appears to be Claude Code
        """
        try:
            # Check container name
            name = container_data.get('Names', '').lower()
            if any(keyword in name for keyword in ['claude', 'anthropic', 'claude-code']):
                return True
            
            # Check image name
            image = container_data.get('Image', '').lower()
            if any(keyword in image for keyword in ['claude', 'anthropic']):
                return True
            
            # Check for exposed ports that Claude Code typically uses
            ports = container_data.get('Ports', '')
            if any(port in ports for port in ['8000', '8080', '3000', '5000']):
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking if container is Claude instance (CLI): {e}")
            return False
    
    async def _container_data_to_instance(self, container_data: Dict[str, Any]) -> Optional[Instance]:
        """
        Convert Docker CLI container data to Instance model.
        
        Args:
            container_data: Container data from Docker CLI JSON
            
        Returns:
            Instance object or None if conversion fails
        """
        try:
            # Extract basic info
            container_id = container_data.get('ID', '')
            name = container_data.get('Names', 'unknown')
            image = container_data.get('Image', 'unknown')
            status = container_data.get('State', 'unknown')
            ports = container_data.get('Ports', '')
            
            # Parse ports to find host mapping
            host_port = None
            
            # Ports format: "0.0.0.0:8000->8000/tcp"
            for port_mapping in ports.split(', '):
                if '->' in port_mapping and '8000' in port_mapping:
                    # Extract host port
                    try:
                        host_part = port_mapping.split('->')[0]
                        if ':' in host_part:
                            host_port = int(host_part.split(':')[-1])
                            break
                    except (ValueError, IndexError):
                        continue
            
            # If no port 8000, try any port
            if not host_port:
                for port_mapping in ports.split(', '):
                    if '->' in port_mapping:
                        try:
                            host_part = port_mapping.split('->')[0]
                            if ':' in host_part:
                                host_port = int(host_part.split(':')[-1])
                                break
                        except (ValueError, IndexError):
                            continue
            
            if not host_port:
                logger.warning(f"No suitable port found for container {name}")
                return None
            
            # Create instance
            instance = Instance(
                id=f"docker_{container_id[:12]}",
                name=f"{name} (Docker)",
                type=InstanceType.DOCKER,
                host="localhost",
                port=host_port,
                container_id=container_id,
                status=InstanceStatus.ONLINE if status == 'running' else InstanceStatus.OFFLINE,
                metadata={
                    "container_name": name,
                    "image": image,
                    "status": status,
                    "ports": ports,
                    "discovery_method": "cli"
                }
            )
            
            return instance
            
        except Exception as e:
            logger.error(f"Error converting container data to instance: {e}")
            return None
    
    async def _container_to_instance(self, container) -> Optional[Instance]:
        """
        Convert Docker container to Instance model.
        
        Args:
            container: Docker container object
            
        Returns:
            Instance object or None if conversion fails
        """
        try:
            # Get container details
            container.reload()
            
            # Extract network information
            ports = container.attrs.get('NetworkSettings', {}).get('Ports', {})
            
            # Find the first exposed port (prefer 8000, then others)
            exposed_port = None
            host_port = None
            
            for port_spec, port_bindings in ports.items():
                if port_bindings:  # Only consider ports with host bindings
                    container_port = port_spec.split('/')[0]
                    host_binding = port_bindings[0]
                    
                    if container_port == '8000':  # Prefer port 8000
                        exposed_port = container_port
                        host_port = host_binding.get('HostPort')
                        break
                    elif not exposed_port:  # Take first available port
                        exposed_port = container_port
                        host_port = host_binding.get('HostPort')
            
            if not exposed_port or not host_port:
                logger.warning(f"No suitable port found for container {container.name}")
                return None
            
            # Create instance
            instance = Instance(
                id=f"docker_{container.short_id}",
                name=f"{container.name} (Docker)",
                type=InstanceType.DOCKER,
                host="localhost",  # Assuming local Docker
                port=int(host_port),
                container_id=container.id,
                status=InstanceStatus.ONLINE if container.status == 'running' else InstanceStatus.OFFLINE,
                metadata={
                    "container_name": container.name,
                    "image": str(container.image.tags[0]) if container.image.tags else "unknown",
                    "status": container.status,
                    "created": container.attrs.get('Created'),
                    "ports": ports
                }
            )
            
            return instance
            
        except Exception as e:
            logger.error(f"Error converting container {container.name} to instance: {e}")
            return None
    
    async def get_container_info(self, container_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific container.
        
        Args:
            container_id: Container ID
            
        Returns:
            Container information
        """
        if not self.is_available():
            return {"error": "Docker not available"}
        
        try:
            container = self.client.containers.get(container_id)
            container.reload()
            
            return {
                "id": container.id,
                "short_id": container.short_id,
                "name": container.name,
                "status": container.status,
                "image": str(container.image.tags[0]) if container.image.tags else "unknown",
                "created": container.attrs.get('Created'),
                "ports": container.attrs.get('NetworkSettings', {}).get('Ports', {}),
                "environment": container.attrs.get('Config', {}).get('Env', []),
                "labels": container.labels
            }
            
        except NotFound:
            return {"error": f"Container {container_id} not found"}
        except APIError as e:
            return {"error": f"Docker API error: {e}"}
        except Exception as e:
            logger.error(f"Error getting container info: {e}")
            return {"error": str(e)}
    
    async def start_container(self, container_id: str) -> Dict[str, Any]:
        """
        Start a stopped container.
        
        Args:
            container_id: Container ID to start
            
        Returns:
            Operation result
        """
        if not self.is_available():
            return {"success": False, "error": "Docker not available"}
        
        try:
            container = self.client.containers.get(container_id)
            container.start()
            
            return {
                "success": True,
                "message": f"Container {container.name} started successfully"
            }
            
        except NotFound:
            return {"success": False, "error": f"Container {container_id} not found"}
        except APIError as e:
            return {"success": False, "error": f"Docker API error: {e}"}
        except Exception as e:
            logger.error(f"Error starting container: {e}")
            return {"success": False, "error": str(e)}
    
    async def stop_container(self, container_id: str) -> Dict[str, Any]:
        """
        Stop a running container.
        
        Args:
            container_id: Container ID to stop
            
        Returns:
            Operation result
        """
        if not self.is_available():
            return {"success": False, "error": "Docker not available"}
        
        try:
            container = self.client.containers.get(container_id)
            container.stop(timeout=10)
            
            return {
                "success": True,
                "message": f"Container {container.name} stopped successfully"
            }
            
        except NotFound:
            return {"success": False, "error": f"Container {container_id} not found"}
        except APIError as e:
            return {"success": False, "error": f"Docker API error: {e}"}
        except Exception as e:
            logger.error(f"Error stopping container: {e}")
            return {"success": False, "error": str(e)}
    
    async def list_all_containers(self) -> List[Dict[str, Any]]:
        """
        List all containers (running and stopped).
        
        Returns:
            List of container information
        """
        if not self.is_available():
            return []
        
        if self.use_cli_fallback:
            return await self._list_containers_cli()
        
        try:
            containers = self.client.containers.list(all=True)
            
            container_list = []
            for container in containers:
                container_list.append({
                    "id": container.id,
                    "short_id": container.short_id,
                    "name": container.name,
                    "status": container.status,
                    "image": str(container.image.tags[0]) if container.image.tags else "unknown",
                    "is_claude": self._is_claude_container(container)
                })
            
            return container_list
            
        except APIError as e:
            logger.error(f"Docker API error listing containers: {e}")
            return []
        except Exception as e:
            logger.error(f"Error listing containers: {e}")
            return []
    
    async def _list_containers_cli(self) -> List[Dict[str, Any]]:
        """List all containers using Docker CLI."""
        try:
            result = subprocess.run(
                ['docker', 'ps', '--all', '--format', 'json'],
                capture_output=True, text=True, timeout=30
            )
            
            if result.returncode != 0:
                logger.error(f"Docker CLI ps failed: {result.stderr}")
                return []
            
            container_list = []
            for line in result.stdout.strip().split('\n'):
                if not line.strip():
                    continue
                    
                try:
                    container_data = json.loads(line)
                    container_list.append({
                        "id": container_data.get('ID', ''),
                        "short_id": container_data.get('ID', '')[:12],
                        "name": container_data.get('Names', 'unknown'),
                        "status": container_data.get('State', 'unknown'),
                        "image": container_data.get('Image', 'unknown'),
                        "is_claude": self._is_claude_container_cli(container_data)
                    })
                    
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse container JSON: {e}")
                except Exception as e:
                    logger.error(f"Error processing container data: {e}")
            
            return container_list
            
        except subprocess.TimeoutExpired:
            logger.error("Docker CLI command timed out")
            return []
        except Exception as e:
            logger.error(f"Error listing containers via CLI: {e}")
            return []