# campus-booking
Project for EMPPP course

## Database

```
cp .env.example .env
docker compose up -d db
```

Postgres runs on `localhost:5432`, data is kept in the `pgdata` volume. Scripts in `db/init/` run only on first start (empty volume), to rerun them: `docker compose down -v`.

## Lint + pre-commit

Backend uses ruff, frontend uses ESLint + Prettier. Hooks run on every commit.

```
cd backend
python -m venv .venv
.venv\Scripts\activate        # Linux / macOS: source .venv/bin/activate
pip install -e ".[dev]"
cd ../frontend
npm ci
cd ..
pre-commit install
```

To check all files: `pre-commit run --all-files`
