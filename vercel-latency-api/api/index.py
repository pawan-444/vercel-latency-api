from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import json
import numpy as np

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

with open("q-vercel-latency.json", "r") as f:
    telemetry = json.load(f)

@app.get("/")
def home():
    return JSONResponse(
        content={"status": "working"},
        headers={"Access-Control-Allow-Origin": "*"}
    )

@app.post("/")
def analytics(payload: dict):

    regions = payload["regions"]
    threshold = payload["threshold_ms"]

    result = {}

    for region in regions:
        records = [r for r in telemetry if r["region"] == region]

        latencies = [r["latency_ms"] for r in records]
        uptimes = [r["uptime_pct"] for r in records]

        result[region] = {
            "avg_latency": sum(latencies) / len(latencies),
            "p95_latency": float(np.percentile(latencies, 95)),
            "avg_uptime": sum(uptimes) / len(uptimes),
            "breaches": sum(1 for x in latencies if x > threshold)
        }

    return JSONResponse(
        content=result,
        headers={"Access-Control-Allow-Origin": "*"}
    )