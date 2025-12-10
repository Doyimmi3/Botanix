from utils.db import Database
from typing import List, Optional
from datetime import datetime  # ✅ FIXED: Add this import

class PrefixManager:
    DEFAULT_PREFIX = "!"
    
    @classmethod
    async def get_prefix(cls, guild_id: int) -> str:
        """Get guild prefix or default."""
        collection = Database.collection("prefixes")
        if collection is None:
            return cls.DEFAULT_PREFIX
        
        prefix_doc = await collection.find_one({"guild_id": guild_id})
        return prefix_doc.get("prefix", cls.DEFAULT_PREFIX) if prefix_doc else cls.DEFAULT_PREFIX
    
    @classmethod
    async def set_prefix(cls, guild_id: int, prefix: str):
        """Set new guild prefix."""
        collection = Database.collection("prefixes")
        if collection is None:
            return False
        
        await collection.update_one(
            {"guild_id": guild_id},
            {"$set": {"prefix": prefix[:5], "updated_at": datetime.utcnow()}},  # ✅ Now works
            upsert=True
        )
        return True
    
    @classmethod
    async def reset_prefix(cls, guild_id: int):
        """Reset to default prefix."""
        collection = Database.collection("prefixes")
        if collection is None:
            return False
        
        await collection.delete_one({"guild_id": guild_id})
        return True
