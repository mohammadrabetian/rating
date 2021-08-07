from fastapi import Security
from fastapi.exceptions import HTTPException
from fastapi.security.api_key import APIKey, APIKeyHeader

from app.core.config import settings

API_KEY_NAME = "Authorization-Header"
api_key_header = APIKeyHeader(name=API_KEY_NAME)


async def get_api_key(
    api_key_header: str = Security(api_key_header),
) -> APIKey:  # pragma: no cover - it is tested in test_security
    if api_key_header == settings.API_KEY_SECRET:
        return api_key_header
    raise HTTPException(status_code=403, detail="WRONG API KEY - not authorized")
