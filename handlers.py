# handlers.py
from datetime import datetime
from aiogram import types, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from config import *
from database import db
from keyboards import *
from channel_checker import channel_checker
from states import AdminStates, WithdrawStates

class BotHandlers:
    def __init__(self, bot):
        self.bot = bot

    async def start_command(self, message: Message):
        """Handle /start command"""
        user_id = message.from_user.id
        username = message.from_user.username or "Unknown"
        first_name = message.from_user.first_name or "User"
        
        # Check for referral
        referred_by = None
        if message.text and len(message.text.split()) > 1:
            try:
                referred_by = int(message.text.split()[1])
                logger.info(f"User {user_id} referred by {referred_by}")
            except ValueError:
                pass
        
        # Get or create user
        user = await db.get_user(user_id)
        if not user:
            user = await db.create_user(user_id, username, first_name, referred_by)
            logger.info(f"New user created: {user_id}")
        else:
            logger.info(f"Existing user: {user_id}")
        
        # Check if user joined all channels
        channels = await db.get_channels()
        if channels:
            is_member, not_joined = await channel_checker.check_user_membership(user_id)
            if not is_member:
                # Show channel join message
                welcome_text = f"""**🌟 Welcome to RajXStars Bot! 🌟**

**👋 Hey {first_name}!** 

**🚀 Get ready to earn amazing rewards!**

**✨ Join our channels to unlock:**
• **🎁 Daily bonus rewards**
• **💰 Referral earnings**  
• **🌟 Exclusive content**
• **💸 Easy withdrawals**

**📢 Please join all channels below and click verify:**"""
                
                keyboard = await get_dynamic_channel_buttons()
                await message.reply(welcome_text, reply_markup=keyboard, parse_mode="Markdown")
                return
        
        # Show main menu directly
        welcome_text = f"""**🎉 Welcome Back, {first_name}! 🎉**

**⭐ RajXStars Bot** - **Your Gateway to Earning! ⭐**

**🚀 What you can do:**
• **🎁 Claim daily bonuses**
• **💰 Check your balance**  
• **👥 Refer friends & earn**
• **💸 Withdraw your earnings**

**✨ Choose an option below to get started:**"""
        
        await message.reply(welcome_text, reply_markup=get_main_menu(), parse_mode="Markdown")

    async def admin_help(self, message: Message):
        """Handle /adminhelp command"""
        if message.from_user.id != ADMIN_ID:
            return
        
        admin_text = """**👑 Welcome Boss! 👑**

**🔧 Here Is Your Admin System**

**🎛️ Control Panel Features:**
• **👥 Manage users**
• **💸 Handle withdrawals**
• **➕ Add channel buttons**
• **➖ Remove channel buttons**
• **📢 Broadcast messages**
• **📋 View channel list**

**⚡ Choose an option below:**"""
        
        await message.reply(admin_text, reply_markup=get_admin_menu(), parse_mode="Markdown")

    async def verify_join(self, callback: types.CallbackQuery):
        """Handle verify join callback"""
        user_id = callback.from_user.id
        
        is_member, not_joined = await channel_checker.check_user_membership(user_id)
        
        if is_member:
            # User joined all channels
            first_name = callback.from_user.first_name or "User"
            
            welcome_text = f"""**🎉 Congratulations {first_name}! 🎉**

**✅ Successfully verified!**

**⭐ Welcome to RajXStars Bot ⭐**

**🚀 You can now:**
• **🎁 Claim your daily bonus**
• **💰 Check your balance**
• **👥 Refer friends & earn**
• **💸 Withdraw your rewards**

**🌟 Let's start earning together!**"""
            
            await callback.message.edit_text(welcome_text, reply_markup=get_main_menu(), parse_mode="Markdown")
        else:
            not_joined_text = ", ".join(not_joined)
            await callback.answer(f"❌ Please join these channels first: {not_joined_text}", show_alert=True)

    async def bonus_menu(self, callback: types.CallbackQuery):
        """Handle bonus menu callback"""
        bonus_text = """**🔥 Claim Your Bonus 🔥**

**🎁 Daily Bonus Available:** **1⭐**

**🕑 Claim Bonus Again In 24 Hours**

**⚡ Bonus Features:**
• **🌟 Get 1 star daily**
• **⏰ 24-hour reset timer**  
• **🎯 Build your balance**
• **💎 Consistent rewards**

**🎊 Ready to claim your reward?**"""
        
        await callback.message.edit_text(bonus_text, reply_markup=get_bonus_menu(), parse_mode="Markdown")

    async def claim_bonus(self, callback: types.CallbackQuery):
        """Handle claim bonus callback"""
        user_id = callback.from_user.id
        
        if await db.claim_daily_bonus(user_id):
            success_text = """**🎉 Congratulations! 🎉**

**⭐ You received 1⭐ as Daily Bonus! ⭐**

**✨ Bonus claimed successfully!**

**⏳ Come back after 24 hours to claim again.**

**🚀 Keep earning and growing your balance!**"""
            
            back_keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="🔙 Back", callback_data="bonus")]
                ]
            )
            
            await callback.message.edit_text(success_text, reply_markup=back_keyboard, parse_mode="Markdown")
        else:
            remaining_time = await db.get_remaining_bonus_time(user_id)
            await callback.answer(
                f"🎁 RajXStars Bot\n⏳ You have already claimed your bonus!\n⏱️ Wait: {remaining_time}",
                show_alert=True
            )

    async def show_balance(self, callback: types.CallbackQuery):
        """Handle balance callback"""
        user_id = callback.from_user.id
        user = await db.get_user(user_id)
        
        if not user:
            await callback.answer("❌ User not found!", show_alert=True)
            return
        
        now = datetime.utcnow()
        balance_text = f"""**👤 Name:** **{user['first_name']}**
**🆔 User ID:** **{user_id}**

**💵 Balance:** **{user['balance']}⭐**

**⌚️ Update On:** **{now.strftime('%I:%M %p')}**
**📆 Date:** **{now.strftime('%Y-%m-%d')}**

**🌟 Keep earning and growing!**"""
        
        await callback.message.edit_text(balance_text, reply_markup=get_back_button(), parse_mode="Markdown")

    async def refer_menu(self, callback: types.CallbackQuery):
        """Handle refer menu callback"""
        user_id = callback.from_user.id
        user = await db.get_user(user_id)
        
        if not user:
            await callback.answer("❌ User not found!", show_alert=True)
            return
        
        refer_text = f"""**🔥 Refer and Earn 🔥**

**✅ Per Refer:** **1⭐**
**👥 Your Total Referrals:** **{user['total_referrals']}**

**🔗 Your Referral Link:**
`https://t.me/{BOT_USERNAME}?start={user_id}`

**🚀 How it works:**
• **📤 Share your link**
• **👥 Friends join via your link**  
• **💰 You earn 1⭐ per referral**
• **🎯 No limits, unlimited earning!**

**📈 Start sharing and earning now!**"""
        
        await callback.message.edit_text(refer_text, reply_markup=get_back_button(), parse_mode="Markdown")

    async def withdraw_menu(self, callback: types.CallbackQuery, state: FSMContext):
        """Handle withdraw menu callback"""
        user_id = callback.from_user.id
        user = await db.get_user(user_id)
        
        if not user:
            await callback.answer("❌ User not found!", show_alert=True)
            return
        
        if user['balance'] < MIN_WITHDRAWAL:
            insufficient_text = f"""**❌ Insufficient Balance!**

**💰 Your balance:** **{user['balance']}⭐**
**🎯 Minimum required:** **{MIN_WITHDRAWAL}⭐**

**📈 How to earn more:**
• **🎁 Claim daily bonus (1⭐)**
• **👥 Refer friends (1⭐ each)**
• **🔄 Keep coming back daily**

**💪 You're on the right track! Keep earning!**"""
            
            await callback.message.edit_text(insufficient_text, reply_markup=get_back_button(), parse_mode="Markdown")
            return
        
        withdraw_text = f"""**⚡ Make Sure To Send Stars To Real Username ⚡**

**🌟 RajXStars Withdrawal System 🌟**

**📋 Withdrawal Info:**
• **🎯 Minimum Order:** **{MIN_WITHDRAWAL}⭐**
• **📥 Type:** **Telegram Stars**
• **⚡ Fast Processing**
• **✅ Secure & Reliable**

**👤 Please enter the correct username** **👇**

**📝 Format:** **@username (with @)**"""
        
        await callback.message.edit_text(withdraw_text, parse_mode="Markdown")
        await state.set_state(WithdrawStates.waiting_for_username)

    async def main_menu(self, callback: types.CallbackQuery):
        """Handle main menu callback"""
        first_name = callback.from_user.first_name or "User"
        
        welcome_text = f"""**🎉 Welcome Back, {first_name}! 🎉**

**⭐ RajXStars Bot** - **Your Gateway to Earning! ⭐**

**🚀 What you can do:**
• **🎁 Claim daily bonuses**
• **💰 Check your balance**  
• **👥 Refer friends & earn**
• **💸 Withdraw your earnings**

**✨ Choose an option below to get started:**"""
        
        await callback.message.edit_text(welcome_text, reply_markup=get_main_menu(), parse_mode="Markdown")

    # Withdraw states handlers
    async def process_withdraw_username(self, message: Message, state: FSMContext):
        """Process withdrawal username"""
        username = message.text.strip()
        
        # Validate username format
        if not username.startswith("@") or len(username) < 2:
            await message.reply(
                "**❌ Invalid username format!**\n\n"
                "**📝 Please use format:** **@username**\n"
                "**✅ Example:** **@faheemironside**",
                parse_mode="Markdown"
            )
            return
        
        await state.update_data(username=username)
        
        amount_text = f"""**⭐ Please enter the Stars amount now:**

**💰 Enter the amount you want to withdraw**

**📋 Requirements:**
• **🎯 Minimum:** **{MIN_WITHDRAWAL}⭐**
• **📊 Based on your balance**
• **🔢 Enter numbers only**

**💎 Example:** **17**"""
        
        await message.reply(amount_text, parse_mode="Markdown")
        await state.set_state(WithdrawStates.waiting_for_amount)

    async def process_withdraw_amount(self, message: Message, state: FSMContext):
        """Process withdrawal amount"""
        try:
            amount = int(message.text.strip())
        except ValueError:
            await message.reply(
                "**❌ Invalid amount!**\n\n"
                "**🔢 Please enter numbers only**\n"
                "**✅ Example:** **17**",
                parse_mode="Markdown"
            )
            return
        
        user_id = message.from_user.id
        user = await db.get_user(user_id)
        
        if not user:
            await message.reply("**❌ User not found!**", parse_mode="Markdown")
            await state.clear()
            return
        
        if amount < MIN_WITHDRAWAL:
            await message.reply(
                f"**❌ Minimum withdrawal is {MIN_WITHDRAWAL}⭐**\n\n"
                f"**📝 You entered:** **{amount}⭐**\n"
                f"**🎯 Required:** **{MIN_WITHDRAWAL}⭐**",
                parse_mode="Markdown"
            )
            return
        
        if amount > user['balance']:
            await message.reply(
                f"**❌ Insufficient balance!**\n\n"
                f"**💰 Your balance:** **{user['balance']}⭐**\n"
                f"**📝 Requested:** **{amount}⭐**",
                parse_mode="Markdown"
            )
            return
        
        # Get stored username
        data = await state.get_data()
        username = data.get('username')
        
        # Deduct amount from user balance
        await db.update_user_balance(user_id, -amount)
        
        # Create withdrawal request
        withdrawal_id = await db.create_withdrawal_request(user_id, username, amount)
        
        # Send confirmation to user
        success_text = f"""**✅ Order successfully placed!**

**🆔 Order ID:** **{withdrawal_id}**
**🎉 Your request has been submitted to admin.**
**⏳ You'll be notified once it's fulfilled.**

**📋 Order Details:**
• **👤 Username:** **{username}**
• **⭐ Amount:** **{amount}⭐**
• **📅 Date:** **{datetime.utcnow().strftime('%Y-%m-%d %H:%M')}**

**💫 Thank you for using RajXStars Bot!**"""
        
        await message.reply(success_text, parse_mode="Markdown")
        
        # Send notification to admin
        admin_text = f"""**📥 New Withdrawal Request**

**👤 User:** **{username}**
**🆔 User ID:** **{user_id}**
**⭐ Total:** **{amount}⭐**
**🔖 Order ID:** **{withdrawal_id}**
**📅 Date:** **{datetime.utcnow().strftime('%Y-%m-%d %H:%M')}**"""
        
        try:
            await self.bot.send_message(
                ADMIN_ID, 
                admin_text, 
                reply_markup=get_withdrawal_admin_buttons(withdrawal_id), 
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(f"Failed to send admin notification: {e}")
        
        await state.clear()

    # Admin handlers
    async def admin_users(self, callback: types.CallbackQuery):
        """Handle admin users callback"""
        if callback.from_user.id != ADMIN_ID:
            return
        
        total_users = await db.get_total_users()
        
        users_text = f"""**👥 User Statistics**

**📊 Total Users:** **{total_users}**

**📈 Growth Metrics:**
• **🎯 Active users earning daily**
• **💰 Total rewards distributed**
• **🚀 Referral network growing**

**🔧 Admin Controls Available**"""
        
        await callback.message.edit_text(users_text, reply_markup=get_admin_back_button(), parse_mode="Markdown")

    async def admin_withdrawals(self, callback: types.CallbackQuery):
        """Handle admin withdrawals callback"""
        if callback.from_user.id != ADMIN_ID:
            return
        
        # Get withdrawal statistics
        pending, approved, rejected = await db.get_withdrawal_stats()
        
        withdrawals_text = f"""**💸 Withdrawal Statistics**

**📊 Request Status:**
• **⏳ Pending:** **{pending}**
• **✅ Approved:** **{approved}**  
• **❌ Rejected:** **{rejected}**

**📈 Total Requests:** **{pending + approved + rejected}**

**🔧 Manage withdrawals from notifications**"""
        
        await callback.message.edit_text(withdrawals_text, reply_markup=get_admin_back_button(), parse_mode="Markdown")

    async def admin_add_button(self, callback: types.CallbackQuery, state: FSMContext):
        """Handle admin add button callback"""
        if callback.from_user.id != ADMIN_ID:
            return
        
        add_text = """**➕ Add Channel Button**

**📢 Send channel link in format:**
**https://t.me/channel_name**

**✅ Valid Examples:**
• **https://t.me/RajXStars**
• **https://t.me/TechUpdates**  
• **https://t.me/CryptoNews**

**📝 Please send the channel link:**"""
        
        await callback.message.edit_text(add_text, parse_mode="Markdown")
        await state.set_state(AdminStates.waiting_for_channel)

    async def admin_remove_button(self, callback: types.CallbackQuery):
        """Handle admin remove button callback"""
        if callback.from_user.id != ADMIN_ID:
            return
        
        channels = await db.get_channels()
        
        if not channels:
            no_channels_text = """**➖ Remove Channel**

**❌ No channels found**

**📝 Add some channels first using 'Add Button' option**"""
            
            await callback.message.edit_text(no_channels_text, reply_markup=get_admin_back_button(), parse_mode="Markdown")
            return
        
        remove_text = "**➖ Remove Channel**\n\n**📋 Channel List:**\n\n"
        
        for channel in channels:
            remove_text += f"**📢 {channel['button_name']}**\n**🔗** {channel['channel_link']}\n**🆔 ID:** `{str(channel['_id'])}`\n\n"
        
        await callback.message.edit_text(remove_text, reply_markup=await get_remove_channel_buttons(), parse_mode="Markdown")

    async def admin_broadcast(self, callback: types.CallbackQuery, state: FSMContext):
        """Handle admin broadcast callback"""
        if callback.from_user.id != ADMIN_ID:
            return
        
        broadcast_text = """**📢 Broadcast Message**

**📝 Send the message you want to broadcast to all users:**

**✨ Features:**
• **📤 Send to all registered users**
• **🎨 Supports text formatting**
• **📊 Get delivery statistics**
• **⚡ Fast bulk delivery**

**💬 Type your message below:**"""
        
        await callback.message.edit_text(broadcast_text, parse_mode="Markdown")
        await state.set_state(AdminStates.waiting_for_broadcast)

    async def admin_channels(self, callback: types.CallbackQuery):
        """Handle admin channels callback"""
        if callback.from_user.id != ADMIN_ID:
            return
        
        channels = await db.get_channels()
        
        if not channels:
            channels_text = """**📄 Channel List**

**❌ No channels configured**

**📝 Use 'Add Button' to add channels**"""
        else:
            channels_text = "**📄 Channel List**\n\n"
            for i, channel in enumerate(channels, 1):
                channels_text += f"**{i}.** **📢 {channel['button_name']}**\n"
                channels_text += f"**🔗** {channel['channel_link']}\n"
                channels_text += f"**🆔 ID:** `{str(channel['_id'])}`\n"
                channels_text += f"**📅 Added:** **{channel['added_at'].strftime('%Y-%m-%d')}**\n\n"
        
        await callback.message.edit_text(channels_text, reply_markup=get_admin_back_button(), parse_mode="Markdown")

    async def admin_menu_callback(self, callback: types.CallbackQuery):
        """Handle admin menu callback"""
        if callback.from_user.id != ADMIN_ID:
            return
        
        admin_text = """**👑 Welcome Boss! 👑**

**🔧 Here Is Your Admin System**

**🎛️ Control Panel Features:**
• **👥 Manage users**
• **💸 Handle withdrawals**
• **➕ Add channel buttons**
• **➖ Remove channel buttons**
• **📢 Broadcast messages**
• **📋 View channel list**

**⚡ Choose an option below:**"""
        
        await callback.message.edit_text(admin_text, reply_markup=get_admin_menu(), parse_mode="Markdown")

    # Admin state handlers
    async def process_channel_link(self, message: Message, state: FSMContext):
        """Process channel link from admin"""
        if message.from_user.id != ADMIN_ID:
            return
        
        channel_link = message.text.strip()
        
        # Validate channel link
        if not channel_link.startswith("https://t.me/"):
            await message.reply(
                "**❌ Invalid channel link format!**\n\n"
                "**✅ Use format:** **https://t.me/channel_name**",
                parse_mode="Markdown"
            )
            return
        
        await state.update_data(channel_link=channel_link)
        
        button_text = """**🏷️ Button Name:**

**📝 Enter the name for this button:**

**✅ Good Examples:**
• **Main Channel**
• **Updates Channel**  
• **News Channel**
• **Crypto Updates**

**💡 Keep it short and clear!**"""
        
        await message.reply(button_text, parse_mode="Markdown")
        await state.set_state(AdminStates.waiting_for_button_name)

    async def process_button_name(self, message: Message, state: FSMContext):
        """Process button name from admin"""
        if message.from_user.id != ADMIN_ID:
            return
        
        button_name = message.text.strip()
        
        if len(button_name) > 30:
            await message.reply(
                "**❌ Button name too long!**\n\n"
                f"**📏 Maximum:** **30 characters**\n"
                f"**📝 Current:** **{len(button_name)} characters**",
                parse_mode="Markdown"
            )
            return
        
        data = await state.get_data()
        channel_link = data.get('channel_link')
        
        result = await db.add_channel(channel_link, button_name)
        
        if result:
            success_text = f"""**✅ Button Added Successfully!**

**📢 Channel:** **{button_name}**
**🔗 Link:** **{channel_link}**
**🆔 Channel ID:** `{result}`

**🎉 The button is now active in /start menu!**

**⚡ Users will need to join this channel to access the bot.**"""
            
            await message.reply(success_text, parse_mode="Markdown")
        else:
            await message.reply(
                "**❌ Channel already exists!**\n\n"
                "**📝 This channel link is already added.**",
                parse_mode="Markdown"
            )
        
        await state.clear()

    async def process_broadcast(self, message: Message, state: FSMContext):
        """Process broadcast message from admin"""
        if message.from_user.id != ADMIN_ID:
            return
        
        broadcast_message = message.text
        
        # Get all users
        cursor = db.users.find({}, {"user_id": 1})
        users = await cursor.to_list(length=None)
        
        total_users = len(users)
        successful_sends = 0
        failed_sends = 0
        
        progress_message = await message.reply(
            f"**📤 Broadcasting...**\n\n"
            f"**👥 Total Users:** **{total_users}**\n"
            f"**✅ Sent:** **0**\n"
            f"**❌ Failed:** **0**",
            parse_mode="Markdown"
        )
        
        for i, user in enumerate(users):
            try:
                await self.bot.send_message(user['user_id'], broadcast_message, parse_mode="Markdown")
                successful_sends += 1
            except Exception as e:
                failed_sends += 1
                logger.error(f"Failed to send broadcast to {user['user_id']}: {e}")
            
            # Update progress every 10 users
            if (i + 1) % 10 == 0 or (i + 1) == total_users:
                try:
                    await progress_message.edit_text(
                        f"**📤 Broadcasting...**\n\n"
                        f"**👥 Total Users:** **{total_users}**\n"
                        f"**✅ Sent:** **{successful_sends}**\n"
                        f"**❌ Failed:** **{failed_sends}**\n"
                        f"**📊 Progress:** **{i + 1}/{total_users}**",
                        parse_mode="Markdown"
                    )
                except:
                    pass
        
        # Final report
        final_text = f"""**✅ Broadcast Completed!**

**📊 Results:**
• **👥 Total Users:** **{total_users}**
• **✅ Successfully Sent:** **{successful_sends}**
• **❌ Failed:** **{failed_sends}**
• **📈 Success Rate:** **{(successful_sends/total_users*100):.1f}%**

**🎉 Broadcast delivered successfully!**"""
        
        await progress_message.edit_text(final_text, parse_mode="Markdown")
        await state.clear()

    # Remove channel callback
    async def remove_channel_callback(self, callback: types.CallbackQuery):
        """Handle remove channel callback"""
        if callback.from_user.id != ADMIN_ID:
            return
        
        channel_id = callback.data.replace("remove_channel_", "")
        
        success = await db.remove_channel(channel_id)
        
        if success:
            await callback.answer("**✅ Channel removed successfully!**", show_alert=True)
            # Refresh the remove button menu
            await self.admin_remove_button(callback)
        else:
            await callback.answer("**❌ Failed to remove channel!**", show_alert=True)

    # Withdrawal approval/rejection callbacks
    async def approve_withdrawal(self, callback: types.CallbackQuery):
        """Handle withdrawal approval"""
        if callback.from_user.id != ADMIN_ID:
            return
        
        withdrawal_id = callback.data.replace("approve_", "")
        
        success = await db.update_withdrawal_status(withdrawal_id, "approved")
        
        if success:
            # Get withdrawal details
            withdrawal = await db.get_withdrawal(withdrawal_id)
            
            if withdrawal:
                # Notify user
                user_notification = f"""**🎉 Withdrawal Successful! 🎉**

**✅ Your withdrawal of {withdrawal['amount']}⭐ Stars has been successful. Enjoy!**

**📋 Details:**
• **🆔 Order ID:** **{withdrawal_id}**
• **⭐ Amount:** **{withdrawal['amount']}⭐**
• **👤 Username:** **{withdrawal['username']}**
• **📅 Processed:** **{datetime.utcnow().strftime('%Y-%m-%d %H:%M')}**

**🌟 Thank you for using RajXStars Bot!**"""
                
                try:
                    await self.bot.send_message(withdrawal['user_id'], user_notification, parse_mode="Markdown")
                except Exception as e:
                    logger.error(f"Failed to notify user: {e}")
            
            # Update admin message
            updated_text = callback.message.text + "\n\n**✅ APPROVED**"
            await callback.message.edit_text(updated_text, parse_mode="Markdown")
            await callback.answer("**✅ Withdrawal approved!**", show_alert=True)
        else:
            await callback.answer("**❌ Failed to approve withdrawal!**", show_alert=True)

    async def reject_withdrawal(self, callback: types.CallbackQuery):
        """Handle withdrawal rejection"""
        if callback.from_user.id != ADMIN_ID:
            return
        
        withdrawal_id = callback.data.replace("reject_", "")
        
        # Get withdrawal details before updating
        withdrawal = await db.get_withdrawal(withdrawal_id)
        
        if not withdrawal:
            await callback.answer("**❌ Withdrawal not found!**", show_alert=True)
            return
        
        success = await db.update_withdrawal_status(withdrawal_id, "rejected")
        
        if success:
            # Refund user balance
            await db.update_user_balance(withdrawal['user_id'], withdrawal['amount'])
            
            # Notify user
            user_notification = f"""**❌ Withdrawal Request Rejected**

**💰 Your withdrawal request was rejected. Stars have been refunded.**

**📋 Details:**
• **🆔 Order ID:** **{withdrawal_id}**
• **⭐ Amount:** **{withdrawal['amount']}⭐** **(Refunded)**
• **👤 Username:** **{withdrawal['username']}**
• **📅 Processed:** **{datetime.utcnow().strftime('%Y-%m-%d %H:%M')}**

**📞 Contact admin for more information:**
**@TRUSTED_X_RAJ**"""
            
            try:
                await self.bot.send_message(withdrawal['user_id'], user_notification, parse_mode="Markdown")
            except Exception as e:
                logger.error(f"Failed to notify user: {e}")
            
            # Update admin message
            updated_text = callback.message.text + "\n\n**❌ REJECTED & REFUNDED**"
            await callback.message.edit_text(updated_text, parse_mode="Markdown")
            await callback.answer("**❌ Withdrawal rejected and refunded!**", show_alert=True)
        else:
            await callback.answer("**❌ Failed to reject withdrawal!**", show_alert=True)