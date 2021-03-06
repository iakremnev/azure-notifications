from fastapi import FastAPI
# from pydantic import BaseModel

app = FastAPI()

@app.post("/")
async def root_get():
    pass


@app.get("/")
async def root_post():
    pass