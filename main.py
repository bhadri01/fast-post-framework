from fastapi import FastAPI, Request, HTTPException
from contextlib import asynccontextmanager
from app.core.database import master_db_engine, Base
from fastapi.middleware.cors import CORSMiddleware
from app.utils.response_utils import send_json_response
from app.api.college import router as college_router
from app.error.exception_handlers import error_exception_handlers,unexpected_exception_handlers

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with master_db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(lifespan=lifespan,title="SucceedEx Placements and Training API", version="0.1.0")

# Register custom exception handlers
error_exception_handlers(app)
unexpected_exception_handlers(app)

# CORS settings
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if f"{exc.status_code}:" in exc.detail[:5]:
        exc.detail = exc.detail.replace(f"{exc.status_code}:", "").strip()
    return send_json_response(exc.status_code, exc.detail)


@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the SucceedEx Placements and Training API"}


@app.get("/health", tags=["Root"])
def health_check():
    return {"status": True}

app.include_router(college_router, prefix="/colleges", tags=["Colleges"])

