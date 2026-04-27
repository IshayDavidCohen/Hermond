import logging
from time import sleep
from typing import Optional, Dict, Any

from pymongo import MongoClient, errors
from datetime import datetime

logger = logging.getLogger(__name__)


class Database:
    def __init__(self, database_name: str, connection_uri: str):
        self.mongo_client = MongoClient(connection_uri)
        self.health: Optional[Dict[str, Any]] = None
        if self._ensure_mongodb_connection():
            self.db = self.mongo_client[database_name]

    def insert_one(self, collection: str, document: Dict) -> Any:
        return self.db[collection].insert_one(document)

    def find_one(self, collection: str, query: Dict, subfield_query: Optional[Dict] = None) -> Optional[Dict]:
        return self.db[collection].find_one(query, subfield_query)

    def find_all(self, collection: str, query: Optional[Dict] = None, subfield_query: Optional[Dict] = None) -> Any:
        if query is None:
            query = {}
        return self.db[collection].find(query, subfield_query)

    def update_one(self, collection: str, query: Dict, update: Dict, operation: str = "$set") -> Any:
        return self.db[collection].update_one(query, {operation: update})

    def delete_one(self, collection: str, query: Dict) -> Any:
        return self.db[collection].delete_one(query)

    def health_check(self) -> Dict[str, Any]:
        self.health = self._check_mongodb_health()
        return self.health

    def close(self) -> None:
        self.mongo_client.close()

    def _ensure_mongodb_connection(self, max_retries: int = 3, retry_delay: int = 2) -> Optional[bool]:
        for attempt in range(max_retries):
            try:
                self.mongo_client.admin.command("ping")
                logger.info("MongoDB connection established on attempt %d", attempt + 1)
                return True
            except (errors.ConnectionFailure, errors.ServerSelectionTimeoutError) as e:
                logger.warning("Attempt %d failed: %s", attempt + 1, e)
                if attempt < max_retries - 1:
                    sleep(retry_delay)
                else:
                    logger.error("All connection attempts failed")
                    return None
        return None

    def _check_mongodb_health(self) -> Dict[str, Any]:
        health_status: Dict[str, Any] = {
            "is_connected": False,
            "timestamp": datetime.now().isoformat(),
            "details": {},
        }
        try:
            self.mongo_client.admin.command("ping")
            health_status["is_connected"] = True
            server_info = self.mongo_client.admin.command("serverStatus")
            health_status["details"] = {
                "version": server_info.get("version", "unknown"),
                "uptime_seconds": server_info.get("uptime", 0),
                "connections": server_info.get("connections", {}).get("current", 0),
            }
        except (errors.ConnectionFailure, errors.ServerSelectionTimeoutError) as e:
            health_status["error"] = str(e)
        return health_status
