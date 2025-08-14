"""
Authentication system for Claude Code Dashboard.
Provides token-based authentication for remote access via Tailscale.
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Optional
import jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext

logger = logging.getLogger(__name__)

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "claude-code-dashboard-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))  # 24 hours

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer(auto_error=False)

# Default credentials (change in production!)
DEFAULT_USERNAME = os.getenv("DASHBOARD_USERNAME", "admin")
DEFAULT_PASSWORD = os.getenv("DASHBOARD_PASSWORD", "claude-dashboard-2024")

# Simple in-memory user store (in production, use a proper database)
USERS = {
    DEFAULT_USERNAME: {
        "username": DEFAULT_USERNAME,
        "hashed_password": pwd_context.hash(DEFAULT_PASSWORD),
        "is_active": True
    }
}


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def authenticate_user(username: str, password: str) -> Optional[dict]:
    """
    Authenticate a user with username and password.
    
    Args:
        username: Username
        password: Plain text password
        
    Returns:
        User dict if authentication successful, None otherwise
    """
    user = USERS.get(username)
    if not user:
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Data to encode in the token
        expires_delta: Token expiration time
        
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """
    Verify and decode a JWT token.
    
    Args:
        token: JWT token to verify
        
    Returns:
        Decoded token payload if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        return payload
    except jwt.PyJWTError:
        return None


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Optional[dict]:
    """
    Get current authenticated user from JWT token.
    
    Args:
        credentials: HTTP authorization credentials
        
    Returns:
        Current user dict
        
    Raises:
        HTTPException: If authentication fails
    """
    # If no authentication is required (for local development)
    if os.getenv("DISABLE_AUTH", "false").lower() == "true":
        return {"username": "local_user", "is_active": True}
    
    # If no credentials provided, allow access for local requests
    if not credentials:
        # In a production environment, you might want to check the request origin
        # For now, we'll allow unauthenticated access for localhost
        logger.warning("No authentication credentials provided - allowing access")
        return {"username": "anonymous", "is_active": True}
    
    # Verify the token
    payload = verify_token(credentials.credentials)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    username: str = payload.get("sub")
    user = USERS.get(username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    return user


async def get_current_user_optional(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Optional[dict]:
    """
    Get current authenticated user (optional - doesn't raise exceptions).
    
    Args:
        credentials: HTTP authorization credentials
        
    Returns:
        Current user dict or None
    """
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None


def require_auth() -> bool:
    """Check if authentication is required based on environment."""
    return os.getenv("DISABLE_AUTH", "false").lower() != "true"


class AuthConfig:
    """Authentication configuration class."""
    
    @staticmethod
    def is_enabled() -> bool:
        """Check if authentication is enabled."""
        return require_auth()
    
    @staticmethod
    def get_default_credentials() -> dict:
        """Get default login credentials (for setup instructions)."""
        return {
            "username": DEFAULT_USERNAME,
            "password": DEFAULT_PASSWORD if not require_auth() else "***"
        }
    
    @staticmethod
    def add_user(username: str, password: str) -> bool:
        """
        Add a new user.
        
        Args:
            username: New username
            password: New password
            
        Returns:
            True if user added successfully
        """
        if username in USERS:
            return False
        
        USERS[username] = {
            "username": username,
            "hashed_password": get_password_hash(password),
            "is_active": True
        }
        return True
    
    @staticmethod
    def remove_user(username: str) -> bool:
        """
        Remove a user.
        
        Args:
            username: Username to remove
            
        Returns:
            True if user removed successfully
        """
        if username in USERS and username != DEFAULT_USERNAME:
            del USERS[username]
            return True
        return False
    
    @staticmethod
    def list_users() -> list:
        """List all users."""
        return [{"username": user["username"], "is_active": user["is_active"]} 
                for user in USERS.values()]