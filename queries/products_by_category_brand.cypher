MATCH (c:Category {id:$category})<-[:IN_CATEGORY]-(p:Product)-[:BRANDED_BY]->(b:Brand {name:$brand})
RETURN p.id AS id
