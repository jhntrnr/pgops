import random

from ..pgops_bot import PgopsBot

class AdaptiveGopsV3(PgopsBot):
    """Keeps track of opponent's plays throughout a match.
    Tries to beat opponent's most common play vs the target card.
    If random play is detected, reverts to bounded random play in response.
    If a winning or losing state is detected, initiates "sand attack"--fully random play to obfuscate own strategy

    Clone of `advanced_gops_v2` with smarter win detection behavior.
    """
    def __init__(self, game_type):
        bot_name = "adaptive_gops_v3"
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
        self.memory = {i: {j: 0 for j in range(1, 14)} for i in range(1, 14)}
    
    def select_and_play_card(self):
        hand_cards = self.get_playable_cards_in_own_hand()

        # Don't bother with logic if only one card left. Initiate "sand attack" to obfuscate the strategy
        if len(hand_cards) == 1:
            self.sand_attack = True
            return self.play_card(hand_cards[0])

        my_score = self.get_own_score()
        opp_score = self.get_opponent_score()

        # If we are significantly leading or lagging behind, initiate "sand attack"
        if self.game_type == "gops" and (my_score > 45 or opp_score > 45):
            self.sand_attack = True
            return self.play_card(random.choice(hand_cards))
        
        current_bid_target = self.get_current_bid_target()
        opponent_hand = [i['card_value'] for i in self.get_playable_cards_in_opponent_hand()]

        # If winning this bid would put us over 45, and we are certain to win, just win the bid
        if self.game_type == "gops" and my_score + current_bid_target.value > 45:
            my_sorted_hand = sorted(hand_cards, key=lambda x: x.value, reverse=True)
            opp_sorted_hand = sorted(opponent_hand, key=lambda x: x, reverse=True)
            for i, card in enumerate(my_sorted_hand):
                # win by force detected
                if card.value > opp_sorted_hand[i]:
                    return self.play_card(my_sorted_hand[0])
                # lose by force if opponent plays optimally; abort
                elif card.value < opp_sorted_hand[i]:
                    break

        # Retrieve the opponent's play history for the current target
        opp_history_for_this_target = self.memory[current_bid_target.value]

        # Compute the total and most common play from the opponent's history
        opp_sum = sum(opp_history_for_this_target.values())
        opp_most_common_play, opp_highest_number = max(opp_history_for_this_target.items(), key=lambda item: item[1])

        # If the opponent's play seems random (based on our threshold), use a bounded random choice
        if opp_sum == 0 or opp_highest_number / opp_sum < self.random_threshold:
            return self.play_card(self.bounded_random_choice(current_bid_target, hand_cards))
        # If the opponent seems to be following a strategy, attempt to beat their predicted play
        else:
            beat_by = abs(current_bid_target.value - opp_most_common_play) + 1
            return self.play_card(self.get_optimal_card(current_bid_target.value, hand_cards, n=beat_by))

    def bounded_random_choice(self, in_card, hand_cards, bounds=2):
        """Pick a random card within 'bounds' of 'in_card' from hand
        If no cards in hand within bounds, returns get_optimal_card"""
        min_value = max(1, in_card.value - bounds)
        max_value = min(13, in_card.value + bounds)

        # Filter cards within the value bounds
        bound_cards = [card for card in hand_cards if min_value <= card.value <= max_value]
        
        if not bound_cards:
            return self.get_optimal_card(in_card.value, hand_cards)
        else:
            return random.choice(bound_cards)
    
    def get_optimal_card(self, value, cards, n=None):
        """Finds a card that either beats a given 'value' by 'n' or is the closest to 'value'.
        If 'n' is None, only the closeness criterion is considered."""
        
        chosen_card = None
        closest_card = None

        beat_difference = float('inf')
        closest_difference = float('inf')

        for card in cards:
            current_difference = card.value - value
            
            if n is not None and card.value > value and current_difference < beat_difference and current_difference >= n:
                beat_difference = current_difference
                chosen_card = card

            if abs(current_difference) < closest_difference:
                closest_difference = abs(current_difference)
                closest_card = card

        return chosen_card if chosen_card is not None else closest_card

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