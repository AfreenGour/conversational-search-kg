from fastapi import FastAPI
from kg_service.routers.kg import router as kg_router

app = FastAPI(title="Conversational Search KG")
app.include_router(kg_router)

@app.get("/")
def health():
    return {"status": "ok"}
