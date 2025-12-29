from typing import Any, Callable, Dict, List, Optional


class FastAPI:
    def __init__(self, *args, **kwargs):
        self._routes = []

    def include_router(self, router: Any):
        self._routes.append(router)


class APIRouter:
    def __init__(self, prefix: str = "", tags: Optional[List[str]] = None):
        self.prefix = prefix
        self.tags = tags or []


class HTTPException(Exception):
    def __init__(self, status_code: int = 500, detail: str = ""):
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


def Header(default: Optional[str] = None):
    return default
