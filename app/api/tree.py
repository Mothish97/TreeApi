from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import crud, schemas
from app.models import TreeNode
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create a new node
@router.post("/tree", response_model=schemas.ResponseWrapper)
def create_node(node: schemas.TreeNodeCreate, db: Session = Depends(get_db)):
    try:
        created = crud.create_node(db, node)
        return {
            "code": 201,
            "message": "Node created successfully",
            "data": created
        }
    except ValueError as ve:
        # This gives specific feedback
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Unhandled error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/tree", response_model=schemas.ResponseWrapper)
def get_tree(db: Session = Depends(get_db)):
    try:
        nodes = crud.get_all_nodes(db)
        tree = crud.build_tree(nodes)

        if not tree:
            return {
                "code": 200,
                "message": "No nodes found",
                "data": []
            }

        return {
            "code": 200,
            "message": "Tree retrieved successfully",
            "data": tree
        }

    except Exception as e:
        logger.error(f"Error retrieving tree: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
#Get Node by id
@router.get("/tree/{node_id}", response_model=schemas.ResponseWrapper)
def get_node_by_id(node_id: int, db: Session = Depends(get_db)):
    try:
        node = db.query(TreeNode).filter(TreeNode.id == node_id).first()
        if not node:
            raise HTTPException(status_code=404, detail="Node not found")

        return {
            "code": 200,
            "message": f"Node {node_id} retrieved successfully",
            "data": {
                "id": node.id,
                "label": node.label,
                "children": []  # Optional: or fetch children if you want
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching node {node_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


# Update an existing node
@router.put("/tree/{node_id}", response_model=schemas.ResponseWrapper)
def update_node(node_id: int, update_data: schemas.TreeNodeCreate, db: Session = Depends(get_db)):
    try:
        updated_node = crud.update_node(db, node_id, update_data)
        if not updated_node:
            raise HTTPException(status_code=404, detail="Node not found")
        return {
            "code": 200,
            "message": "Node updated successfully",
            "data": updated_node
        }
    except ValueError as ve:
        logger.warning(f"Validation error: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error updating node: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Delete a specific node
@router.delete("/tree/{node_id}", response_model=schemas.ResponseWrapper)
def delete_node(node_id: int, db: Session = Depends(get_db)):
    try:
        success = crud.delete_node_by_id(db, node_id)
        if not success:
            raise HTTPException(status_code=404, detail="Node not found")
        return {
            "code": 200,
            "message": f"Node {node_id} deleted successfully",
            "data": None
        }
    except ValueError as ve:
        logger.warning(f"Validation error: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error deleting node: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Delete all nodes
@router.delete("/tree", response_model=schemas.ResponseWrapper)
def delete_all_nodes(db: Session = Depends(get_db)):
    try:
        success = crud.delete_all_nodes(db)
        return {
            "code": 200,
            "message": "All nodes deleted successfully",
            "data": {"isDeleted": success}
        }
    except Exception as e:
        logger.error(f"Error deleting all nodes: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")
