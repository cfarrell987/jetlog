from server.database import database
from server.auth.utils import verify_password, get_user
from server.environment import SECRET_KEY, TOKEN_DURATION

import jwt
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
    redirect_slashes=True
)

ALGORITHM = "HS256"

class Token(BaseModel):
    access_token: str
    token_type: str

def create_access_token(data: dict):
    to_encode = data.copy()

    # set expiration
    assert type(TOKEN_DURATION) == int
    expire = datetime.utcnow() + timedelta(days=TOKEN_DURATION)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def update_last_login(username: str) -> None:
    database.execute_query(f"""UPDATE users
                               SET last_login = current_timestamp
                               WHERE username = ?;""", [username])

@router.post("/token", status_code=200)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    user = get_user(form_data.username)
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, 
                            headers={"WWW-Authenticate": "Bearer"},
                            detail="Incorrect username or password")

    update_last_login(user.username)

    access_token = create_access_token({"sub": user.username})
    return Token(access_token=access_token, token_type="bearer")
