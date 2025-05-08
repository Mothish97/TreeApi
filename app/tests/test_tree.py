import httpx

#Toggle between environments by commenting/uncommenting:
#BASE_URL = "http://127.0.0.1:8000"           #local server
BASE_URL = "https://treeapi.onrender.com"     #deployed cloud API

def test_create_and_get_tree():
    # Create a root node
    response = httpx.post(f"{BASE_URL}/api/tree", json={
        "label": "test-root",
        "parentId": None
    })
    assert response.status_code == 200
    root = response.json()
    assert root["label"] == "test-root"
    assert root["children"] == []

    # Get the tree
    response = httpx.get(f"{BASE_URL}/api/tree")
    assert response.status_code == 200
    tree = response.json()
    assert any(node["label"] == "test-root" for node in tree)

def test_root_route():
    response = httpx.get(f"{BASE_URL}/")
    assert response.status_code == 200
    assert response.json() == {
        "message": "Tree API is running! Visit /docs for Swagger UI."
    }
