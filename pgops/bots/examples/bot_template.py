from ..pgops_bot import PgopsBot

class BotTemplate(PgopsBot):
    def __init__(self, game_type):
        """Skeleton of a Pgops bot.
        See `pgops/README.md` for details about game types.
        See `bots/pgops_bot.py` for available methods.
        See `pgops/bots/README.md` for bot rules and guidelines.
        Must call `super().__init__(game_type, supported_game_types, bot_name=bot_name)` during init.
        """
        bot_name = "TEMPLATE_CHANGE_ME"
        supported_game_types = ["gops", "bgops", "bgops_minus"]
        super().__init__(game_type, supported_game_types, bot_name=bot_name)

    def select_and_play_card(self):
        """Called by the tournament orchestrator each turn.
        Must implement two things:
            -Choose a card from the list in `self.get_playable_cards_in_own_hand()`
            -Must return `self.play_card(chosen_card)`
                -`self.play_card` must not be overridden. Doing so will disqualify the bot.

        If opponent played "Spy" in the previous turn, this method is still called, but the selected card will not be played.
        """
        hand_cards = self.get_playable_cards_in_own_hand()
        if len(hand_cards) > 0:
            chosen_card = random.choice(hand_cards)
            return self.play_card(chosen_card)

    def turn_over(self, my_card_played, opponent_card_played, bid_card, result):
        """Provides information about the previous turn.
        `my_card_played` and `opponent_card_played` might be None.
        `bid_card` is the card that players were bidding on that turn.
        `result` is a list containing one of the following strings:
        ["win", "lose", "tie", "bomb", "my_spy", "opponent_spy", "both_spy"]
        """
        return
    
    def game_over(self, my_score, opponent_score):
        """Provides information about the scores at the end of a game."""
        return
    
    def match_over(self, my_wins, opponent_wins, draws):
        """Provides information about the results of a match."""
        return