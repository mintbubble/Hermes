from typing import List


class User:
    def __init__(self, chat_id: str, is_paid: bool=False, profiles: List["Profile"]=None, favourite_stocks: list[dict]=None):
        self.chat_id = chat_id
        self.is_paid = is_paid
        self.profiles = profiles
        self.favourite_stocks = favourite_stocks



class Profile:
    def __init__(self, name: str, user_id: str, stocks: list[dict]=None):
        self.name = name
        self.user_id = user_id
        self.stocks = stocks
