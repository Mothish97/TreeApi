from fastapi import FastAPI
from app.database import engine, Base
from app.api import tree

#Create DB tables (only if not exists)
Base.metadata.create_all(bind=engine)

#Initialize FastAPI app
app = FastAPI()

# Root welcome route
@app.get("/")
def read_root():
    return {"message": "Tree API is running! Visit /docs for Swagger UI."}

#Register the routes under /api
app.include_router(tree.router, prefix="/api")
