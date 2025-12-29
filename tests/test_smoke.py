import requests

BASE_URL = "http://kg_service:8000"

def test_ingest_and_resolve():
    # Step 1: ingest
    r = requests.post(f"{BASE_URL}/kg/ingest")
    assert r.status_code == 200
    assert r.json()["products"] > 0

    # Step 2: resolve
    r = requests.post(
        f"{BASE_URL}/kg/resolve",
        json={"brand": "Acer"}
    )
    assert r.status_code == 200
    assert len(r.json()) > 0
