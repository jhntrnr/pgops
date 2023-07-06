# PGOPS
PGOPS is based on the playing card game "GOPS," also known as "Goofspiel."
The goal of the game is simple--score the most poins by outbidding your opponent.

## GOPS
Players start with 13 cards in their hands, Ace-King, with each card having a numerical value (Ace=1, 2=2, ... King = 13).

A separate collection of 13 cards is shuffled facedown and is the game's deck.

Each turn, a card is pulled from the deck and placed faceup between the players. This is the bid target. The players make a secret bid by selecting a card from their hand. These bids are simultaneously revealed. The player with the highest bid wins the target and places it into their score pile. The players' bid cards are discarded.

If the players tie a bid, it gets pushed. A new target card is pulled from the deck and players repeat the bidding process. The winner adds the current target and all pushed targets to his score pile.

Play continues until the players run out of cards. Players then sum the values of cards in their score piles. Highest total wins.

### BGOPS
BGOPS adds a few additional rules to further complicate the game. Players start with two additional cards in their hands--a Spy and a Bomb.

If either player plays a Bomb, all current cards in play are discarded. This includes the current bid target, any pushed targets, and all player bid cards. Bombs do not affect player hands, player score piles, or the deck.

If a player plays a Spy, they get to see their opponent's sealed bid before selecting another card to play. If both players play a Spy, players simply repeat the bid as though neither player played a Spy--in other words, two spies is not a push, it's a re-bid.

BGOPS also doubles the number of cards in the deck--two for each denomination. The number of rounds is less than the number of cards in the deck, meaning several cards will not be seen each game.

### BGOPS_MINUS
Player hands are identical to BGOPS, but the deck has an additional 13 cards. These have negative value and are subtracted from player scores at the end of a game. The deck now has 3 cards of each denomination 1-13, two of which are positive, one is negative. BGOPS_MINUS is much higher variance than BGOPS since only slightly more than a third of cards will be seen each game.

## Bots
The primary goal of PGOPS is to facillitate the creation of bots--AI players that play the game with no human input.

A template for bot creation can be found at /bots/examples/bot_template.py

See /bots/README.md for bot creation rules and guidelines.

### Tournaments
PGOPS supports round robin tournaments between bots.

See /matchmaking/README.md for further information, and tourney.py for a simple tournament between example bots.