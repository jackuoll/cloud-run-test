from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()


@app.get("/")
def root() -> JSONResponse:
    return JSONResponse({"content": "hello world"})
