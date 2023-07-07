import random

from ..pgops_bot import PgopsBot

class OddEvenBot(PgopsBot):
    """Tries to play the closest odd card to a target card.
    Else, tries to play the closest even card to a target card.
    If a winning or losing state is detected, initiates "sand attack"--fully random play to obfuscate own strategy.

    Not a powerful opponent; provided for diversity among dummy opponents
    """
    def __init__(self, game_type):
        bot_name = "Odd_Even"
        supported_game_types = ["gops"]
        super().__init__(game_type, supported_game_types, bot_name=bot_name)
        self.setup_memory()

    def setup_memory(self):
        self.sand_attack = False

    def select_and_play_card(self):
        hand_cards = self.get_playable_cards_in_own_hand()

        if len(hand_cards) == 1:
            self.sand_attack = True
            return self.play_card(hand_cards[0])

        my_score = self.get_own_score()
        opponent_score = self.get_opponent_score()

        if self.game_type == "gops" and (my_score > 45 or opponent_score > 45):
            self.sand_attack = True
            return self.play_card(random.choice(hand_cards))
        
        current_bid_target = self.get_current_bid_target()
        chosen_card = self.closest_odd(current_bid_target.value, hand_cards)
        if chosen_card is None:
            chosen_card = self.closest_even(current_bid_target.value, hand_cards)
        if chosen_card is None:
            chosen_card = random.choice(hand_cards)
        return self.play_card(chosen_card)

    def closest_odd(self, value, cards):
        closest_card = None
        closest_value = float('inf')
        for card in cards:
            if card.value % 2 == 0:
                continue
            if card.value == value:
                closest_card = card
                closest_value = 0
            elif abs(card.value - value) < closest_value:
                closest_card = card
                closest_value = abs(card.value - value)
        return closest_card
    
    def closest_even(self, value, cards):
        closest_card = None
        closest_value = float('inf')
        for card in cards:
            if card.value % 2 == 1:
                continue
            if card.value == value:
                closest_card = card
                closest_value = 0
            elif abs(card.value - value) < closest_value:
                closest_card = card
                closest_value = abs(card.value - value)
        return closest_card

    def turn_over(self, my_card_played, opponent_card_played, bid_card, result):
        if self.sand_attack:
            return
        if bid_card is not None and opponent_card_played is not None:
            pass
        return
    
    def game_over(self, my_score, opponent_score):
        self.sand_attack = False
        return
    
    def match_over(self, my_wins, opponent_wins, draws):
        self.setup_memory()
        return