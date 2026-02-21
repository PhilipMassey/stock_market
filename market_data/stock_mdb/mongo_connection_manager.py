"""
MongoDB Connection Manager for Dash App
Place this file in your percent_app directory and import it in your pages.
"""

from pymongo import MongoClient
from functools import lru_cache
import time


class MongoConnectionManager:
    """Singleton MongoDB connection manager to prevent connection pool exhaustion"""

    _instance = None
    _client = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_client(self, max_retries=3, retry_delay=1):
        """Get MongoDB client with retry logic"""
        if self._client is None:
            for attempt in range(max_retries):
                try:
                    # Configure connection pool settings
                    self._client = MongoClient(
                        host='localhost',
                        port=27017,
                        maxPoolSize=50,  # Increase pool size
                        minPoolSize=10,
                        maxIdleTimeMS=45000,
                        waitQueueTimeoutMS=10000,
                        serverSelectionTimeoutMS=10000,
                        connectTimeoutMS=10000,
                        socketTimeoutMS=45000,
                    )
                    # Test the connection
                    self._client.admin.command('ping')
                    # print(f"✓ MongoDB connection established (attempt {attempt + 1})")
                    break
                except Exception as e:
                    # print(f"✗ MongoDB connection attempt {attempt + 1} failed: {e}")
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                    else:
                        raise
        return self._client

    def get_database(self, db_name='stock_market'):
        """Get database instance"""
        client = self.get_client()
        return client[db_name]

    def close(self):
        """Close MongoDB connection"""
        if self._client:
            self._client.close()
            self._client = None
            # print("MongoDB connection closed")


# Global instance
_mongo_manager = MongoConnectionManager()


def get_mongo_client():
    """Get the shared MongoDB client"""
    return _mongo_manager.get_client()


def get_mongo_database(db_name='stock_market'):
    """Get the shared MongoDB database"""
    return _mongo_manager.get_database(db_name)


@lru_cache(maxsize=1)
def get_sectors_industry_cached():
    """
    Cached wrapper for get_sectors_industry to prevent multiple simultaneous calls
    This will only execute once and cache the result
    """
    try:
        import sys
        sys.path.insert(0, '/Users/philipmassey/stock_market')
        import apis.seeking_alpha.symbol_financial_info.mdb_in_out as mdb_in_out

        # print("Loading sector/industry data from MongoDB...")
        result = mdb_in_out.get_sectors_industry()
        # print(f"✓ Loaded {len(result)} sector/industry records")
        return result
    except Exception as e:
        # print(f"✗ Error loading sector/industry data: {e}")
        import pandas as pd
        return pd.DataFrame()  # Return empty DataFrame as fallback


# Pre-load data on module import (but with better connection handling)
def get_sector_data():
    """Lazy loader for sector data to avoid circular imports"""
    return get_sectors_industry_cached()