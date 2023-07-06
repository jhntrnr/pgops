from .card import Card
from .card_state import CardState
from .pile import Pile

class Hand(Pile):
    def __init__(self, cards, player_id):
        super().__init__(cards=cards, designation=player_id)
    
    def count_cards_left_in_hand(self, only_bid_cards=True):
        if only_bid_cards:
            count = len([card for card in self.cards if card.state.value == self.designation])
            return count
        else:
            count = sum([card for card in self.cards if card.state.value == self.designation])
            return count