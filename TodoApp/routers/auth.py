from fastapi import APIRouter
from passlib.context import CryptContext
from starlette import status

from TodoApp.database import db_dependency
from TodoApp.models import Users
from TodoApp.schemas import CreateUserRequest


router = APIRouter()

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


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
