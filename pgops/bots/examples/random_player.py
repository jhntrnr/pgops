import random

from ..pgops_bot import PgopsBot

class RandomPlayer(PgopsBot):
    def __init__(self, game_type):
        """Example Pgops bot implementation
        This bot simply plays cards at random from its hand.
        """
        bot_name = "RandomBot"
        supported_game_types = ["gops", "bgops", "bgops_minus"]
        super().__init__(game_type, supported_game_types, bot_name=bot_name)
    
    def select_and_play_card(self):
        """Called by the tournament orchestrator each turn.
        Must implement two things:
            -Choose a card from the list in `self.get_playable_cards_in_own_hand`
            -Call `self.play_card(chosen_card)`
                -`self.play_card` must not be overridden. Doing so will disqualify the bot.

        Any information from the methods in PgoptsBot is free to be used.
        Any further information from deeper in the game is hidden.
        Using deeper information is illegal and will disqualify the bot.

        If opponent played "Spy" in the previous turn, this method is still called, but the selected card will not be played.
        """
        hand_cards = self.get_playable_cards_in_own_hand()
        if len(hand_cards) > 0:
            chosen_card = random.choice(hand_cards)
            return self.play_card(chosen_card)