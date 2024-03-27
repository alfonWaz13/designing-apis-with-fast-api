from typing import Annotated

import uvicorn
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from TodoApp import models
from TodoApp.models import ToDos
from TodoApp.database import get_database, engine

app = FastAPI()
models.Base.metadata.create_all(bind=engine)


@app.get("/")
async def read_all(db: Annotated[Session, Depends(get_database)]):
    return db.query(ToDos).all()


if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8000)
