from fastapi import FastAPI 

from app.routers import (
    lazy_router
)


app = FastAPI()


app.include_router(lazy_router.router)
