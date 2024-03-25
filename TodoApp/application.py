import uvicorn
from fastapi import FastAPI

from database import engine
import models


app = FastAPI()
models.Base.metadata.create_all(bind=engine)

if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8000)
