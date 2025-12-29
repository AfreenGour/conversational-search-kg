from kg_service.api import ingest, resolve, neighbors


def test_flow():
    assert ingest() > 0
    res1 = resolve({"brand": "Acer"})
    assert len(res1) > 0

    res2 = neighbors("P1")
    assert len(res2) > 0
