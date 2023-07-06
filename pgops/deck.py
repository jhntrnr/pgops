import random

from .pile import Pile
from .card import Card
from .card_state import CardState

class Deck(Pile):
    def __init__(self, cards, deck_id):
        super().__init__(cards=cards, designation=deck_id)

    def shuffle(self):
        random.shuffle(self.cards)

    def random_card_for_bidding(self):
        card = random.choice([card for card in self.cards if card.state == CardState.in_deck])
        card.change_state(CardState.current_bid_target)
        return card

    def count_cards_left_in_deck(self):
        count = len([card for card in self.cards if card.state == CardState.in_deck])
        return count