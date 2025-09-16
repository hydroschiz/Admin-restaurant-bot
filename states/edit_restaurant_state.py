from aiogram.fsm.state import StatesGroup, State


class EditRestaurant(StatesGroup):
    InputID = State()
    SelectColumn = State()
    InputValue = State()
