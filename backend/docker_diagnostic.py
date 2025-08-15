#!/usr/bin/env python3
"""
Docker Diagnostic Script for Claude Code Dashboard

Run this script to diagnose Docker connectivity issues and test different connection methods.
"""

import os
import sys
import docker
from docker.errors import DockerException, APIError
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_docker_connection():
    """Test Docker connection with various methods."""
    print("=" * 60)
    print("CLAUDE CODE DASHBOARD - DOCKER DIAGNOSTIC")
    print("=" * 60)
    
    # Check if Docker Desktop is running
    print("\n1. CHECKING DOCKER DESKTOP STATUS")
    print("-" * 40)
    
    import subprocess
    try:
        result = subprocess.run(['docker', 'version'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Docker CLI is accessible")
            print(f"Docker CLI output:\n{result.stdout}")
        else:
            print("❌ Docker CLI not accessible")
            print(f"Error: {result.stderr}")
    except subprocess.TimeoutExpired:
        print("❌ Docker CLI command timed out")
    except FileNotFoundError:
        print("❌ Docker CLI not found in PATH")
    except Exception as e:
        print(f"❌ Error running Docker CLI: {e}")
    
    # Test Python docker library connections
    print("\n2. TESTING PYTHON DOCKER CONNECTIONS")
    print("-" * 40)
    
    connection_methods = [
        ("Default (from_env)", lambda: docker.from_env()),
        ("Windows Named Pipe", lambda: docker.DockerClient(base_url='npipe:////./pipe/docker_engine')),
        ("TCP localhost:2375", lambda: docker.DockerClient(base_url='tcp://localhost:2375')),
        ("TCP localhost:2376 (TLS)", lambda: docker.DockerClient(base_url='tcp://localhost:2376', tls=True)),
        ("Unix Socket", lambda: docker.DockerClient(base_url='unix://var/run/docker.sock')),
    ]
    
    working_clients = []
    
    for method_name, method_func in connection_methods:
        try:
            print(f"\nTesting: {method_name}")
            client = method_func()
            
            # Test ping
            ping_result = client.ping()
            print(f"  ✅ Connection successful - Ping: {ping_result}")
            
            # Test basic operations
            version = client.version()
            print(f"  ✅ Docker Engine Version: {version.get('Version', 'Unknown')}")
            
            # Test container listing
            containers = client.containers.list(all=True)
            print(f"  ✅ Found {len(containers)} containers")
            
            working_clients.append((method_name, client))
            
        except Exception as e:
            print(f"  ❌ Failed: {str(e)}")
    
    # Test Docker environment variables
    print("\n3. CHECKING ENVIRONMENT VARIABLES")
    print("-" * 40)
    
    docker_env_vars = [
        'DOCKER_HOST',
        'DOCKER_TLS_VERIFY',
        'DOCKER_CERT_PATH',
        'DOCKER_MACHINE_NAME',
        'DOCKER_CONTEXT'
    ]
    
    for var in docker_env_vars:
        value = os.environ.get(var)
        if value:
            print(f"  {var} = {value}")
        else:
            print(f"  {var} = (not set)")
    
    # If we have working clients, test Claude container detection
    if working_clients:
        print("\n4. TESTING CLAUDE CONTAINER DETECTION")
        print("-" * 40)
        
        client = working_clients[0][1]  # Use first working client
        
        try:
            containers = client.containers.list(all=True)
            print(f"All containers ({len(containers)}):")
            
            claude_containers = []
            
            for container in containers:
                print(f"\n  Container: {container.name}")
                print(f"    ID: {container.short_id}")
                print(f"    Status: {container.status}")
                print(f"    Image: {getattr(container.image, 'tags', ['unknown'])[0] if container.image.tags else 'unknown'}")
                
                # Check if it looks like Claude
                is_claude = _is_claude_container(container)
                print(f"    Appears to be Claude: {is_claude}")
                
                if is_claude:
                    claude_containers.append(container)
                
                # Show ports
                ports = container.attrs.get('NetworkSettings', {}).get('Ports', {})
                if ports:
                    print(f"    Ports: {ports}")
            
            print(f"\n  Found {len(claude_containers)} potential Claude containers")
            
        except Exception as e:
            print(f"  ❌ Error testing container detection: {e}")
    
    # Show recommendations
    print("\n5. RECOMMENDATIONS")
    print("-" * 40)
    
    if not working_clients:
        print("❌ No Docker connections working. Please check:")
        print("  1. Docker Desktop is running")
        print("  2. Your user has Docker permissions")
        print("  3. Windows: Try running as administrator")
        print("  4. Linux: Add your user to 'docker' group")
    else:
        print(f"✅ Found {len(working_clients)} working connection(s):")
        for method_name, _ in working_clients:
            print(f"  - {method_name}")
        print("\nThe Claude Code Dashboard should be able to connect to Docker.")
    
    print(f"\n{'=' * 60}")


def _is_claude_container(container) -> bool:
    """Check if container appears to be Claude Code (simplified version)."""
    try:
        # Check container name
        name = container.name.lower()
        if any(keyword in name for keyword in ['claude', 'anthropic', 'claude-code']):
            return True
        
        # Check image name
        image_tags = getattr(container.image, 'tags', [])
        for tag in image_tags:
            tag_lower = tag.lower()
            if any(keyword in tag_lower for keyword in ['claude', 'anthropic']):
                return True
        
        # Check for common ports
        ports = container.attrs.get('NetworkSettings', {}).get('Ports', {})
        for port_spec in ports.keys():
            port = port_spec.split('/')[0]
            if port in ['8000', '8080', '3000', '5000']:
                return True
        
        return False
        
    except Exception:
        return False


if __name__ == "__main__":
    test_docker_connection()