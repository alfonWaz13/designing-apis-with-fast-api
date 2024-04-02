import uvicorn
from fastapi import FastAPI

app = FastAPI()


@app.get("/auth/")
async def get_user():
    return {'user': 'authenticated'}


if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8000)
