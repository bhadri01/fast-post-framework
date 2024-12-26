# Backend

## Run the project

```
POSTGRESQL_DATABASE_MASTER_URL=postgresql+asyncpg://root:dotmail123@postgres/succeedex POSTGRESQL_DATABASE_SLAVE_URL=postgresql+asyncpg://root:dotmail123@postgres/succeedex SECRET_KEY=2ae7ea295c404bacbca5f608b621f8dd fastapi dev main.py
```