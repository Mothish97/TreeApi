from sqlalchemy.orm import Session
from app import models, schemas
from app.exceptions import InvalidParentIDException, NodeNotFoundException
from app.utils import build_tree, is_descendant

def create_node(db: Session, node: schemas.TreeNodeCreate) -> schemas.TreeNodeResponse:
    """
    Creates a new node in the tree.

    Parameters:
        db (Session): The SQLAlchemy database session.
        node (TreeNodeCreate): The input data for the node, including label and optional parentId.

    Returns:
        TreeNodeResponse: The created node with ID and label.
    
    Raises:
        InvalidParentIDException: If the specified parentId does not exist.
    """
    if node.parentId is not None:
        parent = db.query(models.TreeNode).filter(models.TreeNode.id == node.parentId).first()
        if not parent:
            raise InvalidParentIDException(node.parentId)

    db_node = models.TreeNode(label=node.label, parent_id=node.parentId)
    db.add(db_node)
    db.commit()
    db.refresh(db_node)

    return schemas.TreeNodeResponse.model_validate(db_node)


def get_all_nodes(db: Session):
    """
    Retrieves all nodes from the database.

    Parameters:
        db (Session): The database session.

    Returns:
        List[TreeNode]: List of all TreeNode objects in the database.
    """
    return db.query(models.TreeNode).all()


def get_node_by_id(db: Session, node_id: int) -> schemas.TreeNodeResponse:
    """
    Fetch a single node by its ID.

    Parameters:
        db (Session): The database session.
        node_id (int): The unique ID of the node to retrieve.

    Returns:
        TreeNodeResponse: The node data.

    Raises:
        NodeNotFoundException: If the node with given ID does not exist.
    """
    node = db.query(models.TreeNode).filter(models.TreeNode.id == node_id).first()
    if not node:
        raise NodeNotFoundException(node_id)

    return schemas.TreeNodeResponse.model_validate(node)


def delete_all_nodes(db: Session) -> bool:
    """
    Deletes all nodes in the tree.

    Parameters:
        db (Session): The database session.

    Returns:
        bool: True if deletion is successful.
    """
    db.query(models.TreeNode).delete()
    db.commit()
    return True


def delete_node_by_id(db: Session, node_id: int) -> bool:
    """
    Deletes a single node by ID.

    Parameters:
        db (Session): The database session.
        node_id (int): The ID of the node to delete.

    Returns:
        bool: True if deletion was successful.

    Raises:
        NodeNotFoundException: If the node does not exist.
    """
    node = db.query(models.TreeNode).filter(models.TreeNode.id == node_id).first()
    if not node:
        raise NodeNotFoundException(node_id)

    db.delete(node)
    db.commit()
    return True


def update_node(db: Session, node_id: int, data: schemas.TreeNodeCreate) -> schemas.TreeNodeResponse:
    """
    Updates an existing node's label or parent.

    Parameters:
        db (Session): The database session.
        node_id (int): ID of the node to update.
        data (TreeNodeCreate): New values for label and/or parentId.

    Returns:
        TreeNodeResponse: The updated node.

    Raises:
        NodeNotFoundException: If the node to update doesn't exist.
        InvalidParentIDException: If new parent is invalid or causes cyclic relationship.
    """
    node = db.query(models.TreeNode).filter(models.TreeNode.id == node_id).first()
    if not node:
        raise NodeNotFoundException(node_id)

    if data.label:
        node.label = data.label

    if data.parentId is not None:
        if data.parentId == node_id:
            raise InvalidParentIDException("A node cannot be its own parent.")

        parent = db.query(models.TreeNode).filter(models.TreeNode.id == data.parentId).first()
        if not parent:
            raise InvalidParentIDException(data.parentId)

        if is_descendant(db, data.parentId, node_id):
            raise InvalidParentIDException("Cannot set parentId to a descendant node.")

        node.parent_id = data.parentId

    db.commit()
    db.expire_all()
    node = db.query(models.TreeNode).filter(models.TreeNode.id == node_id).first()

    return schemas.TreeNodeResponse.model_validate(node)
