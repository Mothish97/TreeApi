from typing import List, Optional
from pydantic import BaseModel, ConfigDict

# For POST request input
class TreeNodeCreate(BaseModel):
    label: str
    parentId: Optional[int] = None

# For GET response output (recursive structure)
class TreeNodeResponse(BaseModel):
    id: int
    label: str
    children: List["TreeNodeResponse"] = []

class TreeNodeDeleteAll(BaseModel):
    isDeleted: bool

    model_config = ConfigDict(from_attributes=True)
