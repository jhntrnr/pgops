import random

from ..pgops_bot import PgopsBot

class MatchPlusCycle(PgopsBot):
    
    def __init__(self, game_type):
        bot_name = "Match_plus_cycle"
        supported_game_types = ["gops"]
        self.n = 0
        super().__init__(game_type, supported_game_types, bot_name=bot_name)
    
    def cycle_n(self, maxn=4):
        self.n += 1
        if self.n > maxn:
            self.n = 0
        self.sand_attack = False

    def select_and_play_card(self):
        hand_cards = self.get_playable_cards_in_own_hand()

        # Don't bother with logic if only one card left
        if len(hand_cards) == 1:
            self.sand_attack = True
            return self.play_card(hand_cards[0])

        my_score = self.get_own_score()
        opp_score = self.get_opponent_score()

        # if we are definitely losing or winning, initiate "sand attack"
        if self.game_type == "gops" and (my_score > 45 or opp_score > 45):
            self.sand_attack = True
            return self.play_card(random.choice(hand_cards))
        
        current_bid_target = self.get_current_bid_target()
        chosen_card = self.beat_by_n(current_bid_target.value, hand_cards)
        return self.play_card(chosen_card)

    def beat_by_n(self, in_value, hand_cards):
        hand_values = [card.value for card in hand_cards]
        target_value = in_value + self.n
        # overflow
        if target_value > max(hand_values):
            target_value -= 13
        # underflow
        elif target_value < min(hand_values):
            target_value += 13
        
        return hand_cards[hand_values.index(target_value)]

    def game_over(self, my_score, opponent_score):
        self.cycle_n()
        return