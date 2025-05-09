# app/main.py

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.database import engine, Base
from app.api import tree
from app.exceptions import InvalidParentIDException, NodeNotFoundException

# ─────────────────────────────────────────────────────────────────────────────
# Initialize and configure FastAPI application
#─────────────────────────────────────────────────────────────────────────────

# Automatically create tables based on models (only if not exist)
Base.metadata.create_all(bind=engine)

# Instantiate the FastAPI app
app = FastAPI()


# ─────────────────────────────────────────────────────────────────────────────
# Root route to confirm API is running
#─────────────────────────────────────────────────────────────────────────────
@app.get("/")
def read_root():
    return {"message": "Tree API is running! Visit /docs for Swagger UI."}


# ─────────────────────────────────────────────────────────────────────────────
# Global exception handler for InvalidParentIDException
#─────────────────────────────────────────────────────────────────────────────
@app.exception_handler(InvalidParentIDException)
async def invalid_parent_exception_handler(request: Request, exc: InvalidParentIDException):
    return JSONResponse(
        status_code=400,
        content={
            "code": 400,
            "message": exc.message,
            "data": None
        },
    )


# ─────────────────────────────────────────────────────────────────────────────
# Global exception handler for NodeNotFoundException
#─────────────────────────────────────────────────────────────────────────────
@app.exception_handler(NodeNotFoundException)
async def node_not_found_handler(request: Request, exc: NodeNotFoundException):
    return JSONResponse(
        status_code=404,
        content={
            "code": 404,
            "message": exc.message,
            "data": None
        }
    )


# ─────────────────────────────────────────────────────────────────────────────
# Register API routes from app.api.tree under the /api prefix
#─────────────────────────────────────────────────────────────────────────────
app.include_router(tree.router, prefix="/api")
