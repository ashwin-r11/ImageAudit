# ImageAudit documentation

Welcome. This folder explains how **ImageAudit** works end-to-end: architecture, API, ML pipeline, data/evaluation, and local setup.

Start with the [root README](../README.md) for a quick overview, then dive into the pages below.

## Contents

| Doc | What you’ll learn |
|-----|-------------------|
| [architecture.md](architecture.md) | System diagram, request flow, training pipeline, module map |
| [api.md](api.md) | REST endpoints, request/response JSON, errors, CORS |
| [ml-pipeline.md](ml-pipeline.md) | OpenCV features, MobileNetV2, IsolationForest, scoring & thresholds |
| [data-and-evaluation.md](data-and-evaluation.md) | Datasets, capped sampling, fit/eval commands, limitations |
| [setup.md](setup.md) | Detailed Windows / macOS / Linux setup and common failures |

## Interactive API docs

With the backend running:

- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Reading tip

Diagrams use **Mermaid**. They render on GitHub, GitLab, and many Markdown previewers (including Cursor).
