MATCH (p:Product {id:$id})-[:BRANDED_BY]->(b)<-[:BRANDED_BY]-(p2:Product)
RETURN p2.id AS id LIMIT $k
MATCH (p:Product {id:$id})-[:IN_CATEGORY]->(c)<-[:IN_CATEGORY]-(p2)
RETURN p2.id LIMIT $k
