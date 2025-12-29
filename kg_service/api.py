import json
import json
from pathlib import Path

# simple in-memory product store for local testing
_products = []


def ingest(data_path: str = None):
    """Load sample data into an in-memory store. Returns number of products loaded."""
    global _products
    if data_path is None:
        data_path = Path(__file__).resolve().parents[1] / "data" / "sample_catalog.json"
    else:
        data_path = Path(data_path)

    with open(data_path, "r", encoding="utf-8") as f:
        _products = json.load(f)

    return len(_products)


def resolve(query):
    """Resolve products matching the simple query dict (supports brand and category)."""
    if not _products:
        ingest()

    def matches(p):
        for k, v in query.items():
            if k not in p or p[k] != v:
                return False
        return True

    return [p["id"] for p in _products if matches(p)]


def neighbors(product_id: str):
    """Return neighbor product ids; for simplicity return products in same category (including self)."""
    if not _products:
        ingest()

    prod = next((p for p in _products if p.get("id") == product_id), None)
    if prod is None:
        return []

    category = prod.get("category")
    return [p["id"] for p in _products if p.get("category") == category]
