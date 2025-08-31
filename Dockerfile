FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY svc ./svc
COPY data ./data
ENV PORT=8080
ENV API_PORT=8080
CMD ["python","-m","svc.main"]
