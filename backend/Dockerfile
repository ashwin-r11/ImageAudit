FROM python:3.11-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    UPLOAD_DIR=/app/uploads \
    MODEL_PATH=/app/model/anomaly_detector.joblib \
    PUBLIC_API_BASE=http://localhost:8000 \
    DATABASE_URL=sqlite:////data/imageaudit.db

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir torch==2.5.1 torchvision==0.20.1 \
        --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir \
        $(grep -vE '^(torch|torchvision)==' requirements.txt)

COPY app/ ./app/
COPY model/ ./model/

RUN python -c "from torchvision.models import MobileNet_V2_Weights, mobilenet_v2; mobilenet_v2(weights=MobileNet_V2_Weights.IMAGENET1K_V1)"

RUN groupadd --gid 1000 appuser \
    && useradd --uid 1000 --gid appuser --create-home appuser \
    && mkdir -p /data /app/uploads \
    && chown -R appuser:appuser /data /app/uploads /app

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
