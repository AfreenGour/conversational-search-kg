# Conversational Search KG Service

This repository contains a small KG service (FastAPI) and a Neo4j-backed dataset for a conversational search demo.

Quick start (requires Docker & Docker Compose):

Prerequisites (local dev):

- Install Python 3.10+ and Docker Desktop.
- Create and activate a virtual environment and install requirements:

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .\.venv\Scripts\Activate.ps1
pip install -r kg_service/requirements.txt
```

Run with Docker Compose:

```bash
# build and start services
docker-compose up --build
```

Ingest and test endpoints (after stack is running):

```bash
# ingest sample data into the graph (from host):
curl -X POST http://localhost:8000/kg/ingest

# resolve constraint example:
curl -X POST http://localhost:8000/kg/resolve -H 'Content-Type: application/json' -d '{"brand":"Acer"}'

# neighbors:
curl http://localhost:8000/kg/products/P1/neighbors

# explanation:
curl http://localhost:8000/kg/products/P1/explain?to=brand
```

Files of interest:
- `kg_service/` - FastAPI app and Dockerfile
- `scripts/seed_graph.py` - batched ingestion script (for direct DB seed)
- `queries/` - cypher templates used by the service

Deliverables:
- Docker Compose with Neo4j and KG service
- Endpoints: `/kg/ingest`, `/kg/resolve`, `/kg/products/{id}/neighbors`, `/kg/products/{id}/explain`, `/kg/cypher`
