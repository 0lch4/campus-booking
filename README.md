# campus-booking
Project for EMPPP course

## Database

```
cp .env.example .env
docker compose up -d db
```

Postgres runs on `localhost:5432`, data is kept in the `pgdata` volume. Scripts in `db/init/` run only on first start (empty volume), to rerun them: `docker compose down -v`.
