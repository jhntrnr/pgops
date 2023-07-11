import os
import importlib
import inspect
import argparse

from pgops.bots.pgops_bot import PgopsBot
from pgops.matchmaking.pgops_orchestrator import Orchestrator

def load_bots(bot_dir, game_type):
    """Load all PgopsBot classes from python scripts in a specific directory.
    Excludes bot_template and human_player."""
    bots = []

    bot_files = [f[:-3] for f in os.listdir(bot_dir) if f.endswith('.py')]
    for bot_file in bot_files:
        if bot_file == "__init__" or bot_file == "bot_template" or bot_file == "human_player":
            continue
        
        try:
            module = importlib.import_module(f'pgops.bots.examples.{bot_file}')
        except ModuleNotFoundError:
            print(f'Could not import module {bot_file}')
            continue
        
        classes = inspect.getmembers(module, inspect.isclass)

        for name, obj in classes:
            if issubclass(obj, PgopsBot) and obj is not PgopsBot:
                bots.append(obj(game_type))
                print(f'loaded bot from file {bot_file}')

    return bots

def get_args():
    parser = argparse.ArgumentParser(description='Run a bot tournament')
    parser.add_argument('-b', '--bot_dir', default='./pgops/bots/examples', 
                        help='Path to directory containing bot scripts')
    parser.add_argument('-v', '--game_type', default='gops', 
                        choices=['gops', 'bgops', 'bgops_minus'],
                        help='Type of the game to be played')
    parser.add_argument('-m', '--matches', type=int, default=4,
                        help='Number of matches per pairing per round')
    parser.add_argument('-g', '--games', type=int, default=1000,
                        help='Number of games per match')
    parser.add_argument('-t', '--tournaments', type=int, default=3,
                        help='Number of tournaments to run')
    parser.add_argument('-f', '--format', default='round_robin',
                        help='Tournament format')
    return parser.parse_args()

if __name__ == "__main__":
    args = get_args()


    player_pool = load_bots(args.bot_dir, args.game_type)
    tournament = Orchestrator(game_type=args.game_type,
                                player_pool=player_pool,
                                tournament_format=args.format,
                                matches_per_pairing=args.matches,
                                games_per_match=args.games,
                                num_tournaments=args.tournaments)
