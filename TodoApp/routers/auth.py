from datetime import timedelta, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from passlib.context import CryptContext
from starlette import status

from TodoApp.database import db_dependency
from TodoApp.models import Users, Token
from TodoApp.schemas import CreateUserRequest
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError

router = APIRouter(prefix='/auth', tags=['auth'])

SECRET_KEY = 'fc744cc1547da2e58520a888df43bd0b694b8084739ac6571a1330231f587c5b'
ALGORITHM = 'HS256'
TOKEN_EXPIRATION_TIME_MINUTES = 20

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')


def authenticate_user(username: str, password: str, db: db_dependency):
    user = db.query(Users).filter(Users.username == username).first()
    return user if user is not None and bcrypt_context.verify(password, user.hashed_password) else None


def create_access_token(username: str, user_id: int, delta_expiration_time: timedelta):
    encode = {'sub': username, 'id': user_id}
    expires = datetime.utcnow() + delta_expiration_time
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get('sub')
        user_id = payload.get('id')

        if username is None or user_id is None:
            raise ValueError
        return {'username': username, 'id': user_id}

    except (JWTError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, request: CreateUserRequest):
    user_to_create = Users(
        email=request.email,
        username=request.username,
        first_name=request.first_name,
        last_name=request.last_name,
        role=request.role,
        hashed_password=bcrypt_context.hash(request.password),
        is_active=True
    )

    db.add(user_to_create)
    db.commit()


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')

    token = create_access_token(user.username, user.id, timedelta(minutes=TOKEN_EXPIRATION_TIME_MINUTES))
    return {'access_token': token, 'token_type': 'bearer'}
