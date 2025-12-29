// Note: Neo4j cypher uses MATCH patterns; this template expects multiple attribute pairs passed as params
UNWIND $attrs AS attr
MATCH (p:Product)-[:HAS_ATTRIBUTE]->(:Attribute {key:attr.key, value:attr.value})
RETURN DISTINCT p.id AS id
