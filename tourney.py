from pgops.bots.examples.random_player import RandomPlayer
from pgops.bots.examples.matching_player import MatchingPlayer
from pgops.bots.examples.memory_plus import MemoryPlus
from pgops.bots.examples.adaptive_gops import AdaptiveGops
from pgops.bots.examples.odd_even import OddEvenBot

from pgops.matchmaking.pgops_orchestrator import Orchestrator

if __name__ == "__main__":
    '''
    This script will run a round robin tournament between players in `player_pool`.
    Currently only "round_robin" tournaments are supported.
    Any number of bots can be instantiated and included in the `player_pool` list.
    Each pairing will play `matches_per_pairing` matches of `games_per_match` games.
    Pairings "a-b" and "b-a" are considered distinct.

    To force bots to play against themselves, create multiple instances of the bot and include them all in `player_pool`
    '''

    game_type = "gops"
    
    a = RandomPlayer(game_type)
    b = MatchingPlayer(game_type)
    c = AdaptiveGops(game_type)
    d = MemoryPlus(game_type)
    e = OddEvenBot(game_type)

    player_pool = [a,b,c,d,e]
    Orchestrator(game_type=game_type, player_pool=player_pool, tournament_style="round_robin",matches_per_pairing=2, games_per_match=1000)