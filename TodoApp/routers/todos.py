from typing import Annotated

from fastapi import Depends, Path, HTTPException, APIRouter
from sqlalchemy.orm import Session
from starlette import status

from TodoApp.database import get_database
from TodoApp.models import ToDo
from TodoApp.schemas import ToDoRequest

db_dependency = Annotated[Session, Depends(get_database)]
router = APIRouter()


@router.get("/", status_code=status.HTTP_200_OK)
async def read_all(db: db_dependency):
    return db.query(ToDo).all()


@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(db: db_dependency, todo_id: int = Path(gt=0)):
    todo_model = db.query(ToDo).filter(ToDo.id == todo_id).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail='Item not found')


@router.post("/todo", status_code=status.HTTP_201_CREATED)
async def create_todo(db: db_dependency, todo_request: ToDoRequest):
    todo_to_insert = ToDo(**todo_request.dict())
    db.add(todo_to_insert)
    db.commit()


@router.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(db: db_dependency, todo_request: ToDoRequest, todo_id: int = Path(gt=0)):
    todo_to_update: ToDo = db.query(ToDo).filter(ToDo.id == todo_id).first()
    if todo_to_update is None:
        raise HTTPException(status_code=404, detail='Item not found')

    todo_to_update.title = todo_request.title
    todo_to_update.description = todo_request.description
    todo_to_update.priority = todo_request.priority
    todo_to_update.complete = todo_request.complete

    db.add(todo_to_update)
    db.commit()


@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(db: db_dependency, todo_id: int = Path(gt=0)):
    todo_to_delete = db.query(ToDo).filter(ToDo.id == todo_id).first()
    if todo_to_delete is None:
        raise HTTPException(status_code=404, detail='Item not found')
    db.query(ToDo).filter(ToDo.id == todo_id).delete()
    db.commit()
