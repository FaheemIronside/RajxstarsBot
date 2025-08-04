# database.py
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
import pymongo
from bson import ObjectId
from config import *

class Database:
    def __init__(self):
        self.client = AsyncIOMotorClient(MONGO_URI)
        self.db = self.client[DB_NAME]
        self.users = self.db[USERS_COLLECTION]
        self.channels = self.db[CHANNELS_COLLECTION]
        self.withdrawals = self.db[WITHDRAWALS_COLLECTION]

    async def init_db(self):
        """Initialize database collections with indexes"""
        try:
            # Create indexes
            await self.users.create_index("user_id", unique=True)
            await self.channels.create_index("channel_link", unique=True)
            await self.withdrawals.create_index("user_id")
            await self.withdrawals.create_index("withdrawal_id", unique=True)
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Database init error: {e}")

    async def get_user(self, user_id: int) -> Optional[Dict]:
        """Get user from database"""
        return await self.users.find_one({"user_id": user_id})

    async def create_user(self, user_id: int, username: str, first_name: str, referred_by: int = None):
        """Create new user in database"""
        user_data = {
            "user_id": user_id,
            "username": username,
            "first_name": first_name,
            "balance": 0,
            "total_referrals": 0,
            "last_bonus_claim": None,
            "joined_at": datetime.utcnow(),
            "referred_by": referred_by
        }
        
        try:
            await self.users.insert_one(user_data)
            
            # Give referral bonus to referrer
            if referred_by:
                await self.users.update_one(
                    {"user_id": referred_by},
                    {
                        "$inc": {"balance": REFERRAL_BONUS, "total_referrals": 1}
                    }
                )
                logger.info(f"Referral bonus given to user {referred_by}")
            
            return user_data
        except pymongo.errors.DuplicateKeyError:
            return await self.get_user(user_id)

    async def update_user_balance(self, user_id: int, amount: int):
        """Update user balance"""
        await self.users.update_one(
            {"user_id": user_id},
            {"$inc": {"balance": amount}}
        )

    async def claim_daily_bonus(self, user_id: int) -> bool:
        """Claim daily bonus if eligible"""
        user = await self.get_user(user_id)
        if not user:
            return False
        
        now = datetime.utcnow()
        last_claim = user.get("last_bonus_claim")
        
        if last_claim and (now - last_claim).total_seconds() < 86400:  # 24 hours
            return False
        
        await self.users.update_one(
            {"user_id": user_id},
            {
                "$inc": {"balance": DAILY_BONUS},
                "$set": {"last_bonus_claim": now}
            }
        )
        return True

    async def get_remaining_bonus_time(self, user_id: int) -> str:
        """Get remaining time for next bonus claim"""
        user = await self.get_user(user_id)
        if not user or not user.get("last_bonus_claim"):
            return "00h 00m 00s"
        
        last_claim = user["last_bonus_claim"]
        next_claim = last_claim + timedelta(hours=24)
        remaining = next_claim - datetime.utcnow()
        
        if remaining.total_seconds() <= 0:
            return "00h 00m 00s"
        
        hours, remainder = divmod(int(remaining.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}h {minutes:02d}m {seconds:02d}s"

    async def get_channels(self) -> List[Dict]:
        """Get all channels from database"""
        cursor = self.channels.find({})
        channels = await cursor.to_list(length=None)
        logger.info(f"Retrieved {len(channels)} channels from database")
        return channels

    async def add_channel(self, channel_link: str, button_name: str):
        """Add channel to database"""
        channel_data = {
            "channel_link": channel_link,
            "button_name": button_name,
            "added_at": datetime.utcnow()
        }
        
        try:
            result = await self.channels.insert_one(channel_data)
            logger.info(f"Channel added: {button_name} - {channel_link}")
            return str(result.inserted_id)
        except pymongo.errors.DuplicateKeyError:
            logger.warning(f"Channel already exists: {channel_link}")
            return False

    async def remove_channel(self, channel_id: str):
        """Remove channel from database"""
        try:
            result = await self.channels.delete_one({"_id": ObjectId(channel_id)})
            logger.info(f"Channel removed: {channel_id}")
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error removing channel: {e}")
            return False

    async def create_withdrawal_request(self, user_id: int, username: str, amount: int) -> str:
        """Create withdrawal request"""
        withdrawal_id = f"WD{datetime.utcnow().strftime('%Y%m%d%H%M%S')}{user_id}"
        
        withdrawal_data = {
            "withdrawal_id": withdrawal_id,
            "user_id": user_id,
            "username": username,
            "amount": amount,
            "status": "pending",
            "created_at": datetime.utcnow()
        }
        
        await self.withdrawals.insert_one(withdrawal_data)
        logger.info(f"Withdrawal request created: {withdrawal_id}")
        return withdrawal_id

    async def update_withdrawal_status(self, withdrawal_id: str, status: str):
        """Update withdrawal status"""
        result = await self.withdrawals.update_one(
            {"withdrawal_id": withdrawal_id},
            {"$set": {"status": status, "processed_at": datetime.utcnow()}}
        )
        return result.modified_count > 0

    async def get_withdrawal(self, withdrawal_id: str):
        """Get withdrawal by ID"""
        return await self.withdrawals.find_one({"withdrawal_id": withdrawal_id})

    async def get_total_users(self) -> int:
        """Get total number of users"""
        return await self.users.count_documents({})

    async def get_withdrawal_stats(self):
        """Get withdrawal statistics"""
        pending = await self.withdrawals.count_documents({"status": "pending"})
        approved = await self.withdrawals.count_documents({"status": "approved"})
        rejected = await self.withdrawals.count_documents({"status": "rejected"})
        return pending, approved, rejected

    async def close_connection(self):
        """Close database connection"""
        self.client.close()

# Create global database instance
db = Database()