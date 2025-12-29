import json

DATA_FILE = "data/sample_catalog.json"

def load_data(tx):
    with open(DATA_FILE) as f:
        data = json.load(f)

    count = 0
    for p in data["products"]:
        tx.run(
            """
            MERGE (p:Product {id:$id})
            SET p.title=$title
            """,
            id=p["id"],
            title=p["title"]
        )
        count += 1

    return count
