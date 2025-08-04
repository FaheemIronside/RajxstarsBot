# channel_checker.py
from pyrogram import Client
from pyrogram.errors import UserNotParticipant, ChannelPrivate, UsernameNotOccupied, UsernameInvalid
from database import db
from config import *

class ChannelChecker:
    def __init__(self):
        self.app = Client("rajxstars_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

    async def start_client(self):
        """Start pyrogram client"""
        try:
            await self.app.start()
            logger.info("Pyrogram client started successfully")
        except Exception as e:
            logger.error(f"Failed to start pyrogram client: {e}")

    async def stop_client(self):
        """Stop pyrogram client"""
        try:
            await self.app.stop()
            logger.info("Pyrogram client stopped")
        except Exception as e:
            logger.error(f"Failed to stop pyrogram client: {e}")

    def extract_channel_username(self, channel_link: str) -> str:
        """Extract channel username from link"""
        if "/joinchat/" in channel_link:
            return channel_link
        
        # Extract username from t.me link
        parts = channel_link.rstrip('/').split('/')
        username = parts[-1]
        
        if not username.startswith('@'):
            username = f"@{username}"
        
        return username

    async def check_user_membership(self, user_id: int) -> tuple[bool, list]:
        """Check if user is member of all required channels"""
        channels = await db.get_channels()
        if not channels:
            logger.info("No channels found in database")
            return True, []
        
        logger.info(f"Checking membership for user {user_id} in {len(channels)} channels")
        not_joined = []
        
        try:
            for channel in channels:
                channel_link = channel["channel_link"]
                channel_username = self.extract_channel_username(channel_link)
                
                try:
                    member = await self.app.get_chat_member(channel_username, user_id)
                    if member.status in ["left", "kicked"]:
                        logger.info(f"User {user_id} not in channel {channel_username}: {member.status}")
                        not_joined.append(channel['button_name'])
                    else:
                        logger.info(f"User {user_id} is member of {channel_username}: {member.status}")
                except (UserNotParticipant, ChannelPrivate, UsernameNotOccupied, UsernameInvalid) as e:
                    logger.error(f"Channel check error for {channel_username}: {e}")
                    not_joined.append(channel['button_name'])
                except Exception as e:
                    logger.error(f"Unexpected error checking {channel_username}: {e}")
                    not_joined.append(channel['button_name'])
            
            is_member = len(not_joined) == 0
            logger.info(f"User {user_id} membership check result: {is_member}")
            return is_member, not_joined
        except Exception as e:
            logger.error(f"Membership check error: {e}")
            return False, []

# Create global channel checker instance
channel_checker = ChannelChecker()