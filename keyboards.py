# keyboards.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database import db
from config import BOT_USERNAME

def get_main_menu() -> InlineKeyboardMarkup:
    """Create main menu buttons"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🎁 Bonus", callback_data="bonus"),
                InlineKeyboardButton(text="💰 Balance", callback_data="balance")
            ],
            [
                InlineKeyboardButton(text="👥 Refer & Earn", callback_data="refer"),
                InlineKeyboardButton(text="💸 Withdraw", callback_data="withdraw")
            ],
            [
                InlineKeyboardButton(text="📞 Contact Admin", url="https://t.me/TRUSTED_X_RAJ")
            ]
        ]
    )

def get_bonus_menu() -> InlineKeyboardMarkup:
    """Create bonus menu buttons"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🎁 Claim Bonus", callback_data="claim_bonus")],
            [InlineKeyboardButton(text="🔙 Menu", callback_data="main_menu")]
        ]
    )

def get_back_button() -> InlineKeyboardMarkup:
    """Create back button"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Back", callback_data="main_menu")]
        ]
    )

def get_admin_menu() -> InlineKeyboardMarkup:
    """Create admin menu buttons"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="👥 Users", callback_data="admin_users"),
                InlineKeyboardButton(text="💸 Withdrawals", callback_data="admin_withdrawals")
            ],
            [
                InlineKeyboardButton(text="➕ Add Button", callback_data="admin_add_button"),
                InlineKeyboardButton(text="➖ Remove Button", callback_data="admin_remove_button")
            ],
            [
                InlineKeyboardButton(text="📢 Broadcast", callback_data="admin_broadcast"),
                InlineKeyboardButton(text="📋 Channel List", callback_data="admin_channels")
            ]
        ]
    )

async def get_dynamic_channel_buttons() -> InlineKeyboardMarkup:
    """Create dynamic channel buttons from database"""
    channels = await db.get_channels()
    
    if not channels:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="✅ Verify Join", callback_data="verify_join")]
            ]
        )
    
    builder = InlineKeyboardBuilder()
    
    # Add channel buttons (2 per row)
    for i in range(0, len(channels), 2):
        row_buttons = []
        for j in range(2):
            if i + j < len(channels):
                channel = channels[i + j]
                row_buttons.append(
                    InlineKeyboardButton(
                        text=f"📢 {channel['button_name']}", 
                        url=channel['channel_link']
                    )
                )
        builder.row(*row_buttons)
    
    # Add verify button
    builder.row(InlineKeyboardButton(text="✅ Verify Join", callback_data="verify_join"))
    
    return builder.as_markup()

def get_admin_back_button() -> InlineKeyboardMarkup:
    """Create admin back button"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Back", callback_data="admin_menu")]
        ]
    )

def get_withdrawal_admin_buttons(withdrawal_id: str) -> InlineKeyboardMarkup:
    """Create withdrawal approval/rejection buttons"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Approve", callback_data=f"approve_{withdrawal_id}"),
                InlineKeyboardButton(text="❌ Reject", callback_data=f"reject_{withdrawal_id}")
            ]
        ]
    )

async def get_remove_channel_buttons() -> InlineKeyboardMarkup:
    """Create remove channel buttons"""
    channels = await db.get_channels()
    
    if not channels:
        return get_admin_back_button()
    
    builder = InlineKeyboardBuilder()
    
    for channel in channels:
        builder.row(
            InlineKeyboardButton(
                text=f"❌ Remove {channel['button_name']}", 
                callback_data=f"remove_channel_{str(channel['_id'])}"
            )
        )
    
    builder.row(InlineKeyboardButton(text="🔙 Back", callback_data="admin_menu"))
    
    return builder.as_markup()