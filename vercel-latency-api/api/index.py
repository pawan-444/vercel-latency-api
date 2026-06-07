from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse
from pathlib import Path
import json
import numpy as np

app = FastAPI()

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization",
    "Access-Control-Expose-Headers": "Access-Control-Allow-Origin",
}

DATA_FILE = Path(__file__).parent.parent / "q-vercel-latency.json"

with open(DATA_FILE, "r", encoding="utf-8") as f:
    telemetry = json.load(f)


@app.options("/{path:path}")
async def options_handler(path: str):
    return Response(status_code=200, headers=CORS_HEADERS)


@app.get("/")
def home():
    return JSONResponse(
        {"status": "working"},
        headers=CORS_HEADERS
    )


@app.post("/")
def analytics(payload: dict):

    regions = payload.get("regions", [])
    threshold = payload.get("threshold_ms", 180)

    result = {}

    for region in regions:

        records = [
            r for r in telemetry
            if r["region"] == region
        ]

        latencies = [r["latency_ms"] for r in records]
        uptimes = [r["uptime_pct"] for r in records]

        result[region] = {
            "avg_latency": round(sum(latencies) / len(latencies), 2),
            "p95_latency": round(float(np.percentile(latencies, 95)), 2),
            "avg_uptime": round(sum(uptimes) / len(uptimes), 2),
            "breaches": sum(
                1 for x in latencies
                if x > threshold
            )
        }

    return JSONResponse(
        {
            "regions": result
        },
        headers=CORS_HEADERS
    )