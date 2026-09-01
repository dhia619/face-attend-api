from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.config import get_settings
from src.database import engine
from src.auth.router import auth_router
from src.users.router import user_router
from src.employees.router import employee_router
from src.rbac.router import rbac_router
from src.departments.router import department_router
from src.devices.router import device_router
from src.recognition.router import recognition_router
from src.attendance.router import attendance_router
from src.core.logging import setup_logging
from src.core.exception_handlers import VALIDATION_MESSAGES

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

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    errors = []

    for error in exc.errors():
        field = error["loc"][-1] if error["loc"] else "unknown"
        error_type = error["type"]

        message = VALIDATION_MESSAGES.get(error_type, "Invalid value")

        errors.append({
            "field": field,
            "message": message
        })

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": errors}
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

app.include_router(
    router=recognition_router,
    prefix=f"{settings.BASE_API_PATH}/recognition",
    tags=["Recognition"]
)

app.include_router(
    router=user_router,
    prefix=f"{settings.BASE_API_PATH}/users",
    tags=["Users"]
)

app.include_router(
    router=attendance_router,
    prefix=f"{settings.BASE_API_PATH}/attendance",
    tags=["Attendance"]
)