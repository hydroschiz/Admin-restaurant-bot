from aiogram.fsm.state import StatesGroup, State


class AddRestaurant(StatesGroup):
    SetName = State()
    SetBotToken = State()
    SetAdminID1 = State()
    SetAdminID2 = State()
    SetAdminID3 = State()
    SetAuthToken = State()
    Deploy = State()
