FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY kg_service /app/kg_service
COPY data /app/data
COPY scripts /app/scripts
COPY tests /app/tests   

CMD ["uvicorn", "kg_service.main:app", "--host", "0.0.0.0", "--port", "8000"]
