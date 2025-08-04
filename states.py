# states.py
from aiogram.fsm.state import State, StatesGroup

class AdminStates(StatesGroup):
    waiting_for_channel = State()
    waiting_for_button_name = State()
    waiting_for_broadcast = State()

class WithdrawStates(StatesGroup):
    waiting_for_username = State()
    waiting_for_amount = State()