import os
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

_admin_token = os.getenv("ADMIN_TOKEN", "").strip()
_scheme = HTTPBearer(auto_error=False)

def require_admin(creds: HTTPAuthorizationCredentials = Depends(_scheme)):
    if not _admin_token:
        # If you forgot to set ADMIN_TOKEN, block writes defensively.
        raise HTTPException(status_code=503, detail="Admin auth not configured")
    if not creds or not creds.credentials or creds.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    if creds.credentials != _admin_token:
        raise HTTPException(status_code=403, detail="Forbidden")
    return True
