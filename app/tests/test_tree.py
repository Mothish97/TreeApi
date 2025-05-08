from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_and_get_tree():
    # Create a root node
    response = client.post("/api/tree", json={
        "label": "test-root",
        "parentId": None
    })
    assert response.status_code == 200
    root = response.json()
    assert root["label"] == "test-root"
    assert root["children"] == []

    # Get the tree and check root is included
    response = client.get("/api/tree")
    assert response.status_code == 200
    tree = response.json()
    assert any(node["label"] == "test-root" for node in tree)
