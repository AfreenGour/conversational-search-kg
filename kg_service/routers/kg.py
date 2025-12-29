from fastapi import APIRouter, HTTPException, Header
from typing import Optional
import json
import os

from kg_service.db import run_cypher

router = APIRouter(prefix="/kg", tags=["Knowledge Graph"])

# Resolve absolute path to sample_catalog.json
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_FILE = os.path.join(BASE_DIR, "data", "sample_catalog.json")


# -------------------------
# INGEST (IDEMPOTENT)
# -------------------------
@router.post("/ingest")
def ingest():
    if not os.path.exists(DATA_FILE):
        raise HTTPException(status_code=500, detail="sample_catalog.json not found")

    with open(DATA_FILE) as f:
        data = json.load(f)

    # Support both formats
    if isinstance(data, list):
        products = data
    elif isinstance(data, dict) and "products" in data:
        products = data["products"]
    else:
        raise HTTPException(status_code=500, detail="Invalid catalog format")

    # Clear graph → idempotent ingest
    run_cypher("MATCH (n) DELETE n")

    for p in products:
        # Create Product, Brand, Category (single nodes)
        run_cypher(f"""
        MERGE (p:Product {{id:'{p["id"]}'}})
        SET p.title = '{p["title"]}',
            p.price = {p.get("price", 0)},
            p.rating = {p.get("rating", 0)},
            p.popularity = {p.get("popularity", 0)}

        MERGE (b:Brand {{name:'{p["brand"]}'}})
        MERGE (p)-[:BRANDED_BY]->(b)

        MERGE (c:Category {{id:'{p["category"]}', name:'{p["category"]}'}})
        MERGE (p)-[:IN_CATEGORY]->(c)
        """)

        # Attach attributes WITHOUT creating duplicate Product nodes
        for k, v in p.get("attributes", {}).items():
            run_cypher(f"""
            MATCH (p:Product {{id:'{p["id"]}'}})
            MERGE (a:Attribute {{key:'{k}', value:'{v}'}})
            MERGE (p)-[:HAS_ATTRIBUTE]->(a)
            """)

    return {
        "products": len(products),
        "brands": "derived",
        "categories": "derived",
        "attributes": "derived"
    }


# -------------------------
# RESOLVE (CONSTRAINT → IDS)
# -------------------------
@router.post("/resolve")
def resolve(constraints: dict):
    where = []

    if "brand" in constraints:
        where.append(f"(p)-[:BRANDED_BY]->(:Brand {{name:'{constraints['brand']}'}})")

    if "category" in constraints:
        where.append(f"(p)-[:IN_CATEGORY]->(:Category {{id:'{constraints['category']}'}})")

    query = "MATCH (p:Product)"
    if where:
        query += " WHERE " + " AND ".join(where)

    query += " RETURN DISTINCT p.id"

    result = run_cypher(query)
    rows = result[1] if len(result) > 1 else []

    return [row[0] for row in rows]


# -------------------------
# NEIGHBORS (GRAPH EXPANSION)
# -------------------------
@router.get("/products/{product_id}/neighbors")
def neighbors(product_id: str, type: Optional[str] = "brand", k: int = 5):
    if type == "brand":
        query = f"""
        MATCH (p:Product {{id:'{product_id}'}})-[:BRANDED_BY]->(b)<-[:BRANDED_BY]-(p2:Product)
        WHERE p2.id <> '{product_id}'
        RETURN DISTINCT p2.id LIMIT {k}
        """
    else:
        query = f"""
        MATCH (p:Product {{id:'{product_id}'}})-[:IN_CATEGORY]->(c)<-[:IN_CATEGORY]-(p2:Product)
        WHERE p2.id <> '{product_id}'
        RETURN DISTINCT p2.id LIMIT {k}
        """

    result = run_cypher(query)
    rows = result[1] if len(result) > 1 else []

    return {"related_products": [row[0] for row in rows]}


# -------------------------
# EXPLAIN (WHY MATCHED)
# -------------------------
@router.get("/products/{product_id}/explain")
def explain(product_id: str, to: str = "brand"):
    if to == "brand":
        query = f"""
        MATCH (p:Product {{id:'{product_id}'}})-[:BRANDED_BY]->(b)
        RETURN labels(b), b
        """
    elif to == "category":
        query = f"""
        MATCH (p:Product {{id:'{product_id}'}})-[:IN_CATEGORY]->(c)
        RETURN labels(c), c
        """
    else:
        query = f"""
        MATCH (p:Product {{id:'{product_id}'}})-[:HAS_ATTRIBUTE]->(a)
        RETURN labels(a), a
        """

    result = run_cypher(query)
    rows = result[1] if len(result) > 1 else []

    return {
        "path": [
            {"labels": row[0], "props": row[1]}
            for row in rows
        ]
    }


# -------------------------
# ADMIN CYPHER (READ-ONLY)
# -------------------------
@router.post("/cypher")
def cypher(payload: dict, x_admin_token: Optional[str] = Header(None)):
    if x_admin_token != os.getenv("ADMIN_TOKEN", "secret-token"):
        raise HTTPException(status_code=403, detail="Forbidden")

    query = payload.get("query")
    if not query:
        raise HTTPException(status_code=400, detail="Query required")

    return run_cypher(query)
