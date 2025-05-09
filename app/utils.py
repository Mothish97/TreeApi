# app/utils.py

from sqlalchemy.orm import Session
from app import models

def build_tree(nodes, parent_id=None):
    """
    Recursively constructs a tree structure from a flat list of TreeNodes.

    :param nodes: List of TreeNode objects.
    :param parent_id: Parent node ID to match.
    :return: Nested tree as a list of dictionaries.
    """
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


def is_descendant(db: Session, descendant_id: int, ancestor_id: int) -> bool:
    """
    Checks if a node is a descendant of another to prevent cyclic parent-child relationships.

    :param db: SQLAlchemy DB session.
    :param descendant_id: Potential child node.
    :param ancestor_id: Potential ancestor node.
    :return: True if descendant_id is under ancestor_id.
    """
    visited = set()
    stack = [ancestor_id]
    while stack:
        current = stack.pop()
        if current in visited:
            continue
        visited.add(current)

        children = db.query(models.TreeNode.id).filter(models.TreeNode.parent_id == current).all()
        child_ids = [c[0] for c in children]

        if descendant_id in child_ids:
            return True

        stack.extend(child_ids)
    return False
