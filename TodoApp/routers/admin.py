from fastapi import APIRouter, HTTPException
from starlette import status

from TodoApp.database import db_dependency
from TodoApp.models import ToDos
from TodoApp.routers.auth import user_dependency

router = APIRouter(prefix='/admin', tags=['admin'])


@router.get("/todo", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    if user.get('role') != 'admin':
        raise HTTPException(status_code=401, detail='Authentication failed')
    return db.query(ToDos).all()
