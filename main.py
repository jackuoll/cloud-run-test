from typing import Any, Dict

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from google.cloud import bigquery

app = FastAPI()


@app.get("/")
def root() -> JSONResponse:
    return JSONResponse(content={"content": "hello world"})


@app.get("/test_bq/")
def test_bq() -> JSONResponse:
    client = bigquery.Client()
    query_job = client.query(
        "select customer_id, emailable_customer from offers.audience_marketable limit 10"
    )
    rows = query_job.result()
    res = []
    for row in rows:
        output: Dict[str, Any] = {
            "customer_id": row["customer_id"],
            "emailable": row["emailable_customer"],
        }
        res.append(output)
    return JSONResponse(content={"status": res})
