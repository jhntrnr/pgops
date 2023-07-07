import random

from ..pgops_bot import PgopsBot

class AdaptiveGops(PgopsBot):
    """Keeps track of opponent's plays throughout a match.
    Tries to beat opponent's most common play vs the target card.
    If random play is detected, reverts to bounded random play in response.
    If a winning or losing state is detected, initiates "sand attack"--fully random play to obfuscate own strategy
    """
    def __init__(self, game_type):
        bot_name = "adaptive_gops"
        supported_game_types = ["gops"]
        super().__init__(game_type, supported_game_types, bot_name=bot_name)
        self.setup_memory()

    def setup_memory(self):
        self.sand_attack = False
        
        # spooky magic numbers
        # TODO: tune these parameters
        self.random_threshold = 1
        self.cool_factor = 0.75
        self.heat_factor = 1.05
        self.thresh_min = 0.25
        self.thresh_max = 2

        # memory tracks how many times opponent played a card against a given target card
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

        # find opponent's most common play for this target
        current_bid_target = self.get_current_bid_target()
        opp_history_for_this_target = self.memory[current_bid_target.value]

        opp_sum = sum([opp_history_for_this_target[num] for num in opp_history_for_this_target])
        
        opp_highest_number = max([opp_history_for_this_target[num] for num in opp_history_for_this_target])
        opp_most_common_play = list(opp_history_for_this_target.keys())[list(opp_history_for_this_target.values()).index(opp_highest_number)]
        
        # if random play detected from opponent, revert to bounded random play
        if opp_sum == 0 or opp_highest_number / opp_sum < self.random_threshold:
            return self.play_card(self.bounded_random_choice(current_bid_target, hand_cards))
        # otherwise attempt to beat their predicted play
        else:
            beat_by = abs(current_bid_target.value - opp_most_common_play)+1
            return self.play_card(self.beat_target_by_n(current_bid_target.value, hand_cards, beat_by))

    def bounded_random_choice(self, in_card, hand_cards, bounds=2):
        """pick a random card within 'bounds' of 'in_card' from hand"""
        in_value = in_card.value
        min_value = in_value - bounds
        max_value = in_value + bounds
        if max_value > 13:
            max_value = max_value % 13
        pivot_card = self.closest_card_to_value(in_value, hand_cards)
        pivot_index = hand_cards.index(pivot_card)
        bound_cards = []
        for i in range(pivot_index-bounds,pivot_index+bounds+1):
            try:
                bound_cards.append(hand_cards[i])
            except IndexError:
                pass
        bound_cards = set(bound_cards)
        return random.choice(list(bound_cards))
    
    def beat_target_by_n(self, value, cards, n):
        """try to pick a card that beats a value by 'n'. Otherwise play the lowest possible card."""
        beat_difference = float('inf')
        chosen_card = None
        for card in cards:
            if card.value > value and card.value - value < beat_difference and card.value - value >= n:
                beat_difference = card.value - value
                chosen_card = card
        if chosen_card is None:
            chosen_card = self.closest_card_to_value(1, cards)
        return chosen_card

    def closest_card_to_value(self, value, cards):
        """Finds the card in 'cards' closest to 'value'."""
        closest_card = None
        closest_value = float('inf')
        for card in cards:
            if card.value == value:
                closest_card = card
                closest_value = 0
            elif abs(card.value - value) < closest_value:
                closest_card = card
                closest_value = abs(card.value - value)
        return closest_card

    def turn_over(self, my_card_played, opponent_card_played, bid_card, result):
        # Sand attack attempts to corrupt opponent's memory
        # Therefore we stop tracking opponent's plays when sand attack is active
        if self.sand_attack:
            return
        
        # Otherwise, assume opponent has a strategy and log it
        if bid_card is not None and opponent_card_played is not None:
            self.memory[bid_card.value][opponent_card_played.value] += 1
        return
    
    def game_over(self, my_score, opp_score):
        # won the game, assume performance is good, lower random_threshold
        if my_score > opp_score:
            self.random_threshold *= self.cool_factor

        # lost the game, assume performance is bad, raise random_threshold
        elif opp_score > my_score:
            self.random_threshold *= self.heat_factor
        self.random_threshold = max(self.thresh_min, min(self.random_threshold, self.thresh_max))
        self.sand_attack = False
        return
    
    def match_over(self, my_wins, opp_wins, draws):
        # clear own memory after a match to avoid being locked into a death spiral
        self.setup_memory()
        return