FROM python:3.11-slim
WORKDIR /app
RUN pip install flask==3.0.3
COPY server.py .
EXPOSE 5001
CMD ["python", "server.py"]

