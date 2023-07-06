from pgops.bots.examples.random_player import RandomPlayer
from pgops.bots.examples.matching_player import MatchingPlayer
from pgops.bots.examples.matching_plus_spy import MatchingPlusSpy
from pgops.bots.examples.memory_plus import MemoryPlus
from pgops.matchmaking.pgops_orchestrator import Orchestrator

if __name__ == "__main__":
    '''
    This script will run a round robin tournament between players [a, b, c, d].
    Currently only "round_robin" tournaments are supported.
    Any number of bots can be instantiated and included in the `player_pool` list.
    Each pairing will play `matches_per_pairing` matches of `games_per_match` games.
    Pairings "a-b" and "b-a" are considered distinct.

    To force bots to play against themselves, create multiple instances of the bot and include them all in `player_pool`
    '''
    game_type = "bgops"
    a = RandomPlayer(game_type)
    b = MatchingPlayer(game_type)
    c = MatchingPlusSpy(game_type)
    d = MemoryPlus(game_type)

    z = Orchestrator(game_type=game_type, player_pool=[a, b, c, d], tournament_style="round_robin",matches_per_pairing=3, games_per_match=100)