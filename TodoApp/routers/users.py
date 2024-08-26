from fastapi import APIRouter, HTTPException
from starlette import status

from TodoApp.database import db_dependency
from TodoApp.models import Users
from TodoApp.routers.auth import user_dependency, bcrypt_context
from TodoApp.schemas import NewPasswordRequest

router = APIRouter(prefix='/user', tags=['users'])


@router.get('/', status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency):

    if user is None:
        raise HTTPException(status_code=404, detail='User not found.')
    return db.query(Users).filter(Users.id == user.get('id')).first()


@router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user: user_dependency, db: db_dependency, new_password_request: NewPasswordRequest):

    if user is None:
        raise HTTPException(status_code=404, detail='User not found.')

    user_to_update = db.query(Users).filter(Users.id == user.get('id')).first()
    if not bcrypt_context.verify(new_password_request.current_password, user_to_update.hashed_password):
        raise HTTPException(status_code=401, detail='Error on password update.')
    user_to_update.hashed_password = bcrypt_context.hash(new_password_request.new_password)
    db.add(user_to_update)
    db.commit()
