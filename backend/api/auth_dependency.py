from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from db.supabase import get_supabase_client
from supabase import Client

security = HTTPBearer()

def get_current_user_id(credentials: HTTPAuthorizationCredentials = Security(security)) -> str:
    token = credentials.credentials
    supabase: Client = get_supabase_client()
    try:
        response = supabase.auth.get_user(token)
        if not response or not response.user:
            raise HTTPException(status_code=401, detail="Invalid token")
        return response.user.id
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication error: {str(e)}")
