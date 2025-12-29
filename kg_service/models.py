from pydantic import BaseModel
from typing import Optional

class ResolveRequest(BaseModel):
    brand: Optional[str] = None
    category: Optional[str] = None
