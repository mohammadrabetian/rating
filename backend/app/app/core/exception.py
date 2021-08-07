from fastapi import HTTPException


def wrong_isoformat():
    raise HTTPException(
        status_code=422,
        detail="Invalid timestamp - timestamp should be of type isoformat",
    )


def bad_request(err: str):
    raise HTTPException(status_code=400, detail=f"BAD REQUEST - reason: {err}")
