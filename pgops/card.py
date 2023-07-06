from .card_state import CardState

class Card:
    def __init__(self, value, suit, state, name=None):
        self.value = value
        self.suit = suit
        self.state = state
        if name is None:
            self.name = str(value)
        else:
            self.name = name

    def change_state(self, new_state):
        self.state = new_state