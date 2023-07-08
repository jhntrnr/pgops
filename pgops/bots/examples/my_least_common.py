import random

from ..pgops_bot import PgopsBot

class MyLeastCommon(PgopsBot):
    """Plays a card from among the least common own plays against a given target
    Failing that, plays a random card.
    """
    def __init__(self, game_type):
        bot_name = "My_least_common"
        supported_game_types = ["gops"]
        self.setup_memory()
        super().__init__(game_type, supported_game_types, bot_name=bot_name)
    
    def setup_memory(self, maxn=4):
        self.sand_attack = False
        # memory tracks how many times I played a card against a given target card
        self.memory = {}
        for i in range(1,14):
            self.memory[i] = {}
            for j in range(1,14):
                self.memory[i][j] = 0
    
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

        # find my least common plays for this target
        current_bid_target = self.get_current_bid_target()
        my_history = self.memory[current_bid_target.value]
        min_times_played = min([my_history[num] for num in my_history])
        my_lcp = [num for num in my_history if my_history[num] == min_times_played]
        lcp_in_hand = [card for card in hand_cards if card.value in my_lcp]
        if len(lcp_in_hand) > 0:
            chosen_card = random.choice(lcp_in_hand)
        else:
            chosen_card = random.choice(hand_cards)
        return self.play_card(chosen_card)

    def turn_over(self, my_card_played, opponent_card_played, bid_card, result):
        # Sand attack attempts to corrupt opponent's memory
        # Therefore we stop tracking plays when sand attack is active
        if self.sand_attack:
            return
        
        # Otherwise, log our play
        if bid_card is not None and my_card_played is not None:
            self.memory[bid_card.value][my_card_played.value] += 1

    def game_over(self, my_score, opp_score):
        self.sand_attack = False
        return
    
    def match_over(self, my_wins, opp_wins, draws):
        # clear own memory after a match to avoid being locked into a death spiral
        self.setup_memory()
        return