# Tournaments
A tournament between bots can be run by creating an Orchestrator object like so:
```
from pgops.matchmaking.pgops_orchestrator import Orchestrator
from pgops.bots.examples.random_player import RandomPlayer
from pgops.bots.examples.matching_player import MatchingPlayer

game_type = "bgops"
a = RandomPlayer(game_type)
b = MatchingPlayer(game_type)
tournament = Orchestrator(game_type=game_type, 
        player_pool=[a, b],
        tournament_style="round_robin",
        matches_per_pairing=3,
        games_per_match=100)
```

TODO:
- Add further tournament documentation
- Support multiple tournament types
- Add ELO system
- Add persistent performance tracking