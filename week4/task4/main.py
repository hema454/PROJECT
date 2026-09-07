from fastapi import FastAPI

from db import init_db
from router import router

app = FastAPI(title="RAG Pipeline")
app.include_router(router)


@app.on_event("startup")
def startup():
    init_db()