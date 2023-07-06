from ..pgops import Pgops

class Orchestrator:
    def __init__(self, game_type, player_pool, tournament_style, matches_per_pairing=3, games_per_match=1000):
        supported_tournaments = ["round_robin"]
        supported_game_types = ["gops", "bgops", "bgops_minus"]
        if game_type not in supported_game_types:
            raise Exception(f'Game type "{game_type}" not supported. Pick from {supported_game_types}')
        else:
            self.game_type = game_type

        if tournament_style not in supported_tournaments:
            raise Exception(f'Tournament style "{tournament_style}" not supported. Pick from: {supported_tournaments}')
        else:
            self.tournament_style = tournament_style
        
        self.player_pool = player_pool

        self.matches_per_pairing = matches_per_pairing
        self.games_per_match = games_per_match

        print(f'Starting {tournament_style} tournament of {game_type} with {len(player_pool)} players, {matches_per_pairing} matches per pairing, {games_per_match} games per match.')

        self.records = {}
        for i, player in enumerate(self.player_pool):
            self.records[player.bot_name] = {
                "player": player,
                "games_played": 0,
                "matches_played": 0,
                "games_won": 0,
                "games_lost": 0,
                "games_drawn": 0,
                "matches_won": 0,
                "matches_lost": 0,
                "matches_drawn": 0
            }
        for i, player_a in enumerate(self.player_pool):
            for j, player_b in enumerate(self.player_pool):
                if i != j:
                    self.play_matches(player_a, player_b)
        self.pretty_print(self.records, indent=0)

    def play_matches(self, player_a, player_b):
        a_matches_won = 0
        a_matches_lost = 0
        b_matches_won = 0
        b_matches_lost = 0
        matches_drawn = 0
        print(f'Starting pairing between {player_a.bot_name} and {player_b.bot_name}')
        for i in range(self.matches_per_pairing):
            game = Pgops(self.game_type)
            a_games_won = 0
            a_games_lost = 0
            b_games_won = 0
            b_games_lost = 0
            games_drawn = 0
            games_played = 0
            for j in range(self.games_per_match):
                player_a.setup(game, "player_a")
                player_b.setup(game, "player_b")
                game.new_game()
                game_done = False
                while not game_done:
                    bid_card = game.next_turn()
                    a_card = player_a.select_and_play_card()
                    b_card = player_b.select_and_play_card()
                    result = game.evaluate_played_cards()
                    a_result = ""
                    b_result = ""
                    if len(result) > 1:
                        a_result = "both_spy"
                        b_result = "both_spy"
                    elif result[0] == "tie":
                        a_result = "tie"
                        b_result = "tie"
                    elif result[0] == "bomb":
                        a_result = "bomb"
                        b_result = "bomb"
                    elif result[0] == "a_win":
                        a_result = "win"
                        b_result = "lose"
                    elif result[0] == "b_win":
                        a_result = "lose"
                        b_result = "win"
                    elif result[0] == "a_spy":
                        a_result = "my_spy"
                        b_result = "opponent_spy"
                    elif result[0] == "b_spy":
                        a_result = "opponent_spy"
                        b_result = "my_spy"
                    player_a.turn_over(a_card, b_card, bid_card, a_result)
                    player_b.turn_over(b_card, a_card, bid_card, b_result)
                    game_done = game.is_game_over()
                games_played += 1
                score = game.score_players()
                player_a.game_over(score[0], score[1])
                player_b.game_over(score[1], score[0])
                if score[0] > score[1]:
                    a_games_won += 1
                    b_games_lost += 1
                elif score[1] > score[0]:
                    b_games_won += 1
                    a_games_lost += 1
                else:
                    games_drawn += 1
            self.records[player_a.bot_name]['games_played'] += games_played
            self.records[player_a.bot_name]['games_won'] += a_games_won
            self.records[player_a.bot_name]['games_lost'] += a_games_lost
            self.records[player_a.bot_name]['games_drawn'] += games_drawn

            self.records[player_b.bot_name]['games_played'] += games_played
            self.records[player_b.bot_name]['games_won'] += b_games_won
            self.records[player_b.bot_name]['games_lost'] += b_games_lost
            self.records[player_b.bot_name]['games_drawn'] += games_drawn
            player_a.match_over(a_games_won, b_games_won, games_drawn)
            player_b.match_over(b_games_won, a_games_won, games_drawn)
            if a_games_won > b_games_won:
                a_matches_won += 1
                b_matches_lost += 1
            elif b_games_won > a_games_won:
                a_matches_lost += 1
                b_matches_won += 1
            else:
                matches_drawn += 1
        self.records[player_a.bot_name]['matches_played'] += self.matches_per_pairing
        self.records[player_a.bot_name]['matches_won'] += a_matches_won
        self.records[player_a.bot_name]['matches_lost'] += a_matches_lost
        self.records[player_a.bot_name]['matches_drawn'] += matches_drawn

        self.records[player_b.bot_name]['matches_played'] += self.matches_per_pairing
        self.records[player_b.bot_name]['matches_won'] += b_matches_won
        self.records[player_b.bot_name]['matches_lost'] += b_matches_lost
        self.records[player_b.bot_name]['matches_drawn'] += matches_drawn

    def pretty_print(self, d, indent=0):
        for key, value in d.items():
            print('\t' * indent + str(key))
            if isinstance(value, dict):
                self.pretty_print(value, indent+1)
            else:
                print('\t' * (indent+1) + str(value))