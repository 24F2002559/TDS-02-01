import os
import time
import uuid

from fastapi import FastAPI, Query, Request
from fastapi.responses import JSONResponse

app = FastAPI()

# ---------- Configuration ----------
ALLOWED_ORIGIN = os.environ.get("ALLOWED_ORIGIN", "https://dash-cml3ue.example.com")
MY_EMAIL = "24f2002559@ds.study.iitm.ac.in"


# ---------- Middleware for X-Request-ID and X-Process-Time ----------
@app.middleware("http")
async def add_custom_headers(request: Request, call_next):
    start_time = time.time()
    request_id = str(uuid.uuid4())
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = f"{process_time:.6f}"
    return response


# ---------- CORS (strict, manual) ----------
@app.options("/stats")
async def options_handler(request: Request):
    origin = request.headers.get("origin")
    resp = JSONResponse(content={})
    if origin == ALLOWED_ORIGIN:
        resp.headers["Access-Control-Allow-Origin"] = ALLOWED_ORIGIN
        resp.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        resp.headers["Access-Control-Allow-Headers"] = "*"
    return resp


@app.get("/stats")
async def stats(request: Request, values: str = Query(...)):
    # Parse comma‑separated integers
    try:
        nums = [int(x.strip()) for x in values.split(",") if x.strip() != ""]
    except ValueError:
        return JSONResponse(status_code=400, content={"error": "Invalid integer list"})

    if not nums:
        return JSONResponse(status_code=400, content={"error": "No values provided"})

    count = len(nums)
    total = sum(nums)
    minimum = min(nums)
    maximum = max(nums)
    mean = total / count

    result = {
        "email": MY_EMAIL,
        "count": count,
        "sum": total,
        "min": minimum,
        "max": maximum,
        "mean": mean,
    }

    resp = JSONResponse(content=result)
    origin = request.headers.get("origin")
    if origin == ALLOWED_ORIGIN:
        resp.headers["Access-Control-Allow-Origin"] = ALLOWED_ORIGIN
    return resp
