# app/exceptions.py

class InvalidParentIDException(Exception):
    """
    Raised when a given parent ID does not correspond to an existing node
    or would create a cyclic relationship.

    Attributes:
        parent_id (int): The invalid parent ID provided.
        message (str): Explanation of the error.
    """
    def __init__(self, parent_id: int | str):
        self.parent_id = parent_id
        self.message = f"Parent ID {parent_id} is invalid."
        super().__init__(self.message)


class NodeNotFoundException(Exception):
    """
    Raised when a requested node is not found in the database.

    Attributes:
        node_id (int): The ID of the missing node.
        message (str): Explanation of the error.
    """
    def __init__(self, node_id: int):
        self.node_id = node_id
        self.message = f"Node with ID {node_id} not found."
        super().__init__(self.message)
