from fastapi import FastAPI
from api.routers import fishing, tarot, ncku_course, db
import uvicorn

app = FastAPI()
app.include_router(fishing.router, prefix="/fishing", tags=["Fishing"])
app.include_router(tarot.router, prefix="/tarot", tags=["Tarot"])
app.include_router(ncku_course.router, prefix="/ncku_course", tags=["NCKU_course"])
app.include_router(db.router, prefix="/db", tags=["Database"])

@app.get("/")
def read_root():
    return {"message": "API OK!"}

def start_api():
    uvicorn.run(app, host="127.0.0.1", port=8000)