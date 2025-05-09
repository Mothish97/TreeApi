# app/utils.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app import models
from collections import defaultdict

# ─────────────────────────────────────────────────────────────────────────────
# Constructs tree hierarchy from flat list of nodes in O(n)
# ─────────────────────────────────────────────────────────────────────────────
def build_tree(nodes):
    """
    Constructs tree hierarchy from flat list of nodes in O(n).

    :param nodes: List of TreeNode objects.
    :return: Tree as nested list of dictionaries.
    """
    children_map = defaultdict(list)
    id_to_node = {}

    # First pass: create basic node dict and group by parent
    for node in nodes:
        node_dict = {"id": node.id, "label": node.label, "children": []}
        id_to_node[node.id] = node_dict
        children_map[node.parent_id].append(node_dict)

    # Second pass: assign children
    for node in id_to_node.values():
        node["children"] = children_map.get(node["id"], [])

    return children_map[None]


# ─────────────────────────────────────────────────────────────────────────────
# Checks if a node is a descendant of another (async version)
# ─────────────────────────────────────────────────────────────────────────────
async def is_descendant(db: AsyncSession, descendant_id: int, ancestor_id: int) -> bool:
    """
    Checks if a node is a descendant of another to prevent cyclic parent-child relationships.

    :param db: Async SQLAlchemy DB session.
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

        result = await db.execute(
            select(models.TreeNode.id).filter(models.TreeNode.parent_id == current)
        )
        child_ids = [row[0] for row in result.fetchall()]

        if descendant_id in child_ids:
            return True

        stack.extend(child_ids)

    return False


# ─────────────────────────────────────────────────────────────────────────────
# Recursively locate and return the subtree rooted at a specific node ID
# ─────────────────────────────────────────────────────────────────────────────
def find_subtree_by_id(tree, target_id):
    """
    Recursively locate and return the subtree rooted at a specific node ID.

    This function walks through the tree structure, which is a list of nested dictionaries
    (each representing a node with potential children), and returns the first match found
    based on the target_id.

    Parameters:
        tree (list[dict]): The tree structure to search, typically the result of build_tree().
        target_id (int): The ID of the node to locate in the tree.

    Returns:
        dict: The subtree rooted at the matching node.
        None: If no matching node is found in the tree.
    """
    for node in tree:
        if node["id"] == target_id:
            return node
        child = find_subtree_by_id(node["children"], target_id)
        if child:
            return child
    return None
