# app/main.py

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.db.database import engine, Base
from app.api import tree
from app.core.exceptions import InvalidParentIDException, NodeNotFoundException
from app.api.auth_routes import router as auth_router

import asyncio

# ─────────────────────────────────────────────────────────────────────────────
# Initialize FastAPI app
# ─────────────────────────────────────────────────────────────────────────────
app = FastAPI()

# ─────────────────────────────────────────────────────────────────────────────
# Startup event: create tables asynchronously if not present
# ─────────────────────────────────────────────────────────────────────────────
@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# ─────────────────────────────────────────────────────────────────────────────
# Root route
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/")
def read_root():
    return {"message": "Tree API is running! Visit /docs for Swagger UI."}

# ─────────────────────────────────────────────────────────────────────────────
# Exception handlers
# ─────────────────────────────────────────────────────────────────────────────
@app.exception_handler(InvalidParentIDException)
async def invalid_parent_exception_handler(request: Request, exc: InvalidParentIDException):
    return JSONResponse(status_code=400, content={"code": 400, "message": exc.message, "data": None})

@app.exception_handler(NodeNotFoundException)
async def node_not_found_handler(request: Request, exc: NodeNotFoundException):
    return JSONResponse(status_code=404, content={"code": 404, "message": exc.message, "data": None})

# ─────────────────────────────────────────────────────────────────────────────
# Register routes
# ─────────────────────────────────────────────────────────────────────────────

app.include_router(auth_router)
app.include_router(tree.router, prefix="/api")
