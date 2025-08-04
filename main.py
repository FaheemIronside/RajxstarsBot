# main.py
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage

from config import *
from database import db
from channel_checker import channel_checker
from handlers import BotHandlers
from states import AdminStates, WithdrawStates

# Bot setup
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Initialize handlers
handlers = BotHandlers(bot)

# Register command handlers
@dp.message(Command("start"))
async def start_handler(message):
    await handlers.start_command(message)

@dp.message(Command("adminhelp"))
async def admin_help_handler(message):
    await handlers.admin_help(message)

# Register callback handlers
@dp.callback_query(F.data == "verify_join")
async def verify_join_handler(callback):
    await handlers.verify_join(callback)

@dp.callback_query(F.data == "bonus")
async def bonus_menu_handler(callback):
    await handlers.bonus_menu(callback)

@dp.callback_query(F.data == "claim_bonus")
async def claim_bonus_handler(callback):
    await handlers.claim_bonus(callback)

@dp.callback_query(F.data == "balance")
async def balance_handler(callback):
    await handlers.show_balance(callback)

@dp.callback_query(F.data == "refer")
async def refer_handler(callback):
    await handlers.refer_menu(callback)

@dp.callback_query(F.data == "withdraw")
async def withdraw_handler(callback, state):
    await handlers.withdraw_menu(callback, state)

@dp.callback_query(F.data == "main_menu")
async def main_menu_handler(callback):
    await handlers.main_menu(callback)

# Admin callback handlers
@dp.callback_query(F.data == "admin_users")
async def admin_users_handler(callback):
    await handlers.admin_users(callback)

@dp.callback_query(F.data == "admin_withdrawals")
async def admin_withdrawals_handler(callback):
    await handlers.admin_withdrawals(callback)

@dp.callback_query(F.data == "admin_add_button")
async def admin_add_button_handler(callback, state):
    await handlers.admin_add_button(callback, state)

@dp.callback_query(F.data == "admin_remove_button")
async def admin_remove_button_handler(callback):
    await handlers.admin_remove_button(callback)

@dp.callback_query(F.data == "admin_broadcast")
async def admin_broadcast_handler(callback, state):
    await handlers.admin_broadcast(callback, state)

@dp.callback_query(F.data == "admin_channels")
async def admin_channels_handler(callback):
    await handlers.admin_channels(callback)

@dp.callback_query(F.data == "admin_menu")
async def admin_menu_handler(callback):
    await handlers.admin_menu_callback(callback)

# Remove channel callback
@dp.callback_query(F.data.startswith("remove_channel_"))
async def remove_channel_handler(callback):
    await handlers.remove_channel_callback(callback)

# Withdrawal approval/rejection callbacks
@dp.callback_query(F.data.startswith("approve_"))
async def approve_withdrawal_handler(callback):
    await handlers.approve_withdrawal(callback)

@dp.callback_query(F.data.startswith("reject_"))
async def reject_withdrawal_handler(callback):
    await handlers.reject_withdrawal(callback)

# State handlers for withdrawal
@dp.message(WithdrawStates.waiting_for_username)
async def withdraw_username_handler(message, state):
    await handlers.process_withdraw_username(message, state)

@dp.message(WithdrawStates.waiting_for_amount)
async def withdraw_amount_handler(message, state):
    await handlers.process_withdraw_amount(message, state)

# Admin state handlers
@dp.message(AdminStates.waiting_for_channel)
async def admin_channel_handler(message, state):
    await handlers.process_channel_link(message, state)

@dp.message(AdminStates.waiting_for_button_name)
async def admin_button_handler(message, state):
    await handlers.process_button_name(message, state)

@dp.message(AdminStates.waiting_for_broadcast)
async def admin_broadcast_message_handler(message, state):
    await handlers.process_broadcast(message, state)

# Error handler
@dp.error()
async def error_handler(event, exception):
    logger.error(f"Error occurred: {exception}")
    return True

# Main function
async def main():
    try:
        # Initialize database
        await db.init_db()
        logger.info("Database initialized")
        
        # Start pyrogram client
        await channel_checker.start_client()
        
        # Start bot
        logger.info("Starting RajXStars Bot...")
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
    finally:
        # Stop pyrogram client
        await channel_checker.stop_client()
        await db.close_connection()

if __name__ == "__main__":
    asyncio.run(main())