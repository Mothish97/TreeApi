from sqlalchemy.orm import Session
from app import models, schemas

# Create a new node in the database
def create_node(db: Session, node: schemas.TreeNodeCreate):
    # Check if parentId exists (if given)
    if node.parentId is not None:
        parent = db.query(models.TreeNode).filter(models.TreeNode.id == node.parentId).first()
        if not parent:
            raise ValueError("Invalid parentId")

    db_node = models.TreeNode(
        label=node.label,
        parent_id=node.parentId
    )
    db.add(db_node)
    db.commit()
    db.refresh(db_node)
    return db_node

# Retrieve all nodes from the database
def get_all_nodes(db: Session):
    return db.query(models.TreeNode).all()

#Get Node by id
def get_node_by_id(db: Session, node_id: int):
    return db.query(models.TreeNode).filter(models.TreeNode.id == node_id).first()

# Delete all nodes in the database
def delete_all_nodes(db: Session):
    db.query(models.TreeNode).delete()
    db.commit()
    return True

# Recursively build tree structure from flat list
def build_tree(nodes, parent_id=None):
    tree = []
    for node in nodes:
        if node.parent_id == parent_id:
            children = build_tree(nodes, node.id)
            tree.append({
                "id": node.id,
                "label": node.label,
                "children": children
            })
    return tree

# Update an existing node
def update_node(db: Session, node_id: int, data: schemas.TreeNodeCreate):
    node = db.query(models.TreeNode).filter(models.TreeNode.id == node_id).first()
    if not node:
        return None

    if data.label:
        node.label = data.label
    if data.parentId is not None:
        parent = db.query(models.TreeNode).filter(models.TreeNode.id == data.parentId).first()
        if not parent:
            raise ValueError("Invalid parent ID")
        node.parent_id = data.parentId

    db.commit()
    db.refresh(node)
    return node

# Delete a specific node by ID
def delete_node_by_id(db: Session, node_id: int):
    node = db.query(models.TreeNode).filter(models.TreeNode.id == node_id).first()
    if not node:
        return False 
    db.delete(node)
    db.commit()
    return True