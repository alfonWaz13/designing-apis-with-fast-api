import uvicorn
from fastapi import FastAPI

from TodoApp import models
from TodoApp.database import engine
from TodoApp.routers import auth, todos, admin, users

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)


@app.get("/healthy")
def health_check():
    return {'status': 'Healthy'}


if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8000)
