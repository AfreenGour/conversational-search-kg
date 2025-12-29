FROM python:3.10-slim

WORKDIR /app

COPY kg_service /app/kg_service
COPY data /app/data
COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "kg_service.main:app", "--host", "0.0.0.0", "--port", "8000"]
