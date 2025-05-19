# app/crud.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.db import models
from app.db import schemas
from app.core.exceptions import InvalidParentIDException, NodeNotFoundException
from app.core.utils import build_tree, is_descendant
from sqlalchemy.orm import selectinload


# ─────────────────────────────────────────────────────────────────────────────
# Creates a new node in the tree
# ─────────────────────────────────────────────────────────────────────────────
async def create_node(db: AsyncSession, node: schemas.TreeNodeCreate) -> schemas.TreeNodeResponse:
    """
    Creates a new node in the tree.

    Parameters:
        db (AsyncSession): The SQLAlchemy async database session.
        node (TreeNodeCreate): The input data for the node, including label and optional parentId.

    Returns:
        TreeNodeResponse: The created node with ID, label, and empty children list.

    Raises:
        InvalidParentIDException: If the specified parentId does not exist.
    """

    # Validate parentId if provided
    if node.parentId is not None:
        result = await db.execute(
            select(models.TreeNode).filter(models.TreeNode.id == node.parentId)
        )
        parent = result.scalar_one_or_none()
        if not parent:
            raise InvalidParentIDException(node.parentId)
        
    # Create and commit the new TreeNode
    db_node = models.TreeNode(label=node.label, parent_id=node.parentId)
    db.add(db_node)
    await db.commit()
    await db.refresh(db_node)

    # Re-fetch the node with eager-loaded children before returning
    # Required for Pydantic to access children in async environment
    stmt = select(models.TreeNode).options(selectinload(models.TreeNode.children)).where(models.TreeNode.id == db_node.id)
    result = await db.execute(stmt)
    node_with_children = result.scalar_one()

    return schemas.TreeNodeResponse.model_validate(node_with_children)

# ─────────────────────────────────────────────────────────────────────────────
# Retrieves all nodes from the database
# ─────────────────────────────────────────────────────────────────────────────
async def get_all_nodes(db: AsyncSession):
    """
    Retrieves all nodes from the database, including their children.

    Parameters:
        db (AsyncSession): The database session.

    Returns:
        List[TreeNode]: List of all TreeNode objects with eager-loaded children.
    """
    result = await db.execute(
        select(models.TreeNode).options(selectinload(models.TreeNode.children))
    )
    return result.scalars().all()


# ─────────────────────────────────────────────────────────────────────────────
# Fetch a single node by its ID
# ─────────────────────────────────────────────────────────────────────────────
async def get_node_by_id(db: AsyncSession, node_id: int) -> schemas.TreeNodeResponse:
    """
    Fetch a single node by its ID, including its children.

    Parameters:
        db (AsyncSession): The database session.
        node_id (int): The unique ID of the node to retrieve.

    Returns:
        TreeNodeResponse: The node data with children.

    Raises:
        NodeNotFoundException: If the node with given ID does not exist.
    """
    result = await db.execute(
        select(models.TreeNode)
        .options(selectinload(models.TreeNode.children))
        .filter(models.TreeNode.id == node_id)
    )
    node = result.scalar_one_or_none()
    if not node:
        raise NodeNotFoundException(node_id)

    return schemas.TreeNodeResponse.model_validate(node)


# ─────────────────────────────────────────────────────────────────────────────
# Deletes all nodes in the tree
# ─────────────────────────────────────────────────────────────────────────────
async def delete_all_nodes(db: AsyncSession) -> bool:
    """
    Deletes all nodes in the tree.

    Parameters:
        db (AsyncSession): The database session.

    Returns:
        bool: True if deletion is successful.
    """
    await db.execute(delete(models.TreeNode))
    await db.commit()
    return True


# ─────────────────────────────────────────────────────────────────────────────
# Deletes a single node by ID
# ─────────────────────────────────────────────────────────────────────────────
async def delete_node_by_id(db: AsyncSession, node_id: int) -> bool:
    """
    Deletes a single node by ID.

    Parameters:
        db (AsyncSession): The database session.
        node_id (int): The ID of the node to delete.

    Returns:
        bool: True if deletion was successful.

    Raises:
        NodeNotFoundException: If the node does not exist.
    """
    result = await db.execute(select(models.TreeNode).filter(models.TreeNode.id == node_id))
    node = result.scalar_one_or_none()
    if not node:
        raise NodeNotFoundException(node_id)

    await db.delete(node)
    await db.commit()
    return True


# ─────────────────────────────────────────────────────────────────────────────
# Updates an existing node's label or parent
# ─────────────────────────────────────────────────────────────────────────────
async def update_node(db: AsyncSession, node_id: int, data: schemas.TreeNodeCreate) -> schemas.TreeNodeResponse:
    """
    Updates an existing node's label or parent.

    Parameters:
        db (AsyncSession): The database session.
        node_id (int): ID of the node to update.
        data (TreeNodeCreate): New values for label and/or parentId.

    Returns:
        TreeNodeResponse: The updated node.

    Raises:
        NodeNotFoundException: If the node to update doesn't exist.
        InvalidParentIDException: If new parent is invalid or causes cyclic relationship.
    """
    # Fetch the node to update
    result = await db.execute(select(models.TreeNode).filter(models.TreeNode.id == node_id))
    node = result.scalar_one_or_none()
    if not node:
        raise NodeNotFoundException(node_id)
    
    # Update label if provided
    if data.label:
        node.label = data.label

    # Validate and update parentId if provided
    if data.parentId is not None:
        if data.parentId == node_id:
            raise InvalidParentIDException("A node cannot be its own parent.")

        result = await db.execute(select(models.TreeNode).filter(models.TreeNode.id == data.parentId))
        parent = result.scalar_one_or_none()
        if not parent:
            raise InvalidParentIDException(data.parentId)

        if await is_descendant(db, data.parentId, node_id):
            raise InvalidParentIDException("Cannot set parentId to a descendant node.")

        node.parent_id = data.parentId

    # Commit the changes
    await db.commit()
    await db.refresh(node)

    # Re-fetch the updated node with eager-loaded children for validation
    stmt = select(models.TreeNode).options(selectinload(models.TreeNode.children)).where(models.TreeNode.id == node_id)
    result = await db.execute(stmt)
    node_with_children = result.scalar_one()

    return schemas.TreeNodeResponse.model_validate(node_with_children)
