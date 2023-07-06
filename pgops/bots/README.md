# Bots

A PGOPS bot is simply a script that makes one decision per turn: deciding which card in its hand to play.

The details of this decision making process are up to the creator of the bot. It can be as straightforward as "always play a random card", or a highly complex system with many moving parts.

## Bot Requirements
- Every bot ***must*** inherit from `PgopsBot`. This class provides the bot with information of the current game state in a variety of methods.
- Every bot ***must*** register a `bot_name` and a list of supported game types from `["gops", "bgops", "bgops_minus"]`:
```
class BotTemplate(PgopsBot):
    def __init__(self, game_type):
        bot_name = "TEMPLATE_CHANGE_ME"
        supported_game_types = ["gops", "bgops", "bgops_minus"]
        super().__init__(game_type, supported_game_types, bot_name=bot_name)
        # additional init logic here...
```
- Every bot ***must*** implement a `select_and_play_card(card)` method that returns `self.play_card(card)` in every possible game state. `card` is a Card object from among the cards in the bot's hand.
- Every bot ***must not*** override the `setup()` and `play_card()` methods.
- Every bot ***must not*** probe the game for information not available in the `PgopsBot` methods.
- Every bot ***must*** be able to complete a tournament without crashing.

### Bot Guidelines
- Bots ***may*** override the `turn_over()`, `game_over()`, and `match_over()` methods to incorporate the provided information into their decision making processes. These methods are empty in the base `PgopsBot` class and are provided for convenience.
- Bots ***may*** cache information about previous game states throughout a tournament. Keep in mind that the number of games may be very large for tournaments with many players. Memory-intensive bots should implement some form of cache clearing to prevent crashing tournaments.
- Bots ***should*** be performant. There is currently no "play clock" to enforce prompt decision making, but very slow bots will drag a tournament down.
- Bots ***may*** import third-party packages.