from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.core.auth import decode_access_token
from app.db.redis_client import redis_client
from app.services.user_service import UserService, User, UserServiceError

security = HTTPBearer()

async def get_redis():
    if not redis_client:
        raise RuntimeError("Redis client not initialized")
    return redis_client

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> User:
    token = credentials.credentials
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Firebase token")
    
    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

    try:
        user = await UserService.get_by_email(email)
        if user is None:
            # Create user automatically if first time from token
            user = await UserService.create_user(email=email)
    except UserServiceError:
        # Allow coaching endpoints to continue even if profile persistence is temporarily unavailable.
        user = User(id=email, email=email)
    return user
