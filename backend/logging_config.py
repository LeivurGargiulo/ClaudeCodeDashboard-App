"""
Comprehensive logging configuration for Claude Code Dashboard
"""

import logging
import logging.handlers
import os
import sys
import time
from pathlib import Path
from typing import Optional

import structlog
from structlog.stdlib import LoggerFactory


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = "claude_dashboard.log",
    enable_json_logs: bool = False,
    enable_structured_logs: bool = True
) -> None:
    """
    Set up comprehensive logging for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (None to disable file logging)
        enable_json_logs: Whether to output JSON-formatted logs
        enable_structured_logs: Whether to use structured logging
    """
    
    # Ensure logs directory exists
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure basic logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[]
    )
    
    # Create formatters
    if enable_json_logs:
        formatter = logging.Formatter(
            '{"timestamp":"%(asctime)s","logger":"%(name)s","level":"%(levelname)s","message":"%(message)s","module":"%(module)s","function":"%(funcName)s","line":%(lineno)d}'
        )
    else:
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)8s | %(name)s:%(lineno)d | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    
    # File handler with rotation
    if log_file:
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)  # Always debug level for file
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(console_handler)
    if log_file:
        root_logger.addHandler(file_handler)
    
    # Configure specific loggers
    configure_loggers(log_level)
    
    # Setup structured logging if enabled
    if enable_structured_logs:
        setup_structured_logging(enable_json_logs)


def configure_loggers(log_level: str) -> None:
    """Configure specific loggers with appropriate levels."""
    
    # Application loggers
    app_loggers = [
        "claude_dashboard",
        "claude_client",
        "docker_manager",
        "instance_service",
        "chat_service"
    ]
    
    for logger_name in app_loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(getattr(logging, log_level.upper()))
    
    # External library loggers
    external_loggers = {
        "uvicorn": "INFO",
        "uvicorn.access": "WARNING",
        "fastapi": "INFO",
        "aiohttp": "WARNING",
        "docker": "WARNING",
        "httpx": "WARNING",
        "asyncio": "WARNING"
    }
    
    for logger_name, level in external_loggers.items():
        logger = logging.getLogger(logger_name)
        logger.setLevel(getattr(logging, level))


def setup_structured_logging(json_format: bool = False) -> None:
    """Setup structured logging with structlog."""
    
    processors = [
        # Add log level
        structlog.stdlib.add_log_level,
        # Add logger name
        structlog.stdlib.add_logger_name,
        # Add timestamp
        structlog.processors.TimeStamper(fmt="ISO"),
        # Add stack info for errors
        structlog.processors.StackInfoRenderer(),
        # Add exception info
        structlog.dev.set_exc_info,
    ]
    
    if json_format:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.extend([
            # Pretty printing for development
            structlog.dev.ConsoleRenderer(colors=True),
        ])
    
    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=LoggerFactory(),
        cache_logger_on_first_use=True,
    )


class LoggerMixin:
    """Mixin class to add logging capabilities to any class."""
    
    @property
    def logger(self) -> structlog.BoundLogger:
        """Get a logger bound to this class."""
        if not hasattr(self, '_logger'):
            self._logger = structlog.get_logger(self.__class__.__name__)
        return self._logger


class RequestLogger:
    """Middleware for logging HTTP requests."""
    
    def __init__(self, logger_name: str = "request"):
        self.logger = structlog.get_logger(logger_name)
    
    async def log_request(self, request, call_next):
        """Log incoming HTTP requests."""
        start_time = time.time()
        
        # Log request
        self.logger.info(
            "Request started",
            method=request.method,
            url=str(request.url),
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            content_length=request.headers.get("content-length")
        )
        
        try:
            response = await call_next(request)
            duration = time.time() - start_time
            
            # Log response
            self.logger.info(
                "Request completed",
                method=request.method,
                url=str(request.url),
                status_code=response.status_code,
                duration=f"{duration:.3f}s",
                response_size=response.headers.get("content-length")
            )
            
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            
            # Log error
            self.logger.error(
                "Request failed",
                method=request.method,
                url=str(request.url),
                duration=f"{duration:.3f}s",
                error=str(e),
                error_type=type(e).__name__
            )
            
            raise


