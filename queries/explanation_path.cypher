MATCH (p:Product {id:$id})-[:HAS_ATTRIBUTE|:IN_CATEGORY|:BRANDED_BY]->(x)
RETURN labels(x) AS labels, x AS node
