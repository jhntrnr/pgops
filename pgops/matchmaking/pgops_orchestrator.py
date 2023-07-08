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
                "elo": 1500,
                "games_played": 0,
                "matches_played": 0,
                "games_won": 0,
                "games_lost": 0,
                "games_drawn": 0,
                "matches_won": 0,
                "matches_lost": 0,
                "matches_drawn": 0
            }
        schedule = self.round_robin_schedule(len(self.player_pool))
        for tournament_round in schedule:
            for pairing in tournament_round:
                player_a = self.player_pool[pairing[0]]
                player_b = self.player_pool[pairing[1]]
                self.play_matches(player_a, player_b)
        self.pretty_print(self.records, indent=0)

    def round_robin_schedule(self, n):
        """
        Generate a round-robin tournament schedule for `n` teams.
        https://stackoverflow.com/a/14171731
        """
        m = n + n % 2
        for r in range(m - 1):
            def pairing():
                if r < n - 1:
                    yield r, n - 1
                for i in range(m // 2 - 1):
                    p, q = (r + i + 1) % (m - 1), (m + r - i - 2) % (m - 1)
                    if p < n - 1 and q < n - 1:
                        yield p, q
            yield list(pairing())

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
                    elo_result = 1
                    a_games_won += 1
                    b_games_lost += 1
                elif score[1] > score[0]:
                    elo_result = 0
                    b_games_won += 1
                    a_games_lost += 1
                else:
                    elo_result = 0.5
                    games_drawn += 1
                new_elo = record_match(self.records[player_a.bot_name]['elo'], self.records[player_b.bot_name]['elo'], elo_result)
                self.records[player_a.bot_name]['elo'] = new_elo[0]
                self.records[player_b.bot_name]['elo'] = new_elo[1]
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

def record_match(player, opponent, result, k=30):
    """Updates ELO of player and opponent
    result is 0 for a loss; 0.5 for a draw; 1 for a win
    result is from the perspective of 'player'
    """
    expected_player = compare_rating(player, opponent)
    expected_opponent = compare_rating(opponent, player)

    if result == 0.5:
        score_player = 0.5
        score_opponent = 0.5

    elif result == 1:
        score_player = 1.0
        score_opponent = 0.0

    else:
        score_player = 0.0
        score_opponent = 1.0

    new_player = player + k * (score_player - expected_player)
    new_opponent = opponent + k * (score_opponent - expected_opponent)
    if new_player < 0:
        new_player = 0
        new_opponent = opponent - player
    if new_opponent < 0:
        new_opponent = 0
        new_player = player - opponent
    player = new_player
    opponent = new_opponent
    return(player, opponent)

def compare_rating(player, opponent):
    return ( 1+10**((opponent-player)/400.0)) ** -1