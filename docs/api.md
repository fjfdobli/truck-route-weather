# API reference

Base URL: `/api`. All responses are JSON and are gzipped when the client accepts it. No authentication. Times are ISO 8601 in UTC. Distances are in miles, wind in mph, and rain and snow in inches per hour.

| Method | Path | Purpose |
|---|---|---|
| `GET` | [`/api/health`](#get-apihealth) | Liveness check |
| `GET` | [`/api/geocode?q=`](#get-apigeocode) | Place suggestions |
| `POST` | [`/api/plan`](#post-apiplan) | Plan and rank three routes |

## GET /api/health

```json
{ "ok": true }
```

## GET /api/geocode

Place suggestions in the service area (the US, Canada and Mexico), up to 5, with duplicate labels removed. Queries shorter than 2 characters return an empty list. Results are cached for 24 hours.

| Query parameter | Type | Description |
|---|---|---|
| `q` | string | Free text, for example `Dallas` |

**200 OK**

```json
[
  { "label": "Dallas, Texas, US", "lat": 32.7762719, "lon": -96.7968559 },
  { "label": "Dallas, Iowa, US", "lat": 41.6744179, "lon": -94.0394437 }
]
```

## POST /api/plan

### Request

```json
{
  "origin": { "label": "Dallas, Texas, US", "lat": 32.7762719, "lon": -96.7968559 },
  "destination": { "label": "Houston, Texas, US" },
  "departure": "2026-11-09T14:00:00Z",
  "weight_lb": 40000,
  "interval_mi": 50
}
```

| Field | Type | Rules |
|---|---|---|
| `origin`, `destination` | object | `label` is required. Send `lat` and `lon` together (from `/api/geocode`), or neither, and the label is geocoded on the server. Must be in the service area. |
| `departure` | ISO 8601 datetime | From 1 hour ago to 5 days ahead, so the trip stays inside the forecast |
| `weight_lb` | integer | 0 to 200,000. The web form limits it to 80,000. |
| `interval_mi` | integer | `10`, `25` or `50`. Default `25`. |

### Response: 200 OK

Trimmed to one route, two checkpoints and two heatmap cells:

```json
{
  "origin": { "label": "Dallas, Texas, US", "lat": 32.7762719, "lon": -96.7968559 },
  "destination": { "label": "Houston, Texas, US", "lat": 29.7589382, "lon": -95.3676974 },
  "departure": "2026-11-07T21:00:00Z",
  "interval_mi": 50,
  "weight_lb": 40000,
  "recommended_id": 0,
  "reason": "Same weather risk as the alternatives, and 1.5 hours faster than the next best route.",
  "warning": null,
  "routes": [
    {
      "id": 0,
      "rank": 1,
      "name": "I 45",
      "distance_mi": 238.5,
      "duration_h": 4.21,
      "arrival": "2026-11-08T01:12:51Z",
      "summary": {
        "no_travel_mi": 0.0,
        "severe_mi": 0.0,
        "high_mi": 0.0,
        "moderate_mi": 0.0,
        "low_mi": 238.5,
        "unknown_mi": 0.0,
        "avg_risk": 0.0,
        "worst": "Low"
      },
      "geometry": [[32.77595, -96.79675], [32.77615, -96.79584]],
      "checkpoints": [
        {
          "lat": 32.15905,
          "lon": -96.46877,
          "mile": 50.0,
          "eta": "2026-11-07T21:53:55Z",
          "covers_mi": 50.0,
          "weather": { "wind_mph": 7.2, "rain_in": 0, "snow_in": 0 },
          "risk": {
            "level": "Low",
            "score": 0,
            "wind": "Low",
            "rain": "Low",
            "snow": "Low",
            "load_raised": false
          }
        }
      ]
    }
  ],
  "heatmap": {
    "start": "2026-11-07T21:00:00Z",
    "cell_deg": 0.3,
    "cells": [[32.4, -97.2], [32.4, -96.9]],
    "values": [[0.28, 0.3], [0.29, 0.31]]
  }
}
```

### Response fields

**Top level**

| Field | Meaning |
|---|---|
| `recommended_id` | `id` of the recommended route |
| `reason` | One sentence naming the first ranking rule that decided the recommendation |
| `warning` | `null`, or a notice: every route crosses No Travel conditions, or part of a trip is beyond the forecast |
| `routes` | Three routes (fewer only if no more distinct roads exist), in the order the router returned them. Use `rank` for display order. |

**Route**

| Field | Meaning |
|---|---|
| `rank` | 1 is the recommendation. Order: No Travel miles, Severe miles, High miles, average risk, drive time. |
| `duration_h`, `arrival` | Truck drive time (car times capped at 65 mph) and arrival |
| `summary.*_mi` | Miles at each risk level. `unknown_mi` is beyond the forecast. They add up to `distance_mi`. |
| `summary.avg_risk` | Mile-weighted average, from 0 (Low) to 4 (No Travel) |
| `geometry` | Route line as `[lat, lon]` pairs, simplified for display |

**Checkpoint**

| Field | Meaning |
|---|---|
| `mile`, `eta` | Distance from the start along the road, and when the truck gets there |
| `covers_mi` | Road this checkpoint stands for: half the distance to each neighbour |
| `weather` | Forecast at the ETA, or `null` past the forecast |
| `risk.level` | `Low`, `Moderate`, `High`, `Severe` or `No Travel`: the worst of wind, rain and snow |
| `risk.score` | The same level as a number from 0 to 4 |
| `risk.wind`, `risk.rain`, `risk.snow` | Each condition's own level. Wind is after the load rule. |
| `risk.load_raised` | `true` when the load rule made the wind level worse |

**Heatmap**

| Field | Meaning |
|---|---|
| `start` | Hour 0, equal to the departure time |
| `cell_deg` | Grid cell size in degrees (0.3 to 3, larger on long trips) |
| `cells` | Cell centres as `[lat, lon]` |
| `values[h][i]` | Risk intensity from 0 to 4 for cell `i` at hour `h` (0 to 48), or `null` past the forecast. 40 mph wind is 2.5, halfway through High. |

### Errors

| Status | When | Body |
|---|---|---|
| `400` | Invalid input | Field errors, for example `{"departure": ["Departure is in the past."]}` |
| `400` | Place outside the service area, or not found | `{"origin": ["This planner covers the US, Canada and Mexico."]}` |
| `422` | No road connects the two places | `{"detail": "No road connects these two places. Pick a start and an end on the same road network."}` |
| `502` | A routing, search or weather provider failed, or is rate limiting | `{"detail": "api.open-meteo.com is busy (rate limit). Try again in a minute."}` |

Requests to providers are retried twice (after 1 and 3 seconds) before a 502 is returned.
