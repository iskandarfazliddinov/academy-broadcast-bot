from aiogram.fsm.state import State, StatesGroup


class BroadcastState(StatesGroup):
    waiting_for_message = State()
    confirm_broadcast = State()
