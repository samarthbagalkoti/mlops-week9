FROM python:3.11-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY server.py .
EXPOSE 8001
ENV DATA_DIR=/data REPORT_DIR=/reports EVAL_INTERVAL_SEC=15 DATASET_LABEL=demo
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8001"]

