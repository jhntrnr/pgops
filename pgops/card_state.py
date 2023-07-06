from enum import Enum

class CardState(Enum):
    in_deck = 0

    player_a_hand = 1
    player_b_hand = 2
    
    player_a_sealed_bid = 3
    player_b_sealed_bid = 4

    player_a_playzone = 5
    player_b_playzone = 6

    player_a_score = 7
    player_b_score = 8

    player_a_discard = 9
    player_b_discard = 10

    current_bid_target = 11
    previous_bid_targets = 12

    global_discard = 13