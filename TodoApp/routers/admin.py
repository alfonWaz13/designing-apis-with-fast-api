from fastapi import APIRouter, HTTPException, Path
from starlette import status

from TodoApp.database import db_dependency
from TodoApp.models import ToDos
from TodoApp.routers.auth import user_dependency

router = APIRouter(prefix='/admin', tags=['admin'])


@router.get("/todo", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    await check_that_user_is_admin(user)
    return db.query(ToDos).all()


@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    await check_that_user_is_admin(user)
    todo_to_delete = db.query(ToDos).filter(ToDos.id == todo_id)
    if todo_to_delete.first() is None:
        raise HTTPException(status_code=404, detail='Todo not found.')
    todo_to_delete.delete()
    db.commit()


async def check_that_user_is_admin(user):
    if user.get('role') != 'admin':
        raise HTTPException(status_code=401, detail='Authentication Failed')