class ChatLogger:
    """Specialized logger for chat interactions."""
    
    def __init__(self):
        self.logger = structlog.get_logger("chat")
    
    def log_message_sent(self, instance_id: str, message_length: int, user_id: str = None):
        """Log when a message is sent to Claude."""
        self.logger.info(
            "Message sent to Claude",
            instance_id=instance_id,
            message_length=message_length,
            user_id=user_id or "anonymous"
        )
    
    def log_message_received(self, instance_id: str, response_length: int, response_time: float):
        """Log when a response is received from Claude."""
        self.logger.info(
            "Response received from Claude",
            instance_id=instance_id,
            response_length=response_length,
            response_time=f"{response_time:.3f}s"
        )
    
    def log_message_error(self, instance_id: str, error: str, error_type: str = None):
        """Log when a message fails."""
        self.logger.error(
            "Message failed",
            instance_id=instance_id,
            error=error,
            error_type=error_type
        )


class DockerLogger:
    """Specialized logger for Docker operations."""
    
    def __init__(self):
        self.logger = structlog.get_logger("docker")
    
    def log_container_discovered(self, container_id: str, name: str, image: str):
        """Log when a container is discovered."""
        self.logger.info(
            "Container discovered",
            container_id=container_id[:12],
            name=name,
            image=image
        )
    
    def log_container_operation(self, operation: str, container_id: str, success: bool, error: str = None):
        """Log container operations (start, stop, etc.)."""
        if success:
            self.logger.info(
                f"Container {operation} successful",
                container_id=container_id[:12]
            )
        else:
            self.logger.error(
                f"Container {operation} failed",
                container_id=container_id[:12],
                error=error
            )


# Performance monitoring logger
class PerformanceLogger:
    """Logger for performance monitoring."""
    
    def __init__(self):
        self.logger = structlog.get_logger("performance")
    
    def log_slow_operation(self, operation: str, duration: float, threshold: float = 1.0):
        """Log operations that take longer than threshold."""
        if duration > threshold:
            self.logger.warning(
                "Slow operation detected",
                operation=operation,
                duration=f"{duration:.3f}s",
                threshold=f"{threshold:.3f}s"
            )
    
    def log_resource_usage(self, cpu_percent: float, memory_mb: float):
        """Log resource usage."""
        self.logger.info(
            "Resource usage",
            cpu_percent=f"{cpu_percent:.1f}%",
            memory_mb=f"{memory_mb:.1f}MB"
        )


# Security logger
class SecurityLogger:
    """Logger for security events."""
    
    def __init__(self):
        self.logger = structlog.get_logger("security")
    
    def log_auth_attempt(self, username: str, success: bool, ip_address: str = None):
        """Log authentication attempts."""
        self.logger.info(
            "Authentication attempt",
            username=username,
            success=success,
            ip_address=ip_address,
            level="INFO" if success else "WARNING"
        )
    
    def log_unauthorized_access(self, endpoint: str, ip_address: str = None):
        """Log unauthorized access attempts."""
        self.logger.warning(
            "Unauthorized access attempt",
            endpoint=endpoint,
            ip_address=ip_address
        )


# Initialize loggers
def get_loggers():
    """Get all specialized loggers."""
    return {
        'request': RequestLogger(),
        'chat': ChatLogger(),
        'docker': DockerLogger(),
        'performance': PerformanceLogger(),
        'security': SecurityLogger()
    }


# Default setup
def setup_default_logging():
    """Setup default logging configuration."""
    log_level = os.getenv("LOG_LEVEL", "INFO")
    log_file = os.getenv("LOG_FILE", "claude_dashboard.log")
    json_logs = os.getenv("JSON_LOGS", "false").lower() == "true"
    
    setup_logging(
        log_level=log_level,
        log_file=log_file,
        enable_json_logs=json_logs,
        enable_structured_logs=True
    )


if __name__ == "__main__":
    # Test logging setup
    setup_default_logging()
    
    logger = structlog.get_logger("test")
    logger.info("Logging system initialized successfully")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    
    # Test specialized loggers
    loggers = get_loggers()
    loggers['chat'].log_message_sent("test-instance", 100, "test-user")
    loggers['docker'].log_container_discovered("abc123", "test-container", "test-image")
    loggers['security'].log_auth_attempt("admin", True, "127.0.0.1")