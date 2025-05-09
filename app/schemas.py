from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from typing import Union

# For POST request input
class TreeNodeCreate(BaseModel):
    label: str
    parentId: Optional[int] = None

# For GET response output (recursive structure)
class TreeNodeResponse(BaseModel):
    id: int
    label: str
    children: List["TreeNodeResponse"] = []

# For Delete all data
class TreeNodeDeleteAll(BaseModel):
    isDeleted: bool
    model_config = ConfigDict(from_attributes=True)

# Adding common response wrapper with error code and message
class ResponseWrapper(BaseModel):
    code: int
    message: str
    data: Union[TreeNodeResponse, List[TreeNodeResponse], TreeNodeDeleteAll,bool, None]