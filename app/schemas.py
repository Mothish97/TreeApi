from typing import List, Optional, Union
from pydantic import BaseModel, ConfigDict

# ────────────────────────────────────────────────────────────────
# Input schema for creating or updating a node
# Used in POST and PUT endpoints (/tree, /tree/{id})
# ────────────────────────────────────────────────────────────────
class TreeNodeCreate(BaseModel):
    """
    Schema representing the payload to create or update a node.
    
    Fields:
        label (str): Required label or name of the node.
        parentId (Optional[int]): Optional parent ID. If None, node is considered a root.
    """
    label: str
    parentId: Optional[int] = None


# ────────────────────────────────────────────────────────────────
# Output schema for a single node with recursive children
# Used in GET responses (/tree, /tree/{id})
# ────────────────────────────────────────────────────────────────
class TreeNodeResponse(BaseModel):
    """
    Schema representing a single node with its recursive children.

    Fields:
        id (int): Unique identifier of the node.
        label (str): Label or name of the node.
        children (List[TreeNodeResponse]): List of child nodes.
    """
    id: int
    label: str
    children: List["TreeNodeResponse"] = []

    model_config = ConfigDict(from_attributes=True)


# ────────────────────────────────────────────────────────────────
# Output schema for DELETE ALL operation
# Used in DELETE /tree response
# ────────────────────────────────────────────────────────────────
class TreeNodeDeleteAll(BaseModel):
    """
    Schema representing the success status of a delete-all operation.

    Fields:
        isDeleted (bool): Indicates if the operation succeeded.
    """
    isDeleted: bool
    model_config = ConfigDict(from_attributes=True)


# ────────────────────────────────────────────────────────────────
# Generic response wrapper for all API responses
# Applies to all endpoints for consistency in responses
# ────────────────────────────────────────────────────────────────
class ResponseWrapper(BaseModel):
    """
    Schema for standardizing API responses.

    Fields:
        code (int): HTTP status code or application-specific status.
        message (str): Human-readable description of the response.
        data (Union[...]): Payload data or result. Can be a node, list, bool, or None.
    """
    code: int
    message: str
    data: Union[
        TreeNodeResponse,
        List[TreeNodeResponse],
        TreeNodeDeleteAll,
        bool,
        None
    ]


# ────────────────────────────────────────────────────────────────
# Resolve forward references in recursive models
# Required when a model refers to itself (TreeNodeResponse.children)
# ────────────────────────────────────────────────────────────────
TreeNodeResponse.model_rebuild()
