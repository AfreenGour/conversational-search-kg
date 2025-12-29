from pathlib import Path
import os
import json
from neo4j import GraphDatabase


NEO4J_URI = os.getenv("NEO4J_URI", "bolt://neo4j:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

prod_path = Path(__file__).resolve().parents[1] / "data" / "sample_catalog.json"
with open(prod_path, "r", encoding="utf-8") as f:
    products = json.load(f)


def seed(batch_size: int = 50):
    statements = []
    for p in products:
        statements.append((
            """
            MERGE (pr:Product {id:$id})
            SET pr.title = $title, pr.price = $price
            MERGE (b:Brand {name:$brand})
            MERGE (c:Category {id:$category, name:$category})
            MERGE (pr)-[:BRANDED_BY]->(b)
            MERGE (pr)-[:IN_CATEGORY]->(c)
            """,
            {
                "id": p["id"],
                "title": p.get("title"),
                "price": p.get("price"),
                "brand": p.get("brand"),
                "category": p.get("category"),
            },
        ))

    with driver.session() as session:
        for i in range(0, len(statements), batch_size):
            batch = statements[i : i + batch_size]
            with session.begin_transaction() as tx:
                for stmt, params in batch:
                    tx.run(stmt, **params)
                tx.commit()


if __name__ == "__main__":
    seed()

import os
import json
from neo4j import GraphDatabase

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://neo4j:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

prod_path = Path(__file__).resolve().parents[1] / "data" / "sample_catalog.json"
with open(prod_path, "r", encoding="utf-8") as f:
    products = json.load(f)


def seed(batch_size: int = 50):
    from pathlib import Path
    import os
    import json
    from neo4j import GraphDatabase


    NEO4J_URI = os.getenv("NEO4J_URI", "bolt://neo4j:7687")
    NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

    prod_path = Path(__file__).resolve().parents[1] / "data" / "sample_catalog.json"
    with open(prod_path, "r", encoding="utf-8") as f:
        products = json.load(f)


    def seed(batch_size: int = 50):
        statements = []
        for p in products:
            statements.append((
                """
                MERGE (pr:Product {id:$id})
                SET pr.title = $title, pr.price = $price
                MERGE (b:Brand {name:$brand})
                MERGE (c:Category {id:$category, name:$category})
                MERGE (pr)-[:BRANDED_BY]->(b)
                MERGE (pr)-[:IN_CATEGORY]->(c)
                """,
                {
                    "id": p["id"],
                    "title": p.get("title"),
                    "price": p.get("price"),
                    "brand": p.get("brand"),
                    "category": p.get("category"),
                },
            ))

        with driver.session() as session:
            for i in range(0, len(statements), batch_size):
                batch = statements[i : i + batch_size]
                tx = session.begin_transaction()
                for stmt, params in batch:
                    tx.run(stmt, **params)
                tx.commit()


    if __name__ == "__main__":
        seed()
