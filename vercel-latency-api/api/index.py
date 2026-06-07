from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import telemetry_data  # Importing the data we created in Step 1

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
    expose_headers=["Access-Control-Allow-Origin"],
)

# 1. Enable CORS for any origin
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# 2. Define the Request Schema
class AnalyticsRequest(BaseModel):
    regions: List[str]
    threshold_ms: int

# 3. Define the POST Endpoint
@app.post("/")
def analyze_telemetry(req: AnalyticsRequest):
    # Dictionary to store results
    results = {}

    # Iterate over requested regions in the JSON body
    for region in req.regions:
        # Filter data for specific region
        region_entries = [record for record in telemetry_data.telemetry_db if record["region"] == region]

        # If no data exists for region, skip or return empty (omitting for brevity)
        if not region_entries:
            continue

        # Extract metrics into lists
        latencies = sorted([r["latency_ms"] for r in region_entries])
        uptimes = [r["uptime"] for r in region_entries]

        # A. Calculate Average Latency
        avg_latency = sum(latencies) / len(latencies)

        # B. Calculate p95 Latency
        # Index formula: (N - 1) * 0.95. Sort ensures we grab the top 5%.
        idx_p95 = int((len(latencies) - 1) * 0.95)
        p95_latency = latencies[idx_p95]

        # C. Calculate Average Uptime
        avg_uptime = sum(uptimes) / len(uptimes)

        # D. Calculate Breaches (count where latency > threshold)
        breaches = sum(1 for lat in latencies if lat > req.threshold_ms)

        # Add to results dictionary
        results[region] = {
            "avg_latency": round(avg_latency, 2),
            "p95_latency": p95_latency,
            "avg_uptime": round(avg_uptime, 2),
            "breaches": breaches
        }

    return results