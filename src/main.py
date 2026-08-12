from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import get_settings
from src.database import engine
from src.auth.router import auth_router
from src.employees.router import employee_router
from src.rbac.router import rbac_router
from src.departments.router import department_router
from src.devices.router import device_router
from src.core.logging import setup_logging

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):

    setup_logging()

    yield

    await engine.dispose()

app = FastAPI(lifespan=lifespan, title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get(f"{settings.BASE_API_PATH}/")
def root():
    return {"app_name": settings.APP_NAME, "app_version": settings.APP_VERSION}

app.include_router(
    router=auth_router,
    prefix=f"{settings.BASE_API_PATH}/auth",
    tags=["Authentication"]
)

app.include_router(
    router=employee_router,
    prefix=f"{settings.BASE_API_PATH}/employees",
    tags=["Employees"]
)

app.include_router(
    router=department_router,
    prefix=f"{settings.BASE_API_PATH}/departments",
    tags=["Departments"]
)

app.include_router(
    router=rbac_router,
    prefix=f"{settings.BASE_API_PATH}/rbac",
    tags=["RBAC"]
)

app.include_router(
    router=device_router,
    prefix=f"{settings.BASE_API_PATH}/devices",
    tags=["Devices"]
)