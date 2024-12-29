from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.database import master_db_engine, Base
from fastapi.middleware.cors import CORSMiddleware
from app.error.exception_handlers import error_exception_handlers, http_exception_handlers
from app.generator.routers import generate_crud_router
from app.generator.schema import generate_schemas
from app.generator.models import get_models
from app.api import *
from fastapi.responses import PlainTextResponse
from fastapi.staticfiles import StaticFiles
from app.api.upload import upload


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with master_db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(lifespan=lifespan,
              title="SucceedEx Placements and Training API", version="0.1.0")

# Register custom exception handlers
error_exception_handlers(app)
http_exception_handlers(app)

# Serve static files
app.mount("/public", StaticFiles(directory="public"), name="public")

# CORS settings
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the SucceedEx Placements and Training API"}


@app.get("/health", tags=["Root"])
def health_check():
    return {"status": True}

@app.get("/metrics")
def get_metrics():
    return PlainTextResponse("Running")

app.include_router(upload.router)

# Dynamically generate and include routers for all models
models = get_models()
print(models)
for model in models:
    schemas = generate_schemas(model)
    model_name = model.__name__
    config = model_configs.get(model_name, {})
    required_roles = config.get("required_roles", {})
    custom_routes = config.get("custom_routes", [])
    router = generate_crud_router(
        model, schemas, required_roles, custom_routes)
    app.include_router(router, prefix=f"/api/{model.__tablename__}")


