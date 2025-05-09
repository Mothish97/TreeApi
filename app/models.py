# app/models.py

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

# ─────────────────────────────────────────────────────────────────────────────
# SQLAlchemy model representing a tree node in the database
#─────────────────────────────────────────────────────────────────────────────
class TreeNode(Base):
    __tablename__ = "nodes"  # Table name in the database

    # Unique identifier for each node (Primary Key)
    id = Column(Integer, primary_key=True, index=True)

    # The name or label of the node (required)
    label = Column(String, nullable=False)

    # Foreign key referencing the parent node (nullable for root nodes)
    parent_id = Column(Integer, ForeignKey('nodes.id'), nullable=True)

    # Relationship to access child nodes (self-referential one-to-many)
    children = relationship("TreeNode")
