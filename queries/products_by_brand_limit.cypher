MATCH (b:Brand {name:$brand})<-[:BRANDED_BY]-(p:Product)
RETURN p.id AS id LIMIT $k
