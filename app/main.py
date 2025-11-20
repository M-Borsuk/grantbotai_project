from fastapi import FastAPI

from app.logger import logger
from app.routers import generate, history

app = FastAPI()

logger.info("Starting FastAPI application...")

app.include_router(generate.router)
logger.info("Included generate router")

app.include_router(history.router)
logger.info("Included history router")
