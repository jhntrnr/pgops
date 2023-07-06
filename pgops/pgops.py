from .player import Player
from .pile import Pile
from .deck import Deck
from .card import Card
from .card_state import CardState

class Pgops:
    def __init__(self, game_type, logging=False):
        self.game_type = game_type
        self.logging = logging

    def new_game(self):
        self.player_a = Player(1, self.game_type)
        self.player_b = Player(2, self.game_type)
        self.players = {"player_a":self.player_a, "player_b":self.player_b}
        self.deck = self.setup_gops_deck(self.game_type)

    def setup_gops_deck(self, game_type):
        cards = []
        for i in range(1, 14):
            card_a = Card(i, "positive", CardState.in_deck)
            cards.append(card_a)
            if game_type == "bgops" or game_type == "bgops_minus":
                card_b = Card(i, "positive", CardState.in_deck)
                cards.append(card_b)
                if game_type == "bgops_minus":
                    card_c = Card(-i, "negative", CardState.in_deck)
                    cards.append(card_c)
        deck = Deck(cards, "deck")
        if self.logging:
            print(f'created deck of length {len(cards)}')
        return deck

    def next_turn(self):
        if self.player_a.unfreeze_next:
            self.player_a.unfreeze_self()
        if self.player_b.unfreeze_next:
            self.player_b.unfreeze_self()
        if self.player_a.frozen:
            self.player_a.unfreeze_next = True
        if self.player_b.frozen:
            self.player_b.unfreeze_next = True
        if self.player_a.frozen or self.player_b.frozen:
            return
        bidding_card = self.deck.random_card_for_bidding()
        return bidding_card
        if self.logging:
            print(f'bidding target is {bidding_card.value}')

    def evaluate_played_cards(self):
        turn_result = []
        a_sealed_bid_list = [card for card in self.player_a.hand.cards if card.state == CardState.player_a_sealed_bid]
        b_sealed_bid_list = [card for card in self.player_b.hand.cards if card.state == CardState.player_b_sealed_bid]

        if len(a_sealed_bid_list) > 0:
            a_sealed_bid = a_sealed_bid_list[0]
        else:
            a_sealed_bid = None
        if len(b_sealed_bid_list) > 0:
            b_sealed_bid = b_sealed_bid_list[0]
        else:
            b_sealed_bid = None

        a_playzone = [card for card in self.player_a.hand.cards if card.state == CardState.player_a_playzone]
        b_playzone = [card for card in self.player_b.hand.cards if card.state == CardState.player_b_playzone]

        previous_bid_targets = [card for card in self.deck.cards if card.state == CardState.previous_bid_targets]
        current_bid_target = [card for card in self.deck.cards if card.state == CardState.current_bid_target][0]
        
        either_spied = False
        if a_sealed_bid is not None and a_sealed_bid.name == "Spy":
            turn_result.append("a_spy")
            if self.logging:
                print('player_a played spy')
            self.player_b.reveal_hand()
            self.player_b.freeze_self()
            a_sealed_bid.change_state(CardState.player_a_playzone)
            either_spied = True
        if b_sealed_bid is not None and b_sealed_bid.name == "Spy":
            turn_result.append("b_spy")
            if self.logging:
                print('player_b played spy')
            self.player_a.reveal_hand()
            if either_spied:
                self.player_b.unfreeze_self()
            else:
                self.player_a.freeze_self()
                either_spied = True
            b_sealed_bid.change_state(CardState.player_b_playzone)
        if either_spied:
            return turn_result

        # either player bombed; all active cards are discarded
        if a_sealed_bid is not None and a_sealed_bid.name == "Bomb" or b_sealed_bid is not None and b_sealed_bid.name == "Bomb":
            turn_result.append("bomb")
            if self.logging:
                print('bomb was played; discarding active cards\n')
            current_bid_target.change_state(CardState.global_discard)
            a_sealed_bid.change_state(CardState.player_a_discard)
            b_sealed_bid.change_state(CardState.player_b_discard)
            for bombed_card in previous_bid_targets:
                bombed_card.change_state(CardState.global_discard)
            for bombed_card in a_playzone:
                bombed_card.change_state(CardState.player_a_discard)
            for bombed_card in b_playzone:
                bombed_card.change_state(CardState.player_b_discard)
            return turn_result

        # tie; push
        if a_sealed_bid is not None and b_sealed_bid is not None and a_sealed_bid.value == b_sealed_bid.value:
            turn_result.append("tie")
            if self.logging:
                print(f'Players tied; pushing\n')
            a_sealed_bid.change_state(CardState.player_a_playzone)
            b_sealed_bid.change_state(CardState.player_b_playzone)
            current_bid_target.change_state(CardState.previous_bid_targets)
            return turn_result

        # player_a wins; all bid targets move to player_a_score
        elif b_sealed_bid is None or a_sealed_bid.value > b_sealed_bid.value:
            turn_result.append("a_win")
            if self.logging:
                print(f'player_a won bid\n')
            current_bid_target.change_state(CardState.player_a_score)
            for won_card in previous_bid_targets:
                won_card.change_state(CardState.player_a_score)
        
        # player_b wins; all bid targets move to player_b_score
        elif a_sealed_bid is None or b_sealed_bid.value > a_sealed_bid.value:
            turn_result.append("b_win")
            if self.logging:
                print(f'player_b won bid\n')
            current_bid_target.change_state(CardState.player_b_score)
            for won_card in previous_bid_targets:
                won_card.change_state(CardState.player_b_score)
    
        # all playzone cards are discarded
        if a_sealed_bid is not None:
            a_sealed_bid.change_state(CardState.player_a_discard)
        if b_sealed_bid is not None:
            b_sealed_bid.change_state(CardState.player_b_discard)
        for discard_card in a_playzone:
            discard_card.change_state(CardState.player_a_discard)
        for discard_card in b_playzone:
            discard_card.change_state(CardState.player_b_discard)
        return turn_result

    def is_game_over(self):
        a_hand_count = self.player_a.hand.count_cards_left_in_hand()
        b_hand_count = self.player_b.hand.count_cards_left_in_hand()
        if self.logging:
            print(f'a_hand_count {a_hand_count} b_hand_count {b_hand_count}')
        if a_hand_count == 0 and b_hand_count == 0:
            return True
        return False

    def score_players(self):
        player_a_score = sum([card.value for card in self.deck.cards if card.state == CardState.player_a_score])
        player_b_score = sum([card.value for card in self.deck.cards if card.state == CardState.player_b_score])
        return (player_a_score, player_b_score)

    def masked_game_state(self):
        a_hand = self.player_a.hand.masked_pile_state()
        b_hand = self.player_b.hand.masked_pile_state()
        deck_state = self.deck.pile_state()
        current_score = self.score_players()
        state = {
            "player_a_cards":a_hand,
            "player_b_cards":b_hand,
            "deck_state":deck_state,
            "player_a_score":current_score[0],
            "player_b_score":current_score[1]
        }
        return state