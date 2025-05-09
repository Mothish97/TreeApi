from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import crud, schemas
from app.models import TreeNode
import logging
from app.exceptions import InvalidParentIDException, NodeNotFoundException

router = APIRouter()
logger = logging.getLogger(__name__)

def get_db():
    """
    Dependency to create and close DB session per request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/tree", response_model=schemas.ResponseWrapper)
def create_node(node: schemas.TreeNodeCreate, db: Session = Depends(get_db)):
    """
    Create a new tree node.

    Parameters:
        node (TreeNodeCreate): Payload containing label and optional parentId.
        db (Session): SQLAlchemy session dependency.

    Returns:
        ResponseWrapper: The created node in standard response format.

    Raises:
        InvalidParentIDException: If parentId is invalid.
        HTTPException: For internal server errors.
    """
    try:
        created = crud.create_node(db, node)
        return {
            "code": 201,
            "message": "Node created successfully",
            "data": created
        }
    except (InvalidParentIDException, NodeNotFoundException):
        raise
    except Exception as e:
        logger.error(f"Unexpected error while creating node: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/tree/{node_id}", response_model=schemas.ResponseWrapper)
def get_node_by_id(node_id: int, db: Session = Depends(get_db)):
    """
    Fetch a specific node by its ID.

    Parameters:
        node_id (int): The ID of the node to retrieve.
        db (Session): SQLAlchemy session dependency.

    Returns:
        ResponseWrapper: Node info if found, or error message.

    Raises:
        NodeNotFoundException: If node does not exist.
        HTTPException: For internal server errors or key issues.
    """
    try:
        node = db.query(TreeNode).filter(TreeNode.id == node_id).first()
        if not node:
            raise NodeNotFoundException(node_id)
        return {
            "code": 200,
            "message": f"Node {node_id} retrieved successfully",
            "data": {
                "id": node.id,
                "label": node.label,
                "children": []
            }
        }
    except (InvalidParentIDException, NodeNotFoundException):
        raise
    except KeyError as ke:
        logger.warning(f"KeyError while accessing node {node_id}: {ke}")
        raise HTTPException(status_code=400, detail=f"Missing field: {str(ke)}")
    except Exception as e:
        logger.error(f"Unhandled error while fetching node {node_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/tree", response_model=schemas.ResponseWrapper)
def get_tree(db: Session = Depends(get_db)):
    """
    Get the entire tree structure starting from root nodes.

    Parameters:
        db (Session): SQLAlchemy session dependency.

    Returns:
        ResponseWrapper: A list of root-level nodes with nested children.

    Raises:
        HTTPException: If the operation fails.
    """
    try:
        nodes = crud.get_all_nodes(db)
        tree = crud.build_tree(nodes)
        return {
            "code": 200,
            "message": "Tree retrieved successfully" if tree else "No nodes found",
            "data": tree
        }
    except Exception as e:
        logger.error(f"Error retrieving tree: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.put("/tree/{node_id}", response_model=schemas.ResponseWrapper)
def update_node(node_id: int, update_data: schemas.TreeNodeCreate, db: Session = Depends(get_db)):
    """
    Update the label or parent of a node.

    Parameters:
        node_id (int): ID of the node to update.
        update_data (TreeNodeCreate): New values for label/parentId.
        db (Session): SQLAlchemy session dependency.

    Returns:
        ResponseWrapper: Updated node info.

    Raises:
        InvalidParentIDException: If parentId is invalid or causes cycle.
        NodeNotFoundException: If node doesn't exist.
        HTTPException: For internal server errors.
    """
    try:
        updated_node = crud.update_node(db, node_id, update_data)
        return {
            "code": 200,
            "message": "Node updated successfully",
            "data": updated_node
        }
    except (InvalidParentIDException, NodeNotFoundException):
        raise
    except Exception as e:
        logger.error(f"Error updating node {node_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.delete("/tree/{node_id}", response_model=schemas.ResponseWrapper)
def delete_node(node_id: int, db: Session = Depends(get_db)):
    """
    Delete a node by its ID.

    Parameters:
        node_id (int): ID of the node to delete.
        db (Session): SQLAlchemy session dependency.

    Returns:
        ResponseWrapper: Status of deletion.

    Raises:
        NodeNotFoundException: If node does not exist.
        HTTPException: For internal server errors.
    """
    try:
        crud.delete_node_by_id(db, node_id)
        return {
            "code": 200,
            "message": f"Node {node_id} deleted successfully",
            "data": None
        }
    except NodeNotFoundException:
        raise
    except Exception as e:
        logger.error(f"Error deleting node {node_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.delete("/tree", response_model=schemas.ResponseWrapper)
def delete_all_nodes(db: Session = Depends(get_db)):
    """
    Delete all nodes from the database.

    Parameters:
        db (Session): SQLAlchemy session dependency.

    Returns:
        ResponseWrapper: Deletion status as boolean.
    
    Raises:
        HTTPException: If the deletion fails.
    """
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
