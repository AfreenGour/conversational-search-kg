from fastapi import APIRouter, HTTPException, Header
from typing import Optional, List
import json, os
from kg_service.db import get_session

router = APIRouter(prefix="/kg", tags=["Knowledge Graph"])

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_FILE = os.path.join(BASE_DIR, "data", "sample_catalog.json")


def _run_cypher(query: str, params: dict = None) -> List[dict]:
    params = params or {}
    with get_session() as session:
        result = session.run(query, **params)
        return [dict(r) for r in result]


@router.post("/ingest")
def ingest():
    if not os.path.exists(DATA_FILE):
        raise HTTPException(500, "sample_catalog.json not found")

    with open(DATA_FILE, "r") as f:
        products = json.load(f)

    def write_tx(tx):
        count = 0
        for p in products:
            tx.run(
                """
                MERGE (p:Product {id:$id})
                SET p.title=$title,
                    p.price=$price,
                    p.rating=$rating,
                    p.popularity=$popularity

                MERGE (b:Brand {name:$brand})
                MERGE (p)-[:BRANDED_BY]->(b)

                MERGE (c:Category {id:$category})
                MERGE (p)-[:IN_CATEGORY]->(c)
                """,
                id=p["id"],
                title=p["title"],
                price=p["price"],
                rating=p["rating"],
                popularity=p["popularity"],
                brand=p["brand"],
                category=p["category"],
            )

            for k, v in p["attributes"].items():
                tx.run(
                    """
                    MERGE (a:Attribute {key:$key, value:$value})
                    MERGE (p)-[:HAS_ATTRIBUTE]->(a)
                    """,
                    key=k,
                    value=v,
                )

            count += 1
        return count

    with get_session() as session:
        loaded = session.execute_write(write_tx)

    return {"loaded_products": loaded}


@router.post("/resolve")
def resolve(constraints: dict):
    query = "MATCH (p:Product)"
    clauses, params = [], {}

    if "brand" in constraints:
        clauses.append("(p)-[:BRANDED_BY]->(:Brand {name:$brand})")
        params["brand"] = constraints["brand"]

    if "category" in constraints:
        clauses.append("(p)-[:IN_CATEGORY]->(:Category {id:$category})")
        params["category"] = constraints["category"]

    if clauses:
        query += " WHERE " + " AND ".join(clauses)

    query += " RETURN p.id AS id"
    return [r["id"] for r in _run_cypher(query, params)]


@router.get("/products/{product_id}/neighbors")
def neighbors(product_id: str, type: str = "brand", k: int = 5):
    if type == "brand":
        q = """
        MATCH (p:Product {id:$id})-[:BRANDED_BY]->(b)<-[:BRANDED_BY]-(x)
        RETURN x.id AS id LIMIT $k
        """
    else:
        q = """
        MATCH (p:Product {id:$id})-[:IN_CATEGORY]->(c)<-[:IN_CATEGORY]-(x)
        RETURN x.id AS id LIMIT $k
        """

    return [r["id"] for r in _run_cypher(q, {"id": product_id, "k": k})]


@router.get("/products/{product_id}/explain")
def explain(product_id: str, to: str = "brand"):
    if to == "brand":
        q = "MATCH (p:Product {id:$id})-[:BRANDED_BY]->(x) RETURN labels(x), properties(x)"
    elif to == "category":
        q = "MATCH (p:Product {id:$id})-[:IN_CATEGORY]->(x) RETURN labels(x), properties(x)"
    else:
        q = "MATCH (p:Product {id:$id})-[:HAS_ATTRIBUTE]->(x) RETURN labels(x), properties(x)"

    return _run_cypher(q, {"id": product_id})
