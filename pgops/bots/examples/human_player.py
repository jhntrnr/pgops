from ..pgops_bot import PgopsBot

class HumanPlayer(PgopsBot):
    def __init__(self, game_type):
        bot_name = "Human Player"
        supported_game_types = ["gops"]
        super().__init__(game_type, supported_game_types, bot_name=bot_name)

    def select_and_play_card(self):
        hand_cards = self.get_playable_cards_in_own_hand()
        opponent_hand_cards = self.get_playable_cards_in_opponent_hand()
        bid_card = self.get_current_bid_target()
        my_score = self.get_own_score()
        opponent_score = self.get_opponent_score()
        print(f'My score: {my_score} --- Opponent score: {opponent_score}')
        print(f'Current bid target is: {bid_card.value}')
        print(f'Opponent hand is: {[card.value for card in opponent_hand_cards]}')
        print(f'Hand cards are: {[card.value for card in hand_cards]}')
        chosen_card = None
        while chosen_card is None:
            selected_card_val = int(input('Select a card to play... '))
            for card in hand_cards:
                if card.value == selected_card_val:
                    chosen_card = card
            if chosen_card is None:
                print(f'Card {selected_card_val} is invalid')
        return self.play_card(chosen_card)

    def turn_over(self, my_card_played, opponent_card_played, bid_card, result):
        if bid_card is not None and opponent_card_played is not None and my_card_played is not None:
            print(f'\ntarget was {bid_card.value} -- opponent played {opponent_card_played.value} -- human played {my_card_played.value}\n')
        return
    
    def game_over(self, my_score, opponent_score):
        print(f'\nGame is done, human scored {my_score} -- opponent scored {opponent_score}\n')
        return
    
    def match_over(self, my_wins, opponent_wins, draws):
        return