# TreeApi
FastApi to execute tree CUD operations


# Tree API – FastAPI Project

This is a simple tree-building HTTP API built using **FastAPI** and **SQLite**, supporting:

- ✅ Create nodes (with parent-child structure)
- ✅ Fetch the entire tree as nested JSON
- ✅ Delete all nodes (reset)

---

## Project Structure

```
app/
├── api/
│   └── tree.py         # Route handlers
├── crud.py             # DB interaction logic
├── database.py         # DB session and engine
├── models.py           # SQLAlchemy models
├── schemas.py          # Pydantic request/response models
main.py                 # FastAPI app entry point
.env                    # DB and secret config
requirements.txt
README.md
```

---

## How to Run

### 1. Install Python packages

```bash
pip install -r requirements.txt
```

### 2. Run the FastAPI server

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```
http://127.0.0.1:8000
```

Swagger UI (interactive API docs):

```
http://127.0.0.1:8000/docs
```

---

## API Endpoints

| Method | Route        | Description                  |
|--------|--------------|------------------------------|
| POST   | `/api/tree`  | Add a node                   |
| GET    | `/api/tree`  | Fetch the full tree          |
| DELETE | `/api/tree`  | Delete all nodes (reset)     |

---

## Example Payload (POST)

```json
{
  "label": "Root",
  "parentId": null
}
```

To create a child:

```json
{
  "label": "Child",
  "parentId": 1
}
```

---

## Notes

- Uses **SQLite** for simplicity (`tree.db`)
- Designed for clarity, not authentication (JWT ready if needed)
- Swagger docs are auto-generated

---

## Requirements

See `requirements.txt` for dependencies.

---

## Running Tests

Use `pytest` to run the included unit test:

```bash
python -m pytest
```

This test will:
- Create a root node
- Confirm the API responds with HTTP 200
- Validate that the label is stored correctly
