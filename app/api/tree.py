from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from app.database import SessionLocal
from app import crud, schemas
#Disabled Auth 
# from app.auth import (
#     authenticate_user,
#     create_access_token,
#     get_current_user
# )

router = APIRouter()

# 🔹 Get DB session per request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Optional login route (disabled auth for now)
# @router.post("/login")
# def login(form_data: OAuth2PasswordRequestForm = Depends()):
#     if not authenticate_user(form_data.username, form_data.password):
#         raise HTTPException(status_code=401, detail="Invalid credentials")
#     access_token = create_access_token(
#         data={"sub": form_data.username},
#         expires_delta=timedelta(minutes=30)
#     )
#     return {"access_token": access_token, "token_type": "bearer"}



# Public POST: Add node
@router.post("/tree", response_model=schemas.TreeNodeResponse)
def create_node(
    node: schemas.TreeNodeCreate,
    db: Session = Depends(get_db)
    # , user: str = Depends(get_current_user)  #disabled
):
    return crud.create_node(db, node)

#Public GET: Return tree
@router.delete("/tree")
def delete_tree(db: Session = Depends(get_db)):
    return {"success": crud.delete_all_nodes(db)}


#Public GET: Return tree
@router.get("/tree", response_model=list[schemas.TreeNodeResponse])
def get_tree(db: Session = Depends(get_db)):
    all_nodes = crud.get_all_nodes(db)
    return crud.build_tree(all_nodes)