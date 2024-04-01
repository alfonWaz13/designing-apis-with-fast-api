from typing import Annotated

import uvicorn
from fastapi import FastAPI, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from starlette import status

from TodoApp import models
from TodoApp.models import ToDo
from TodoApp.database import get_database, engine
from TodoApp.schemas import ToDoRequest

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

db_dependency = Annotated[Session, Depends(get_database)]


@app.get("/", status_code=status.HTTP_200_OK)
async def read_all(db: db_dependency):
    return db.query(ToDo).all()


@app.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(db: db_dependency, todo_id: int = Path(gt=0)):
    todo_model = db.query(ToDo).filter(ToDo.id == todo_id).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail='Item not found')


@app.post("/todo", status_code=status.HTTP_201_CREATED)
async def create_todo(db: db_dependency, todo_request: ToDoRequest):
    todo_to_insert = ToDo(**todo_request.dict())
    db.add(todo_to_insert)
    db.commit()


@app.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
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


@app.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(db: db_dependency, todo_id: int = Path(gt=0)):
    todo_to_delete = db.query(ToDo).filter(ToDo.id == todo_id).first()
    if todo_to_delete is None:
        raise HTTPException(status_code=404, detail='Item not found')
    db.query(ToDo).filter(ToDo.id == todo_id).delete()
    db.commit()

if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8000)
