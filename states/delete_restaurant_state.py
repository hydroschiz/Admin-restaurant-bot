from aiogram.fsm.state import StatesGroup, State


class DeleteRestaurant(StatesGroup):
    InputID = State()
