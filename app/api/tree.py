# app/api/tree.py

from fastapi import APIRouter, Depends, HTTPException
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.db import crud
from app.db import schemas
from app.db.models import TreeNode
import logging
from app.core.exceptions import InvalidParentIDException, NodeNotFoundException
from app.core.utils import build_tree, find_subtree_by_id
from app.core.auth import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Create a new tree node
# ─────────────────────────────────────────────────────────────────────────────
@router.post("/tree", response_model=schemas.ResponseWrapper, status_code=status.HTTP_201_CREATED)
async def create_node(node: schemas.TreeNodeCreate, db: AsyncSession = Depends(get_db),user: dict = Depends(get_current_user)):
    """
    Create a new tree node.

    Parameters:
        node (TreeNodeCreate): Payload containing label and optional parentId.
        db (AsyncSession): Async SQLAlchemy session dependency.
        user (dict): Authenticated user from JWT token.

    Returns:
        ResponseWrapper: The created node in standard response format.

    Raises:
        InvalidParentIDException: If parentId is invalid.
        HTTPException: For internal server errors.
    """
    try:
        created = await crud.create_node(db, node)
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


# ─────────────────────────────────────────────────────────────────────────────
# Retrieve a node by its ID, including any children in a nested structure
# ─────────────────────────────────────────────────────────────────────────────
@router.get("/tree/{node_id}", response_model=schemas.ResponseWrapper)
async def get_node_by_id(node_id: int, db: AsyncSession = Depends(get_db),user: dict = Depends(get_current_user)):
    """
    Retrieve a node by its ID, including any children in a nested structure.

    Parameters:
        node_id (int): ID of the node to retrieve.
        db (AsyncSession): Async SQLAlchemy session dependency.
        user (dict): Authenticated user from JWT token.

    Returns:
        ResponseWrapper: Nested node structure starting from node_id, or error.

    Raises:
        NodeNotFoundException: If no node with the given ID exists.
        HTTPException: For unexpected server errors.
    """
    try:
        all_nodes = await crud.get_all_nodes(db)
        full_tree = build_tree(all_nodes)
        node_subtree = find_subtree_by_id(full_tree, node_id)

        if not node_subtree:
            raise NodeNotFoundException(node_id)

        return {
            "code": 200,
            "message": f"Node {node_id} retrieved successfully",
            "data": node_subtree
        }

    except (InvalidParentIDException, NodeNotFoundException):
        raise
    except Exception as e:
        logger.error(f"Unhandled error while fetching node {node_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


# ─────────────────────────────────────────────────────────────────────────────
# Get the entire tree structure starting from root nodes
# ─────────────────────────────────────────────────────────────────────────────
@router.get("/tree", response_model=schemas.ResponseWrapper)
async def get_tree(
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """
    Get the entire tree structure starting from root nodes.
    Requires JWT authentication.

    Parameters:
        db (AsyncSession): Async SQLAlchemy session dependency.
        user (dict): Authenticated user from JWT token.

    Returns:
        ResponseWrapper: A list of root-level nodes with nested children.

    Raises:
        HTTPException: If the operation fails.
    """
    try:
        nodes = await crud.get_all_nodes(db)
        tree = build_tree(nodes)
        return {
            "code": 200,
            "message": "Tree retrieved successfully" if tree else "No nodes found",
            "data": tree
        }
    except Exception as e:
        logger.error(f"Error retrieving tree: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


# ─────────────────────────────────────────────────────────────────────────────
# Update the label or parent of a node
# ─────────────────────────────────────────────────────────────────────────────
@router.put("/tree/{node_id}", response_model=schemas.ResponseWrapper)
async def update_node(node_id: int, update_data: schemas.TreeNodeCreate, db: AsyncSession = Depends(get_db),user: dict = Depends(get_current_user)):
    """
    Update the label or parent of a node.

    Parameters:
        node_id (int): ID of the node to update.
        update_data (TreeNodeCreate): New values for label/parentId.
        db (AsyncSession): Async SQLAlchemy session dependency.
        user (dict): Authenticated user from JWT token.

    Returns:
        ResponseWrapper: Updated node info.

    Raises:
        InvalidParentIDException: If parentId is invalid or causes cycle.
        NodeNotFoundException: If node doesn't exist.
        HTTPException: For internal server errors.
    """
    try:
        updated_node = await crud.update_node(db, node_id, update_data)
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


# ─────────────────────────────────────────────────────────────────────────────
# Delete a node by its ID
# ─────────────────────────────────────────────────────────────────────────────
@router.delete("/tree/{node_id}", response_model=schemas.ResponseWrapper)
async def delete_node(node_id: int, db: AsyncSession = Depends(get_db),user: dict = Depends(get_current_user)):
    """
    Delete a node by its ID.

    Parameters:
        node_id (int): ID of the node to delete.
        db (AsyncSession): Async SQLAlchemy session dependency.
        user (dict): Authenticated user from JWT token.

    Returns:
        ResponseWrapper: Status of deletion.

    Raises:
        NodeNotFoundException: If node does not exist.
        HTTPException: For internal server errors.
    """
    try:
        await crud.delete_node_by_id(db, node_id)
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


# ─────────────────────────────────────────────────────────────────────────────
# Delete all nodes from the database
# ─────────────────────────────────────────────────────────────────────────────
@router.delete("/tree", response_model=schemas.ResponseWrapper)
async def delete_all_nodes(db: AsyncSession = Depends(get_db),user: dict = Depends(get_current_user)):
    """
    Delete all nodes from the database.

    Parameters:
        db (AsyncSession): Async SQLAlchemy session dependency.
        user (dict): Authenticated user from JWT token.

    Returns:
        ResponseWrapper: Deletion status as boolean.
    
    Raises:
        HTTPException: If the deletion fails.
    """
    try:
        success = await crud.delete_all_nodes(db)
        return {
            "code": 200,
            "message": "All nodes deleted successfully",
            "data": {"isDeleted": success}
        }
    except Exception as e:
        logger.error(f"Error deleting all nodes: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
    