from fastapi import FastAPI
from fastapi import Request
# from pydantic import BaseModel

import json
import datetime
import os

app = FastAPI()

os.makedirs("requests", exist_ok=True)

@app.post("/")
async def root_get(request: Request):
    with open(f"requests/GET {datetime.datetime.now()}.json", "w") as f:
        json.dump(f, request.json(), indent=2)


@app.get("/")
async def root_post(request: Request):
    with open(f"requests/POST {datetime.datetime.now()}.json", "w") as f:
        json.dump(f, request.json(), indent=2)