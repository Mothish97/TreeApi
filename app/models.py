# app/models.py

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

# ─────────────────────────────────────────────────────────────────────────────
# TreeNode model: Represents a hierarchical tree structure using self-reference
# Each node may have a parent and can contain multiple children (recursive).
# ─────────────────────────────────────────────────────────────────────────────
class TreeNode(Base):
    __tablename__ = "nodes"  # Name of the table in the database

    # ─────────────────────────────────────────────────────────────────────────
    # Unique identifier for the node (Primary Key)
    # ─────────────────────────────────────────────────────────────────────────
    id = Column(Integer, primary_key=True, index=True)

    # ─────────────────────────────────────────────────────────────────────────
    # Descriptive label for the node (Required)
    # ─────────────────────────────────────────────────────────────────────────
    label = Column(String, nullable=False)

    # ─────────────────────────────────────────────────────────────────────────
    # Optional foreign key pointing to the parent node's ID
    # A null value indicates this node is a root node
    # ─────────────────────────────────────────────────────────────────────────
    parent_id = Column(Integer, ForeignKey("nodes.id"), nullable=True)

    # ─────────────────────────────────────────────────────────────────────────
    # Reference to the parent node
    # remote_side=[id] helps SQLAlchemy resolve the self-referential direction
    # ─────────────────────────────────────────────────────────────────────────
    parent = relationship("TreeNode", remote_side=[id], backref="children", lazy="selectin")

    # Notes:
    # - `remote_side=[id]` is required to resolve ambiguity in self-reference
    # - `backref="children"` creates a reverse-access relationship
    # - `lazy="selectin"` allows async-safe eager loading for nested tree access
