from fastapi import Path, HTTPException, APIRouter
from starlette import status

from TodoApp.database import db_dependency
from TodoApp.models import ToDos
from TodoApp.routers.auth import user_dependency
from TodoApp.schemas import ToDoRequest


router = APIRouter()


@router.get("/", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):

    return db.query(ToDos).filter(ToDos.owner_id == user.get('id')).all()


@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):

    user_todos = db.query(ToDos).filter(ToDos.owner_id == user.get('id'))
    todo_model = user_todos.filter(ToDos.id == todo_id).first()

    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail='Item not found')


@router.post("/todo", status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency, db: db_dependency, todo_request: ToDoRequest):

    todo_to_insert = ToDos(**todo_request.dict(), owner_id=user.get('id'))
    db.add(todo_to_insert)
    db.commit()


@router.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(user: user_dependency, db: db_dependency, todo_request: ToDoRequest, todo_id: int = Path(gt=0)):

    user_todos = db.query(ToDos).filter(ToDos.owner_id == user.get('id'))
    todo_to_update = user_todos.filter(ToDos.id == todo_id).first()

    if todo_to_update is None:
        raise HTTPException(status_code=404, detail='Item not found')

    todo_to_update.title = todo_request.title
    todo_to_update.description = todo_request.description
    todo_to_update.priority = todo_request.priority
    todo_to_update.complete = todo_request.complete

    db.add(todo_to_update)
    db.commit()


@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):

    user_todos = db.query(ToDos).filter(ToDos.owner_id == user.get('id'))
    todo_to_delete = user_todos.filter(ToDos.id == todo_id).first()

    if todo_to_delete is None:
        raise HTTPException(status_code=404, detail='Item not found')

    user_todos.filter(ToDos.id == todo_id).delete()
    db.commit()
