from fastapi import APIRouter

router = APIRouter()


@router.get("/ping/", include_in_schema=False)
async def ping_me() -> str:
    return "pong!"
