# test_tree.py

import httpx

# Toggle between environments:
#BASE_URL = "http://127.0.0.1:8000"
BASE_URL = "https://treeapi.onrender.com"

def find_node(node_list, node_id):
    """Recursively search for a node with a given ID in a tree."""
    for node in node_list:
        if node["id"] == node_id:
            return node
        result = find_node(node.get("children", []), node_id)
        if result:
            return result
    return None

def test_non_intrusive_flow():
    # Step 1: Create root node
    res1 = httpx.post(f"{BASE_URL}/api/tree", json={"label": "test-root-node"})
    assert res1.status_code == 201
    root_data = res1.json()["data"]
    root_id = root_data["id"]

    # Step 2: Create child node under the root
    res2 = httpx.post(f"{BASE_URL}/api/tree", json={"label": "test-child-node", "parentId": root_id})
    assert res2.status_code == 201
    child_data = res2.json()["data"]
    child_id = child_data["id"]

    # Step 3: Get tree and validate structure
    tree_res = httpx.get(f"{BASE_URL}/api/tree")
    assert tree_res.status_code == 200
    tree_data = tree_res.json()["data"]

    assert find_node(tree_data, root_id)
    assert find_node(tree_data, child_id)

    # Step 4: Delete child and then parent
    del_child = httpx.delete(f"{BASE_URL}/api/tree/{child_id}")
    assert del_child.status_code == 200

    del_root = httpx.delete(f"{BASE_URL}/api/tree/{root_id}")
    assert del_root.status_code == 200

    print("test_non_intrusive_flow passed")

def test_update_parent_and_validate_tree():
    # Step 1: Create two root nodes
    res1 = httpx.post(f"{BASE_URL}/api/tree", json={"label": "test-parent"})
    assert res1.status_code == 201
    parent_id = res1.json()["data"]["id"]

    res2 = httpx.post(f"{BASE_URL}/api/tree", json={"label": "test-child"})
    assert res2.status_code == 201
    child_id = res2.json()["data"]["id"]

    # Step 2: Update child to make parent_id its parent
    update_res = httpx.put(
        f"{BASE_URL}/api/tree/{child_id}",
        json={"label": "test-child", "parentId": parent_id}
    )
    assert update_res.status_code == 200

    # Step 3: Fetch parent node and check for child
    get_parent = httpx.get(f"{BASE_URL}/api/tree/{parent_id}")
    assert get_parent.status_code == 200
    parent_data = get_parent.json()["data"]
    assert parent_data["id"] == parent_id
    assert any(child["id"] == child_id for child in parent_data["children"])

    # Step 4: Clean up
    del_child = httpx.delete(f"{BASE_URL}/api/tree/{child_id}")
    assert del_child.status_code == 200

    del_parent = httpx.delete(f"{BASE_URL}/api/tree/{parent_id}")
    assert del_parent.status_code == 200

    print("test_update_parent_and_validate_tree passed")


def test_cannot_set_node_as_its_own_parent():
    # Step 1: Create a node
    create_response = httpx.post(f"{BASE_URL}/api/tree", json={"label": "self-parent-test"})
    assert create_response.status_code == 201

    node_data = create_response.json()["data"]
    node_id = node_data["id"]

    try:
        # Step 2: Try to update the node to have itself as parent
        update_response = httpx.put(
            f"{BASE_URL}/api/tree/{node_id}",
            json={"label": "invalid-update", "parentId": node_id}
        )

        # Step 3: Validate that a 400 Bad Request was returned
        assert update_response.status_code == 400
        assert "cannot be its own parent" in update_response.text.lower() or "invalidparentid" in update_response.text.lower()
    
    finally:
        # Step 4: Cleanup - delete the node
        delete_response = httpx.delete(f"{BASE_URL}/api/tree/{node_id}")
        assert delete_response.status_code == 200
        print("test_cannot_set_node_as_its_own_parent passed")

def test_create_with_invalid_parent_id():
    response = httpx.post(f"{BASE_URL}/api/tree", json={"label": "invalid-parent", "parentId": 9999})
    assert response.status_code == 400
    assert "parent id" in response.text.lower() and "invalid" in response.text.lower()
    print("test_create_with_invalid_parent_id passed")


def test_cannot_create_circular_relationship():
    # Create A
    res_a = httpx.post(f"{BASE_URL}/api/tree", json={"label": "A"})
    node_a = res_a.json()["data"]
    id_a = node_a["id"]

    # Create B with parent A
    res_b = httpx.post(f"{BASE_URL}/api/tree", json={"label": "B", "parentId": id_a})
    id_b = res_b.json()["data"]["id"]

    try:
        # Try to update A's parent to B (which would create a cycle)
        res_update = httpx.put(f"{BASE_URL}/api/tree/{id_a}", json={"label": "A", "parentId": id_b})
        assert res_update.status_code == 400
        assert "descendant" in res_update.text.lower()
    finally:
        # Cleanup
        httpx.delete(f"{BASE_URL}/api/tree/{id_a}")
        httpx.delete(f"{BASE_URL}/api/tree/{id_b}")
        print("test_cannot_create_circular_relationship passed")


if __name__ == "__main__":
    test_non_intrusive_flow()
    test_update_parent_and_validate_tree()
    test_cannot_set_node_as_its_own_parent()
    test_create_with_invalid_parent_id()
    test_cannot_create_circular_relationship()
