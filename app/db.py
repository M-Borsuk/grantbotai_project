from pymongo import MongoClient
from pymongo.collection import Collection

from app.config import settings
from app.logger import logger


class Mongo:
    def __init__(self):
        self.client = MongoClient(settings.mongo_uri)
        self.db = self.client[settings.mongo_db_name]

    @property
    def documents(self) -> Collection:
        return self.db["documents"]

    @property
    def history(self) -> Collection:
        return self.db["history"]


logger.info("Connecting to MongoDB...")
mongo = Mongo()
logger.info("Connected to MongoDB.")
