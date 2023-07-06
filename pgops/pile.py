import random

from .card_state import CardState

class Pile:
    def __init__(self, cards, designation):
        self.cards = cards
        self.designation = designation
        self.starting_size = len(self.cards)
        self.revealing = False

    def score_of_pile(self):
        score = 0
        for card in self.cards:
            if card.suit == "negative":
                score -= card.value
            else:
                score += card.value
        return score
    
    def pile_state(self):
        state = []
        for card in self.cards:
            if card.state == CardState.player_a_sealed_bid:
                report_state = CardState.player_a_hand
            elif card.state == CardState.player_b_sealed_bid:
                report_state = CardState.player_b_hand
            else:
                report_state = card.state
            card_dict = {
                "card_value":card.value,
                "card_state":report_state,
                "card_suit":card.suit,
                "card_reference":card
            }
            state.append(card_dict)
        return state
    
    def masked_pile_state(self):
        state = []
        for card in self.cards:
            if card.state == CardState.player_a_sealed_bid and not self.revealing:
                report_state = CardState.player_a_hand
            elif card.state == CardState.player_b_sealed_bid and not self.revealing:
                report_state = CardState.player_b_hand
            else:
                report_state = card.state
            card_dict = {
                "card_value":card.value,
                "card_state":report_state,
                "card_name":card.name,
                "card_reference":card
            }
            state.append(card_dict)
        return state