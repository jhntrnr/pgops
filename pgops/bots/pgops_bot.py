from ..card import Card
from ..card_state import CardState

class PgopsBot:
    def __init__(self, game_type, supported_game_types, bot_name="Bot"):
        self.game_type = game_type
        self.bot_name = bot_name
        if self.game_type not in supported_game_types:
            raise Exception(f'Bot {self.bot_name} does not support game of type {self.game_type}')

    def setup(self, game, player_name):
        """MUST NOT be overridden"""
        self.game = game
        self.player_name = player_name
        if player_name == "player_a":
            self.opponent_name = "player_b"
        elif player_name == "player_b":
            self.opponent_name = "player_a"

    def play_card(self, card):
        """MUST NOT be overridden"""
        if self.game.players[self.player_name].frozen:
            return None
        else:
            played_card = self.game.players[self.player_name].play_specific_card(card)
            return played_card

    def turn_over(self, my_card_played, opponent_card_played, bid_card, result):
        """Provides information about the previous turn.
        `my_card_played` or `opponent_card_played` might be None.
        `bid_card` is the card that players were bidding on that turn.
        `result` is a list containing one or more of the following strings:
        ["win", "lose", "tie", "bomb", "my_spy", "opponent_spy", "both_spy"]
        """
        return
    
    def game_over(self, my_score, opponent_score):
        """Provides information about the scores at the end of a game."""
        return
    
    def match_over(self, my_wins, opponent_wins, draws):
        """Provides information about the results of a match."""
        return

    def get_state(self):
        """Returns the full, masked game state on demand.
        Masked means a player's current sealed bid appears to still be in hand, unless that player was spied on last turn.
        """
        return self.game.masked_game_state()

    def get_current_bid_target(self):
        """Returns information about the current bid target in a dict:
        card_dict = {
            "card_value": Int,
            "card_state": CardState,
            "card_suit": Str,
            "card_reference": Card
        }
        """
        state = self.get_state()
        for card_dict in state['deck_state']:
            if card_dict['card_reference'].state == CardState.current_bid_target:
                return card_dict['card_reference']
        return None
    
    def get_all_bid_targets(self):
        """Returns a list of dicts of information about all active bid targets, including pushed targets.
        card_dict = {
            "card_value": Int,
            "card_state": CardState,
            "card_suit": Str,
            "card_reference": Card
        }
        """
        all_targets = []
        state = self.get_state()
        for card_dict in state['deck_state']:
            if card_dict['card_reference'].state == CardState.current_bid_target or card_dict['card_reference'].state == CardState.previous_bid_targets:
                all_targets.append(card_dict['card_reference'])
        return all_targets

    def get_playable_cards_in_own_hand(self):
        """Returns a list of dicts of information about all playable cards in own hand.
        card_dict = {
            "card_value": Int,
            "card_state": CardState,
            "card_name": Str,
            "card_reference": Card
        }
        """
        playable_hand = []
        state = self.get_state()
        for card_dict in state[f'{self.player_name}_cards']:
            if card_dict['card_reference'].state in [CardState.player_a_hand, CardState.player_b_hand]:
                playable_hand.append(card_dict['card_reference'])
        return playable_hand
    
    def get_playable_cards_in_opponent_hand(self):
        """Returns a list of dicts of information about all playable cards in opponent's hand.
        Opponent's current sealed bid shows up as in their hand.
        card_dict = {
            "card_value": Int,
            "card_state": CardState,
            "card_name": Str,
            "card_reference": Card
        }
        """
        opponent_hand = []
        state = self.get_state()
        for card_dict in state[f'{self.opponent_name}_cards']:
            if card_dict['card_reference'].state in [CardState.player_a_hand, CardState.player_b_hand]:
                opponent_hand.append(card_dict['card_reference'])
        return opponent_hand
    
    def get_all_cards_in_own_playzone(self):
        """Returns a list of dicts of information about all cards in own playzone.
        Generally these are any played cards visible to both players.
        card_dict = {
            "card_value": Int,
            "card_state": CardState,
            "card_name": Str,
            "card_reference": Card
        }
        """
        playzone = []
        state = self.get_state()
        for card_dict in state[f'{self.player_name}_cards']:
            if card_dict['card_reference'].state in [CardState.player_a_playzone, CardState.player_b_playzone]:
                playzone.append(card_dict['card_reference'])
        return playzone
    
    def get_all_cards_in_opponent_playzone(self):
        """Returns a list of dicts of information about all cards in opponent's playzone.
        Generally these are any played cards visible to both players.
        card_dict = {
            "card_value": Int,
            "card_state": CardState,
            "card_name": Str,
            "card_reference": Card
        }
        """
        playzone = []
        state = self.get_state()
        for card_dict in state[f'{self.opponent_name}_cards']:
            if card_dict['card_reference'].state in [CardState.player_a_playzone, CardState.player_b_playzone]:
                playzone.append(card_dict['card_reference'])
        return playzone
    
    def get_opponent_sealed_bid(self):
        """Returns a dict of information about opponent's sealed bid if own Spy was played last turn. Else None.
        card_dict = {
            "card_value": Int,
            "card_state": CardState,
            "card_name": Str,
            "card_reference": Card
        }
        """
        if not self.game.players[self.opponent_name].frozen:
            return None
        else:
            state = self.get_state()
            for card_dict in state[f'{self.opponent_name}_cards']:
                if card_dict['card_reference'].state in [CardState.player_a_sealed_bid, CardState.player_b_sealed_bid]:
                    return card_dict['card_reference']
            return None
    
    def get_own_score(self):
        """Returns own current game score"""
        state = self.get_state()
        return state[f'{self.player_name}_score']
    
    def get_opponent_score(self):
        """Returns opponent's current game score"""
        state = self.get_state()
        return state[f'{self.opponent_name}_score']