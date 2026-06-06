# api/index.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import statistics
import os

app = FastAPI()

# Enable CORS for POST requests from any origin
@app.middleware("http")
async def add_cors_headers(request: Request, call_next):
    response = await call_next(request)
    if request.method == "POST":
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "POST"
        response.headers["Access-Control-Allow-Headers"] = "*"
    return response

@app.post("/")
def analytics_endpoint(request: Request):
    data = request.json
    regions = data["regions"]
    threshold_ms = data["threshold_ms"]
    
    # Load the JSON telemetry file
    with open("q-vercel-latency.json", "r") as f:
        import json
        telemetry = json.load(f)
    
    results = {}
    
    for region in regions:
        # Filter records for this region
        region_records = [r for r in telemetry if r["region"] == region]
        
        if not region_records:
            results[region] = {
                "avg_latency": 0,
                "p95_latency": 0,
                "avg_uptime": 0,
                "breaches": 0
            }
            continue
        
        latencies = [r["latency_ms"] for r in region_records]
        uptimes = [r["uptime_percent"] for r in region_records]
        
        avg_latency = statistics.mean(latencies)
        p95_latency = statistics.quantiles(latencies, n=100)[94] if len(latencies) >= 100 else max(latencies)
        avg_uptime = statistics.mean(uptimes)
        breaches = sum(1 for lat in latencies if lat > threshold_ms)
        
        results[region] = {
            "avg_latency": avg_latency,
            "p95_latency": p95_latency,
            "avg_uptime": avg_uptime,
            "breaches": breaches
        }
    
    return JSONResponse(content=results)