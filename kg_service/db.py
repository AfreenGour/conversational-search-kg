import os
import redis

FALKOR_HOST = os.getenv("FALKOR_HOST", "localhost")
FALKOR_PORT = int(os.getenv("FALKOR_PORT", 6379))
GRAPH_NAME = os.getenv("GRAPH_NAME", "kg")

client = redis.Redis(
    host=FALKOR_HOST,
    port=FALKOR_PORT,
    decode_responses=True
)

def run_cypher(query: str, params: dict | None = None):
    params = params or {}

    if params:
        flat = []
        for k, v in params.items():
            flat.extend([k, v])
        return client.execute_command(
            "GRAPH.QUERY",
            GRAPH_NAME,
            query,
            "PARAMS",
            *flat
        )

    return client.execute_command(
        "GRAPH.QUERY",
        GRAPH_NAME,
        query
    )
