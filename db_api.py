from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
import psycopg2.extras
import re

app = FastAPI()

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "user": "postgres",
    "password": "difyai123456",
    "database": "jobsdb"
}

BLOCKED = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|TRUNCATE|ALTER|CREATE|GRANT|REVOKE)\b",
    re.IGNORECASE
)

class QueryRequest(BaseModel):
    sql: str

@app.post("/query")
async def run_query(req: QueryRequest):
    if BLOCKED.search(req.sql):
        raise HTTPException(status_code=400, detail="Only SELECT queries are allowed.")
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(req.sql)
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return {"result": [dict(r) for r in rows], "count": len(rows)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health():
    return {"status": "ok"}
