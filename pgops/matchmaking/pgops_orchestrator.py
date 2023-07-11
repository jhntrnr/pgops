import random
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from ..pgops import Pgops

class Orchestrator:
    SUPPORTED_TOURNAMENT_FORMATS = ["round_robin", "random_matches"]
    SUPPORTED_GAME_TYPES = ["gops", "bgops", "bgops_minus"]
    STARTING_ELO = 1500
    ELO_K = 30

    def __init__(self, game_type, player_pool, tournament_format, matches_per_pairing=3, games_per_match=1000, num_tournaments=1):
        if game_type not in self.SUPPORTED_GAME_TYPES:
            raise Exception(f'Game type "{game_type}" not supported. Pick from {self.SUPPORTED_GAME_TYPES}')
        else:
            self.game_type = game_type

        if tournament_format not in self.SUPPORTED_TOURNAMENT_FORMATS:
            raise Exception(f'Tournament style "{tournament_style}" not supported. Pick from: {self.SUPPORTED_TOURNAMENT_FORMATS}')
        else:
            self.tournament_format = tournament_format
        
        self.player_pool = player_pool
        self.matches_per_pairing = matches_per_pairing
        self.games_per_match = games_per_match
        self.num_tournaments = num_tournaments

        print(f'Starting {tournament_format} tournament of {game_type} with {len(player_pool)} players, {matches_per_pairing} matches per pairing, {games_per_match} games per match.')

        self.records = self.initialize_records()
        self.pairwise_records = {}

        self.pairwise_results = {}

        if tournament_format == "round_robin":
            self.run_round_robin_tournament()
        elif tournament_format == "random_matches":
            self.run_random_tournament()

    def initialize_records(self):
        records = {}
        for i, player in enumerate(self.player_pool):
            records[player.bot_name] = {
                "player": player,
                "elo": self.STARTING_ELO,
                "games_played": 0,
                "matches_played": 0,
                "games_won": 0,
                "games_lost": 0,
                "games_drawn": 0,
                "matches_won": 0,
                "matches_lost": 0,
                "matches_drawn": 0
            }
        return records
    
    def initialize_record(self, bot_name):
        record = {
            "name": bot_name,
            "pairwise_elo": self.STARTING_ELO,
            "games_played": 0,
            "matches_played": 0,
            "games_won": 0,
            "games_lost": 0,
            "games_drawn": 0
        }
        return record

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

    def run_round_robin_tournament(self):
        for i in range(self.num_tournaments):
            random.shuffle(self.player_pool)
            schedule = self.round_robin_schedule(len(self.player_pool))
            for tournament_round in schedule:
                for pairing in tournament_round:
                    player_a = self.player_pool[pairing[0]]
                    player_b = self.player_pool[pairing[1]]
                    self.play_matches(player_a, player_b)
        
        self.pretty_print(self.records)
        self.visualize_results()

    def run_random_tournament(self):
        for i in range(self.num_tournaments):
            players = random.sample(self.player_pool, 2)
            player_a = players[0]
            player_b = players[1]
            self.play_matches(player_a, player_b)
        
        self.pretty_print(self.records)
        self.visualize_results()

    def play_matches(self, player_a, player_b):
        for i in range(self.matches_per_pairing):
            match_results = self.play_match(player_a, player_b)
            self.update_match_results(player_a, player_b, match_results)
            self.update_pairwise_records(player_a, player_b, match_results)

    def play_match(self, player_a, player_b):
        match_results = {
            'a_bot_name':player_a.bot_name,
            'b_bot_name':player_b.bot_name,
            'a_games_won': 0,
            'a_games_lost': 0,
            'b_games_won': 0,
            'b_games_lost': 0,
            'games_drawn': 0,
            'games_played': 0
        }

        game = Pgops(self.game_type)

        for j in range(self.games_per_match):
            result = self.play_game(player_a, player_b, game)
            match_results = self.update_game_results(match_results, result)
        
        return match_results

    def play_game(self, player_a, player_b, game):
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
        score = game.score_players()
        player_a.game_over(score[0], score[1])
        player_b.game_over(score[1], score[0])
        if score[0] > score[1]:
            elo_result = 1
        elif score[1] > score[0]:
            elo_result = 0
        else:
            elo_result = 0.5
        return elo_result

    def update_game_results(self, match_results, elo_result):
        pair_key = tuple(sorted((match_results['a_bot_name'], match_results['b_bot_name'])))
        if pair_key not in self.pairwise_records:
            self.pairwise_records[pair_key] = {
                match_results['a_bot_name']: self.initialize_record(match_results['a_bot_name']),
                match_results['b_bot_name']: self.initialize_record(match_results['b_bot_name'])
            }
        new_elo = self.record_match(self.records[match_results['a_bot_name']]['elo'], self.records[match_results['b_bot_name']]['elo'], elo_result)
        new_pairwise_elo = self.record_match(self.pairwise_records[pair_key][match_results['a_bot_name']]['pairwise_elo'], self.pairwise_records[pair_key][match_results['b_bot_name']]['pairwise_elo'], elo_result)

        self.records[match_results['a_bot_name']]['elo'] = new_elo[0]
        self.records[match_results['b_bot_name']]['elo'] = new_elo[1]
        self.pairwise_records[pair_key][match_results['a_bot_name']]['pairwise_elo'] = new_pairwise_elo[0]
        self.pairwise_records[pair_key][match_results['b_bot_name']]['pairwise_elo'] = new_pairwise_elo[1]
        
        match_results['games_played'] += 1
        if elo_result == 0.5:
            match_results['games_drawn'] += 1
        elif elo_result == 1:
            match_results['a_games_won'] += 1
            match_results['b_games_lost'] += 1
        elif elo_result == 0:
            match_results['a_games_lost'] += 1
            match_results['b_games_won'] += 1
        return match_results

    def update_match_results(self, player_a, player_b, match_results):
        a = player_a.bot_name
        b = player_b.bot_name
        
        self.records[a]['matches_played'] += 1
        self.records[b]['matches_played'] += 1

        a_games_won = match_results['a_games_won']
        b_games_won = match_results['b_games_won']

        self.records[a]['games_played'] += match_results['games_played']
        self.records[b]['games_played'] += match_results['games_played']

        self.records[a]['games_drawn'] += match_results['games_drawn']
        self.records[b]['games_drawn'] += match_results['games_drawn']

        self.records[a]['games_won'] += a_games_won
        self.records[b]['games_won'] += b_games_won

        self.records[a]['games_lost'] += match_results['a_games_lost']
        self.records[b]['games_lost'] += match_results['b_games_lost']
        
        if a_games_won == b_games_won:
            self.records[a]['matches_drawn'] += 1
            self.records[b]['matches_drawn'] += 1
        elif a_games_won > b_games_won:
            self.records[a]['matches_won'] += 1
            self.records[b]['matches_lost'] += 1
        elif b_games_won > a_games_won:
            self.records[a]['matches_lost'] += 1
            self.records[b]['matches_won'] += 1

    def update_pairwise_records(self, player_a, player_b, match_results):
        pair_key = tuple(sorted((player_a.bot_name, player_b.bot_name)))
        if pair_key not in self.pairwise_records:
            self.pairwise_records[pair_key] = {
                player_a.bot_name: self.initialize_record(player_a.bot_name),
                player_b.bot_name: self.initialize_record(player_b.bot_name)
            }

        self.pairwise_records[pair_key][player_a.bot_name]['matches_played'] += 1
        self.pairwise_records[pair_key][player_a.bot_name]['games_played'] += match_results['games_played']
        self.pairwise_records[pair_key][player_a.bot_name]['games_won'] += match_results['a_games_won']
        self.pairwise_records[pair_key][player_a.bot_name]['games_lost'] += match_results['a_games_lost']
        self.pairwise_records[pair_key][player_a.bot_name]['games_drawn'] += match_results['games_drawn']

        self.pairwise_records[pair_key][player_b.bot_name]['matches_played'] += 1
        self.pairwise_records[pair_key][player_b.bot_name]['games_played'] += match_results['games_played']
        self.pairwise_records[pair_key][player_b.bot_name]['games_won'] += match_results['b_games_won']
        self.pairwise_records[pair_key][player_b.bot_name]['games_lost'] += match_results['b_games_lost']
        self.pairwise_records[pair_key][player_b.bot_name]['games_drawn'] += match_results['games_drawn']

    def record_match(self, player, opponent, result):
        """Updates ELO of player and opponent
        result is 0 for a loss; 0.5 for a draw; 1 for a win
        result is from the perspective of 'player'
        """
        expected_player = self.compare_rating(player, opponent)
        expected_opponent = self.compare_rating(opponent, player)

        if result == 0.5:
            score_player = 0.5
            score_opponent = 0.5

        elif result == 1:
            score_player = 1.0
            score_opponent = 0.0

        else:
            score_player = 0.0
            score_opponent = 1.0

        new_player = player + self.ELO_K * (score_player - expected_player)
        new_opponent = opponent + self.ELO_K * (score_opponent - expected_opponent)
        if new_player < 0:
            new_player = 0
            new_opponent = opponent - player
        if new_opponent < 0:
            new_opponent = 0
            new_player = player - opponent
        player = new_player
        opponent = new_opponent
        return(player, opponent)
    
    def compare_rating(self, player, opponent):
        return ( 1+10**((opponent-player)/400.0)) ** -1

    def pretty_print(self, d, indent=0):
        for key, value in d.items():
            print('\t' * indent + str(key))
            if isinstance(value, dict):
                self.pretty_print(value, indent+1)
            else:
                print('\t' * (indent+1) + str(value))

    def visualize_results(self):
        bot_names = [player.bot_name for player in self.player_pool]
        pd.options.display.float_format = '{:.0f}'.format

        elos = {}
        for bot_name in bot_names:
            elo = self.records[bot_name]["elo"]
            elos[bot_name] = elo

        sorted_bot_names = sorted(bot_names, key=lambda x: elos[x], reverse=True)

        data = pd.DataFrame(index=sorted_bot_names, columns=sorted_bot_names)
        for bot_name in sorted_bot_names:
            data.loc[bot_name, bot_name] = round(self.records[bot_name]["elo"], 4)
        for pair, result in self.pairwise_records.items():
            data.loc[pair[0], pair[1]] = round(result[pair[0]]["pairwise_elo"], 4)
            data.loc[pair[1], pair[0]] = round(result[pair[1]]["pairwise_elo"], 4)

        data = data.apply(pd.to_numeric)
        print(data)
        plt.figure(figsize=(10, 10))
        ax = sns.heatmap(data, annot=True, cmap="flare", center=0, fmt='.0f')
        ax.tick_params(top=True, bottom=False, labeltop=True, labelbottom=False)
        ax.xaxis.set_label_position('top')
        plt.xticks(rotation=45)
        plt.show()
