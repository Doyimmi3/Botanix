import motor.motor_asyncio
from typing import Optional, Dict, Any, List
import logging
from contextlib import asynccontextmanager
from datetime import datetime

logger = logging.getLogger("db")

class Database:
    _client: Optional[motor.motor_asyncio.AsyncIOMotorClient] = None
    _db = None
    
    @classmethod
    @asynccontextmanager
    async def get_client(cls):
        if cls._client is None:
            raise RuntimeError("Database not initialized")
        yield cls._client
    
    @classmethod
    async def init(cls, uri: str):
        try:
            cls._client = motor.motor_asyncio.AsyncIOMotorClient(
                uri, serverSelectionTimeoutMS=5000
            )
            await cls._client.admin.command('ping')
            cls._db = cls._client["discord_bot"]
            logger.info("✅ MongoDB connection established")
        except Exception as e:
            logger.error(f"❌ MongoDB connection failed: {e}")
            cls._db = None
    
    @classmethod
    async def close(cls):
        if cls._client:
            cls._client.close()
            logger.info("🔒 MongoDB connection closed")
    
    @classmethod
    def collection(cls, name: str):
        """✅ SAFE: Returns None if DB not ready"""
        if cls._db is None:
            return None
        return cls._db[name]

    # ✅ SAFE METHODS - No truth testing errors
    @classmethod
    async def safe_log_moderation(cls, guild_id: int, action: str, target_id: int, 
                                moderator_id: int, reason: str = ""):
        collection = cls.collection("moderation_logs")
        if collection is None:
            logger.warning("DB offline - moderation log skipped")
            return
        try:
            await collection.insert_one({
                "guild_id": guild_id, "action": action, 
                "target_id": target_id, "moderator_id": moderator_id,
                "reason": reason, "timestamp": datetime.utcnow()
            })
        except Exception as e:
            logger.error(f"Moderation log error: {e}")

    @classmethod
    async def safe_add_warning(cls, guild_id: int, user_id: int, reason: str, 
                             moderator_id: int) -> Dict:
        collection = cls.collection("warnings")
        if collection is None:
            logger.warning("DB offline - warning skipped")
            return {"warning_id": "DB_OFFLINE"}
        
        try:
            warns = await cls.safe_get_warnings(guild_id, user_id)
            warning = {
                "guild_id": guild_id, "user_id": user_id, "reason": reason,
                "moderator_id": moderator_id, "timestamp": datetime.utcnow(),
                "warning_id": f"{guild_id}-{len(warns) + 1}"
            }
            await collection.insert_one(warning)
            return warning
        except Exception as e:
            logger.error(f"Warning error: {e}")
            return {"warning_id": "ERROR"}

    @classmethod
    async def safe_get_warnings(cls, guild_id: int, user_id: int) -> List[Dict]:
        collection = cls.collection("warnings")
        if collection is None:
            return []
        try:
            return await collection.find({"guild_id": guild_id, "user_id": user_id}).to_list(None)
        except Exception as e:
            logger.error(f"Get warnings error: {e}")
            return []
