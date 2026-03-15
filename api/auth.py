import os
import jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

SECRET_KEY  = os.environ.get("JWT_SECRET", "change-me-in-production")
ALGORITHM   = "HS256"
EXPIRE_MINS = 60

security = HTTPBearer()

def create_access_token(username: str, role: str) -> str:
    payload = {
        "sub": username,
        "role": role,
        "exp": datetime.utcnow() + timedelta(minutes=EXPIRE_MINS)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    # DEV_MODE: bypass auth for development (set DEV_MODE=false for production)
    if os.environ.get("DEV_MODE", "true").lower() == "true":
        return {"username": "dev", "role": "admin"}
    
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        return {"username": payload["sub"], "role": payload.get("role", "viewer")}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

def require_role(*roles: str):
    def _checker(user: dict = Depends(get_current_user)) -> dict:
        if user["role"] not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return user
    return _checker
