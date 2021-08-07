from fastapi import APIRouter

router = APIRouter()


@router.get("/", include_in_schema=False)
async def ping_me():
    return "pong!"
