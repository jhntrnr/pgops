from .card import Card
from .card_state import CardState
from .hand import Hand

class Player:
    def __init__(self, player_id, game_type):
        self.player_id = player_id
        self.hand = self.make_new_hand(game_type,1,13)
        self.frozen = False
        self.unfreeze_next = False

    def make_new_hand(self, game_type, min_value, max_value):
        cards = []
        for i in range(min_value, max_value+1):
            card = Card(i, "player", CardState(self.player_id), str(i))
            cards.append(card)
        if game_type == "bgops" or game_type == "bgops_minus":
            spy = Card(0, "player", CardState(self.player_id), "Spy")
            bomb = Card(-1, "player", CardState(self.player_id), "Bomb")
            cards.append(spy)
            cards.append(bomb)
        hand = Hand(cards, self.player_id)
        return hand

    def play_specific_card(self, chosen_card):
        if self.frozen:
            return None
        if chosen_card.state.value != self.player_id:
            raise Exception(f"Card {chosen_card.name} not playable")
        chosen_card.change_state(CardState(chosen_card.state.value + 2))
        return chosen_card

    def mask(self):
        hand_mask = [card.state == self.player_id for card in self.hand.cards]
        return hand_mask

    def reveal_hand(self):
        self.hand.revealing = True

    def hide_hand(self):
        self.hand.revealing = False
    
    def freeze_self(self):
        self.frozen = True
        self.unfreeze_next = False
    
    def unfreeze_self(self):
        self.frozen = False
        self.unfreeze_next = False