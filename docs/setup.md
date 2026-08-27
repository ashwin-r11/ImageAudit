# Local setup guide

ImageAudit runs as **two processes**: FastAPI backend (`:8000`) and Next.js frontend (`:3000`). Docker/cloud deployment is a later step.

---

## Prerequisites

- **Python** 3.11+ (3.12 works)
- **Node.js** 18+ (for the frontend)
- Disk space for `sample_images/` datasets and PyTorch wheels

---

## 1. Backend

### Create and activate the virtualenv

Deps (OpenCV, torch, etc.) must install into the **project** `.venv`. Using system `uvicorn` causes:

`ModuleNotFoundError: No module named 'cv2'`

**PowerShell (Windows):**

```powershell
cd C:\Users\ashwi\Documents\Repositories\ImageAudit
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
```

**macOS / Linux:**

```bash
cd /path/to/ImageAudit
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

### Run the API

**PowerShell:**

```powershell
cd backend
$env:PYTHONPATH = "."
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Or:

```powershell
cd backend
.\run.ps1
```

**Important:** In PowerShell, `set PYTHONPATH=.` does **nothing**. Use `$env:PYTHONPATH = "."`.

**macOS / Linux:**

```bash
cd backend
export PYTHONPATH=.
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Verify:

- [http://localhost:8000/health](http://localhost:8000/health) → `"model_loaded": true`
- [http://localhost:8000/docs](http://localhost:8000/docs) → Swagger UI

If `model_loaded` is false, fit the detector first (see [data-and-evaluation.md](data-and-evaluation.md)).

### Environment variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `DATABASE_URL` | SQLite file under `backend/` | SQLAlchemy connection |
| `MODEL_PATH` | `backend/model/anomaly_detector.joblib` | IsolationForest artifact |
| `UPLOAD_DIR` | `backend/uploads` | Saved uploads |
| `PUBLIC_API_BASE` | `http://localhost:8000` | Prefix for `thumbnail_url` |

---

## 2. Frontend

Scaffolded with **v0.dev**; lives in `frontend/`. Prefer fixing API mismatches on the **backend**.

```bash
cd frontend
npm install --legacy-peer-deps
npm install workflow --legacy-peer-deps   # required by next.config.mjs in this template
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

Optional `.env.local`:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

---

## 3. Common failures

| Symptom | Cause | Fix |
|---------|-------|-----|
| `No module named 'cv2'` | System Python / wrong uvicorn | Activate `.venv`, run `python -m uvicorn ...` or `.\run.ps1` |
| WinError 10048 / address already in use | Port 8000 taken | Stop the old process, or use another port and update `NEXT_PUBLIC_API_BASE_URL` |
| `model_loaded: false` / 500 on analyze | Missing joblib | `python -m app.training.fit_anomaly_detector` then restart |
| Frontend CORS errors | API not allowing origin | Ensure API CORS includes `http://localhost:3000` (default in `main.py`) |
| `Cannot find package 'workflow'` | Incomplete frontend install | `npm install workflow --legacy-peer-deps` |
| PowerShell `PYTHONPATH` ignored | Used `set` syntax | Use `$env:PYTHONPATH = "."` |

Find process on port 8000 (PowerShell):

```powershell
Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue |
  Select-Object OwningProcess -Unique |
  ForEach-Object { Get-Process -Id $_.OwningProcess }
```

---

## 4. Suggested first-time checklist

1. Create `.venv` and `pip install -r backend/requirements.txt`
2. Ensure `backend/model/anomaly_detector.joblib` exists (fit if needed)
3. Start backend → confirm `/health`
4. Start frontend → upload a sample image
5. Confirm history populates and thumbnails load

---

## 5. Deployment note

Local Docker Compose / cloud hosting is **not** part of the current MVP pass. Documented next step once the local pipeline is solid.

Next: [Architecture](architecture.md) · [API](api.md)
