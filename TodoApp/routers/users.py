from fastapi import APIRouter, HTTPException
from starlette import status

from TodoApp.database import db_dependency
from TodoApp.models import Users
from TodoApp.routers.auth import user_dependency, bcrypt_context
from TodoApp.schemas import NewPasswordRequest

router = APIRouter(prefix='/users', tags=['users'])


@router.get('/', status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency):

    if user is None:
        raise HTTPException(status_code=404, detail='User not found.')
    return user_info
    return db.query(Users).filter(Users.id == user.get('id')).first()

