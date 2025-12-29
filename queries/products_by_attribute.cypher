MATCH (p:Product)-[:HAS_ATTRIBUTE]->(:Attribute {key:$key, value:$value})
RETURN p.id AS id
