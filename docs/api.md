# API reference

Base URL (local): `http://localhost:8000`

Interactive docs while the server is running:

- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

The Next.js app expects this contract exactly (see `frontend/components/image-audit/types.ts`). Field names below are authoritative.

---

## CORS

The API allows browser calls from:

- `http://localhost:3000`
- `http://127.0.0.1:3000`

---

## Summary

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/health` | Liveness + whether the anomaly model loaded |
| `POST` | `/analyze` | Upload an image and run quality analysis |
| `GET` | `/results/{id}` | Fetch one stored analysis |
| `GET` | `/history` | List recent analyses (newest first) |
| `GET` | `/uploads/{filename}` | Static uploaded image (thumbnails) |

---

## `GET /health`

Check that the API is up and the IsolationForest artifact is loaded.

### Response `200`

```json
{
  "status": "ok",
  "model_loaded": true
}
```

If `model_loaded` is `false`, run `python -m app.training.fit_anomaly_detector` so `backend/model/anomaly_detector.joblib` exists, then restart the server.

### Example

```bash
curl http://localhost:8000/health
```

---

## `POST /analyze`

Analyze a single image upload.

### Request

- **Content-Type:** `multipart/form-data`
- **Field name:** `file` (required) — must be a decodable image

### Response `200` — `AnalysisResult`

```json
{
  "id": 1,
  "quality_score": 93.9,
  "quality_label": "ACCEPTABLE",
  "issues": [
    {
      "type": "blur",
      "severity": "medium",
      "confidence": 0.75
    }
  ],
  "image_stats": {
    "blur_score": 345.6,
    "brightness_mean": 73.6,
    "contrast": 37.3,
    "noise_estimate": 10.9
  },
  "explanation": "Hybrid score: embedding anomaly_conf=0.256 (IsolationForest decision=0.0052); CV issues: none; quality_score=93.9 -> ACCEPTABLE."
}
```

| Field | Type | Meaning |
|-------|------|---------|
| `id` | `number` (integer) | Database primary key |
| `quality_score` | `number` | 0–100 overall score |
| `quality_label` | string | `ACCEPTABLE` \| `DEGRADED` \| `DEFECTIVE` |
| `issues` | array | Detected problems (may be empty) |
| `issues[].type` | string | e.g. `blur`, `underexposure`, `overexposure`, `noise`, `corruption`, `visual_defect` |
| `issues[].severity` | string | `low` \| `medium` \| `high` only |
| `issues[].confidence` | number | 0–1 |
| `image_stats.blur_score` | number | Laplacian variance (higher ≈ sharper) |
| `image_stats.brightness_mean` | number | Mean grayscale intensity |
| `image_stats.contrast` | number | Std of grayscale intensities |
| `image_stats.noise_estimate` | number | Residual noise estimate |
| `explanation` | string \| null | Human-readable hybrid summary |

### Example

```bash
curl -X POST \
  -F "file=@sample_images/acceptable/acceptable_00.jpg" \
  http://localhost:8000/analyze
```

### Errors

| Status | Body | When |
|--------|------|------|
| `400` | `{ "detail": "File must be an image" }` | Non-image content type |
| `400` | `{ "detail": "Unreadable or invalid image file" }` | Bytes do not decode |
| `400` | `{ "detail": "Empty file upload" }` | Empty body |
| `500` | `{ "detail": "Anomaly model not loaded. ..." }` | Missing joblib model |
| `500` | `{ "detail": "Analysis failed" }` | Unexpected inference error (no stack trace leaked) |

---

## `GET /results/{id}`

Retrieve one past analysis by integer id.

### Path parameters

| Name | Type | Description |
|------|------|-------------|
| `id` | integer | Analysis id returned by `/analyze` |

### Response `200`

Same shape as `POST /analyze` (`AnalysisResult`).

### Example

```bash
curl http://localhost:8000/results/1
```

### Errors

| Status | Body |
|--------|------|
| `404` | `{ "detail": "Analysis result not found" }` |

---

## `GET /history`

List recent analyses, newest first.

### Query parameters

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `limit` | integer | `50` | Clamped to 1–200 |

### Response `200`

JSON **array** of history entries:

```json
[
  {
    "id": 2,
    "quality_label": "DEGRADED",
    "quality_score": 66.1,
    "created_at": "2026-08-27T13:04:25.575830",
    "thumbnail_url": "http://localhost:8000/uploads/b920a47fca7444b290ebdba4278c8737.jpg"
  }
]
```

| Field | Type | Meaning |
|-------|------|---------|
| `id` | number | Analysis id |
| `quality_label` | string | Same enum as analyze |
| `quality_score` | number | Stored score |
| `created_at` | string | ISO-8601 timestamp |
| `thumbnail_url` | string | Absolute URL to `/uploads/...` (uses `PUBLIC_API_BASE`) |

### Example

```bash
curl http://localhost:8000/history
curl "http://localhost:8000/history?limit=10"
```

---

## Static files: `/uploads/{filename}`

Uploaded images are written under `backend/uploads/` and mounted at `/uploads`.

History thumbnails use absolute URLs like:

`http://localhost:8000/uploads/<uuid>.jpg`

Override the public host with env `PUBLIC_API_BASE` if needed.

---

## Labels and score buckets

| `quality_label` | Score range |
|-----------------|-------------|
| `ACCEPTABLE` | ≥ 70 |
| `DEGRADED` | ≥ 40 and &lt; 70 |
| `DEFECTIVE` | &lt; 40 |

How scores are computed: [ml-pipeline.md](ml-pipeline.md).

---

## Frontend wiring

```ts
// frontend/lib/image-audit-api.ts
API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000"
// POST /analyze with FormData field "file"
// GET /history → HistoryEntry[]
// GET /results/:id → AnalysisResult
```

Errors are expected as `{ detail?: string }` (FastAPI default).
