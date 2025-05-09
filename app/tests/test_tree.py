# test_tree.py

import httpx

# Toggle between environments:
BASE_URL = "http://127.0.0.1:8000"
# BASE_URL = "https://treeapi.onrender.com"

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

    print("✅ test_non_intrusive_flow passed")

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

    print("✅ test_update_parent_and_validate_tree passed")


if __name__ == "__main__":
    test_non_intrusive_flow()
    test_update_parent_and_validate_tree()
