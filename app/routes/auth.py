from fastapi import APIRouter, Depends, HTTPException, status, Header
from pydantic import BaseModel, EmailStr
from app.services.user_service import UserService, User, UserServiceError
from app.core.auth import decode_access_token

router = APIRouter()

class SyncRequest(BaseModel):
    full_name: str | None = None

class UserProfileResponse(BaseModel):
    email: str
    full_name: str | None = None
    status: str = "ok"

async def get_current_user(authorization: str = Header(None)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization header")
    token = authorization.split(" ")[1]
    payload = decode_access_token(token)
    if not payload or not payload.get("sub"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Firebase token")
    return payload["sub"]

@router.post("/sync", response_model=UserProfileResponse)
async def sync_profile(request: SyncRequest, email: str = Depends(get_current_user)):
    try:
        user = await UserService.get_by_email(email)
        if not user:
            user = await UserService.create_user(email=email, full_name=request.full_name)
        else:
            # update last active
            await UserService.update_last_active(user)
    except UserServiceError:
        return {"email": email, "full_name": request.full_name, "status": "storage_unavailable"}
    
    return {"email": user.email, "full_name": user.full_name, "status": "synced"}
