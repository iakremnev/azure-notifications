from fastapi import FastAPI
from fastapi import Request

import pickle
import datetime
import os

app = FastAPI()


@app.post("/")
async def root_get(request: Request):
    os.makedirs("requests", exist_ok=True)
    with open(f"requests/GET {datetime.datetime.now()}.json", "w") as f:
        pickle.dump(f, request)


@app.get("/")
async def root_post(request: Request):
    os.makedirs("requests", exist_ok=True)
    with open(f"requests/POST {datetime.datetime.now()}.json", "w") as f:
        pickle.dump(f, request)