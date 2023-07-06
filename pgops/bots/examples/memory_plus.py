import random

from ..pgops_bot import PgopsBot

class MemoryPlus(PgopsBot):
    def __init__(self, game_type):
        bot_name = "MemoryPlus"
        supported_game_types = ["gops", "bgops", "bgops_minus"]
        super().__init__(game_type, supported_game_types, bot_name=bot_name)
        self.setup_memory()

    def setup_memory(self):
        self.memory = {}
        for i in range(1,14):
            self.memory[f'{i}_positive'] = []
            if self.game_type == "bgops_minus":
                self.memory[f'-{i}_negative'] = []

    def select_and_play_card(self):
        hand_cards = self.get_playable_cards_in_own_hand()
        if len(hand_cards) < 1:
            return None
        current_bid_target = self.get_current_bid_target()
        memory_query = f'{current_bid_target.value}_{current_bid_target.suit}'
        if len(self.memory[memory_query]) < 1:
            chosen_card = self.random_within_bounds(current_bid_target, hand_cards)
        else:
            chosen_card = self.beat_most_frequent_by_minimum(current_bid_target, self.memory[memory_query], hand_cards)
        if chosen_card is None:
            chosen_card =  self.random_within_bounds(current_bid_target, hand_cards)
        return self.play_card(chosen_card)

    def beat_target_by_minimum(self, in_value, hand_cards):
        beat_difference = float('inf')
        chosen_card = None
        for card in hand_cards:
            if card.value > in_value and card.value - in_value < beat_difference:
                beat_difference = card.value - in_value
                chosen_card = card
        if chosen_card is None:
            return self.bomb_or_smallest_in_hand(hand_cards)
        return chosen_card

    def beat_most_frequent_by_minimum(self, input_card, input_memory, hand_cards):
        in_value = input_card.value
        most_frequent = max(set(input_memory), key = input_memory.count)
        if input_memory.count(most_frequent)/len(input_memory) < 0.5:
            return self.beat_target_by_minimum(input_card.value, hand_cards)
        if most_frequent.name == "Bomb" or most_frequent.name == "Spy":
            return self.bomb_or_smallest_in_hand(hand_cards)
        else:
            return self.beat_target_by_minimum(most_frequent.value, hand_cards)

    def bomb_or_smallest_in_hand(self, hand_cards):
        value_to_beat = float('inf')
        chosen_card = None
        for card in hand_cards:
            if card.name == "Bomb":
                chosen_card = card
                return chosen_card
            elif card.name != "Spy" and card.value < value_to_beat:
                value_to_beat = card.value
                chosen_card = card
        return chosen_card

    def random_within_bounds(self, input_card, hand_cards):
        in_value = input_card.value
        lower_bounds = min(0, in_value - 3)
        upper_bounds = max(14, in_value + 3)
        playable_cards_in_bounds = []
        for card in hand_cards:
            if card.value > lower_bounds and card.value < upper_bounds:
                playable_cards_in_bounds.append(card)
        if len(playable_cards_in_bounds) > 0:
            return random.choice(playable_cards_in_bounds)
        else:
            return random.choice(hand_cards)

    def turn_over(self, my_card_played, opponent_card_played, bid_card, result):
        if opponent_card_played is not None and bid_card is not None:
            self.memory[f'{bid_card.value}_{bid_card.suit}'].append(opponent_card_played)
            if len(self.memory[f'{bid_card.value}_{bid_card.suit}']) > 50:
                self.memory[f'{bid_card.value}_{bid_card.suit}'].pop(random.randrange(len(self.memory[f'{bid_card.value}_{bid_card.suit}'])))
        return
    
    def game_over(self, my_score, opponent_score):
        return
    
    def match_over(self, my_wins, opponent_wins, draws):
        self.setup_memory()
        return