# TreeApi
A modern FastAPI-based HTTP API to **create, read, update, and delete nodes** in a hierarchical tree structure (parent-child). Built with **async SQLAlchemy**, supports both **SQLite** (local dev) and **PostgreSQL** (production on Render).

# Python 3.10+ is required to run this project

# For Public Access URL

- Http: [https://treeapi.onrender.com](https://treeapi.onrender.com)
- Swagger: [https://treeapi.onrender.com/docs](https://treeapi.onrender.com/docs)

## Features

- Create nodes with optional `parentId`
- Fetch individual nodes or the **entire tree** in nested format
- Update node `label` or reassign parent (with cycle protection)
- Delete nodes individually or wipe all
- Fully async with `asyncpg` / `aiosqlite`
- Deployed on [Render](https://render.com)
- Includes automated tests (with edge case coverage)

---

## 📁 Project Structure

```
app/
├── api/
│   └── tree.py         # FastAPI route handlers
├── crud.py             # Async DB operations
├── database.py         # DB engine/session logic
├── models.py           # SQLAlchemy models (self-referential)
├── schemas.py          # Pydantic request/response models
├── utils.py            # Recursive tree builders
├── exceptions.py       # Custom exception classes
tests/
├── test_tree.py        # API integration and edge case tests
main.py                 # FastAPI app entry point
requirements.txt
.env                    # DB + secret config (local vs cloud)
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


| Method | Route               | Description                         |
|--------|---------------------|-------------------------------------|
| POST   | `/api/tree`         | Create a node                       |
| GET    | `/api/tree`         | Fetch entire tree                   |
| GET    | `/api/tree/{id}`    | Fetch subtree rooted at given node  |
| PUT    | `/api/tree/{id}`    | Update label or parentId            |
| DELETE | `/api/tree/{id}`    | Delete a specific node              |
| DELETE | `/api/tree`         | Delete all nodes                    |

---


## Example API Payloads

### Create a root node:
```json
{
  "label": "Root",
  "parentId": null
}
```

### Create a child node:
```json
{
  "label": "Child A",
  "parentId": 1
}
```

---


## Requirements

See `requirements.txt` for dependencies.

---


## Running Tests

```bash
python -m pytest
```

Tests cover:
- Create, read, update, delete
- Invalid parent references
- Cycle prevention (A → B → A)
- Node cleanup after tests

---

## Additional Highlights

- `selectinload` used for async-safe eager loading of children
- `remote_side=[id]` for correct parent-child resolution
- Test coverage includes edge cases and rollback safety
- Designed for dev clarity with potential for production hardening

## Future Improvements

- [ ] JWT authentication & user-scoped tree views
- [ ] Docker Compose + PostgreSQL dev image
- [ ] Optional rate limiting or caching

##  Author
Mothish Raj — [@Mothish97](https://github.com/Mothish97)