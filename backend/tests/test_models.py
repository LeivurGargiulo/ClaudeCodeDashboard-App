"""
Tests for data models.
"""

import pytest
from pydantic import ValidationError

from models.instance import Instance, InstanceCreate, InstanceUpdate, InstanceType, InstanceStatus
from models.chat import ChatMessage, ChatResponse


def test_instance_model():
    """Test Instance model validation."""
    instance_data = {
        "id": "test-id",
        "name": "Test Instance",
        "type": InstanceType.LOCAL,
        "host": "localhost",
        "port": 8000
    }
    
    instance = Instance(**instance_data)
    assert instance.id == "test-id"
    assert instance.name == "Test Instance"
    assert instance.type == InstanceType.LOCAL
    assert instance.host == "localhost"
    assert instance.port == 8000


def test_instance_create_model():
    """Test InstanceCreate model validation."""
    create_data = {
        "name": "New Instance",
        "type": InstanceType.DOCKER,
        "host": "127.0.0.1",
        "port": 8080
    }
    
    instance_create = InstanceCreate(**create_data)
    assert instance_create.name == "New Instance"
    assert instance_create.type == InstanceType.DOCKER


def test_instance_model_validation():
    """Test Instance model field validation."""
    # Test invalid port
    with pytest.raises(ValidationError):
        Instance(
            id="test",
            name="Test",
            type=InstanceType.LOCAL,
            port=99999  # Invalid port
        )
    
    # Test empty name
    with pytest.raises(ValidationError):
        Instance(
            id="test",
            name="",  # Empty name
            type=InstanceType.LOCAL,
            port=8000
        )


def test_chat_message_model():
    """Test ChatMessage model."""
    message_data = {
        "instance_id": "test-instance",
        "message": "Hello Claude",
        "sender": "user"
    }
    
    chat_message = ChatMessage(**message_data)
    assert chat_message.instance_id == "test-instance"
    assert chat_message.message == "Hello Claude"
    assert chat_message.sender == "user"


def test_chat_response_model():
    """Test ChatResponse model."""
    response_data = {
        "success": True,
        "message": "Response sent successfully",
        "response": "Hello! How can I help?"
    }
    
    chat_response = ChatResponse(**response_data)
    assert chat_response.success is True
    assert chat_response.message == "Response sent successfully"
    assert chat_response.response == "Hello! How can I help?"