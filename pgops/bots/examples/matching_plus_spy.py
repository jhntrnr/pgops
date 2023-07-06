from ..pgops_bot import PgopsBot

class MatchingPlusSpy(PgopsBot):
    
    def __init__(self, game_type):
        bot_name = "Matching+1_spybomb13"
        supported_game_types = ["gops", "bgops", "bgops_minus"]
        super().__init__(game_type, supported_game_types, bot_name=bot_name)
        self.played_spy_last_turn = False

    def playable_spy_in_hand(self, hand):
        playable_spy = None
        for card in hand:
            if card.name == "Spy":
                playable_spy = card
        return playable_spy

    def playable_bomb_in_hand(self, hand):
        playable_bomb = None
        for card in hand:
            if card.name == "Bomb":
                playable_bomb = card
        return playable_bomb

    def beat_by_minimum_possible(self, card_to_beat, hand):
        closest_value = 100000
        chosen_card = None
        for card in hand:
            if card.name != "Spy" and card.name != "Bomb":
                if card.value > card_to_beat.value and card.value-card_to_beat.value < closest_value:
                    chosen_card = card
        return chosen_card

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
        current_bid_target = self.get_current_bid_target()
        if self.played_spy_last_turn:
            opponent_card = self.get_opponent_sealed_bid()
            self.played_spy_last_turn = False
            if opponent_card is not None:
                card = self.beat_by_minimum_possible(opponent_card, hand_cards)
                if card is not None:
                    return self.play_card(card)
        playable_spy = self.playable_spy_in_hand(hand_cards)
        playable_bomb = self.playable_bomb_in_hand(hand_cards)
        if current_bid_target.value == 13 and playable_spy is not None:
            played = self.play_card(playable_spy)
            if played is not None:
                self.played_spy_last_turn = True
            return played
        if current_bid_target.value == 13 and playable_bomb is not None:
            played = self.play_card(playable_bomb)
            return played
        for card in hand_cards:
            if card.value == 1 and current_bid_target.value == 13:
                return self.play_card(card)
            if card.value == current_bid_target.value + 1:
                return self.play_card(card)
        min_value = float("inf")
        min_card = None
        for card in hand_cards:
            if card.value < min_value:
                min_value = card.value
                min_card = card
        if min_card is not None:
            return self.play_card(min_card)