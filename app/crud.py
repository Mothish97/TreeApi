from sqlalchemy.orm import Session
from app import models, schemas

# Create a new node in the database
def create_node(db: Session, node: schemas.TreeNodeCreate):
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

# Retrieve all nodes from the database
def delete_all_nodes(db: Session):
    db.query(models.TreeNode).delete()
    db.commit()
    db.close()
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
