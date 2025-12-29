from fastapi import FastAPI
from kg_service.routers.kg import router

app = FastAPI(title="Conversational Search KG")

app.include_router(router)

@app.get("/")
def health():
    return {"status": "ok"}
