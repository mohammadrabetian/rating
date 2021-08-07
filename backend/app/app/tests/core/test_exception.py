import pytest
from fastapi import HTTPException

from app.core.exception import bad_request, wrong_isoformat


def test_bad_request():
    with pytest.raises(HTTPException) as http_exception:
        bad_request(err="Error")
    assert http_exception.value.detail == "BAD REQUEST - reason: Error"


def test_wrong_isoformat():
    with pytest.raises(HTTPException) as http_exception:
        wrong_isoformat()
    assert http_exception.value.detail == "Invalid timestamp - timestamp should be of type isoformat"
