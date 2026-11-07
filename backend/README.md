# Backend

FastAPI app. Config is read from env vars or `.env` (in `backend/` or repo root, see `.env.example`).

## Run locally

```
python -m venv .venv
.venv\Scripts\activate        # Linux / macOS: source .venv/bin/activate
pip install -e .
uvicorn app.main:app --reload
```

- API: http://localhost:8000/api
- Docs: http://localhost:8000/api/docs
- Health: http://localhost:8000/api/health, returns 503 if the db is unavailable

Start the db first (see the root README). When running `uvicorn` outside Docker, set `POSTGRES_HOST=localhost` in `.env`, because `db` only resolves inside the Docker network.
