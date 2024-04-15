from typing import Annotated

from fastapi import APIRouter, Depends
from passlib.context import CryptContext
from starlette import status

from TodoApp.database import db_dependency
from TodoApp.models import Users
from TodoApp.schemas import CreateUserRequest
from fastapi.security import OAuth2PasswordRequestForm


router = APIRouter()

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def authenticate_user(username: str, password: str, db: db_dependency):
    user = db.query(Users).filter(Users.username == username).first()
    return user is not None and bcrypt_context.verify(password, user.hashed_password)


@router.post("/auth", status_code=status.HTTP_201_CREATED)
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


@router.post("/token")
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        return 'Failed Authentication'
    return 'Success Authentication'
