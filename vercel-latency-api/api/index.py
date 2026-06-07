from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import json
import numpy as np

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

telemetry = []

try:
    data_file = Path(__file__).parent.parent / "q-vercel-latency.json"

    with open(data_file, "r", encoding="utf-8") as f:
        telemetry = json.load(f)

except Exception as e:
    telemetry = []
    print("LOAD ERROR:", e)


@app.get("/")
def home():
    return {
        "status": "working",
        "records_loaded": len(telemetry)
    }


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

        if not records:
            result[region] = {
                "avg_latency": 0,
                "p95_latency": 0,
                "avg_uptime": 0,
                "breaches": 0
            }
            continue

        latencies = [r["latency_ms"] for r in records]
        uptimes = [r["uptime_pct"] for r in records]

        result[region] = {
            "avg_latency": round(sum(latencies) / len(latencies), 2),
            "p95_latency": round(float(np.percentile(latencies, 95)), 2),
            "avg_uptime": round(sum(uptimes) / len(uptimes), 2),
            "breaches": sum(1 for x in latencies if x > threshold)
        }

    return {
        "regions": result
    }