from asyncio import sleep
from typing import Optional, Dict, Any
from pymongo import MongoClient, errors
from datetime import datetime


class Database:
    def __init__(self, database_name: str, connection_uri: str):
        self.mongo_client = MongoClient(connection_uri)
        self.health = None

        if self.__ensure_mongodb_connection():
            self.db = self.mongo_client[database_name]

    def insert_one(self, collection, document):
        return self.db[collection].insert_one(document)

    def find_one(self, collection, query, subfield_query=None):
        return self.db[collection].find_one(query, subfield_query)

    def find_all(self, collection, query: Optional[Dict] = None, subfield_query=None):
        if query is None:
            query = {}
        return self.db[collection].find(query, subfield_query)

    def update_one(self, collection, query, update):
        return self.db[collection].update_one(query, {'$set': update})

    def delete_one(self, collection, query):
        return self.db[collection].delete_one(query)

    def health_check(self):
        self.health = self.__check_mongodb_health()
        return self.health

    def last_health_check(self):
        return self.health

    # Private Methods
    def __ensure_mongodb_connection(self, max_retries: int = 3, retry_delay: int = 2) -> Optional[bool]:
        """
        Attempts to establish MongoDB connection with retries
        """
        for attempt in range(max_retries):
            try:
                self.mongo_client.admin.command('ping')
                print(f"MongoDB connection established on attempt {attempt + 1}")
                return True

            except (errors.ConnectionFailure, errors.ServerSelectionTimeoutError) as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    print(f"Retrying in {retry_delay} seconds...")
                    sleep(retry_delay)
                else:
                    print("All connection attempts failed")
                    return None
        return None

    def __check_mongodb_health(self) -> Dict[str, Any]:
        health_status = {
            "is_connected": False,
            "timestamp": datetime.utcnow(),
            "details": {}
        }

        try:
            # Check basic connectivity
            self.mongo_client.admin.command('ping')
            health_status["is_connected"] = True

            # Get server info
            server_info = self.mongo_client.admin.command('serverStatus')
            health_status["details"] = {
                "version": server_info.get("version", "unknown"),
                "uptime_seconds": server_info.get("uptime", 0),
                "connections": server_info.get("connections", {}).get("current", 0),
                "active_clients": server_info.get("globalLock", {}).get("activeClients", {}).get("total", 0)
            }

        except (errors.ConnectionFailure, errors.ServerSelectionTimeoutError) as e:
            health_status["error"] = str(e)

        return health_status
