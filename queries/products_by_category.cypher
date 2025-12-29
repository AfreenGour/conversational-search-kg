MATCH (c:Category {id:$category})<-[:IN_CATEGORY]-(p:Product)
RETURN p.id AS id LIMIT $k
