from typing import Iterable
from catanatron.game import Game, Action, Player

class Brain():
    def __init__(self):
        print("brain")

    def decide(self, game: Game, playable_actions: Iterable[Action]):
        print("brain think")
        #if (canBuyABuilding):
        #    return buyABuilding (returns an Action) #buyABuilding is a function which interacts with a specific lobe (NN) of the brain.
        #if (canBuy...):
        #   return whatever
        #if (has more than 7 cards)
        #   do whatever
        #

class MyPlayer(Player):
    def __init__(self, color, brain, is_bot=True):
        super().__init__(color, is_bot)

        if (type(brain) != Brain):
            print("~~~ ERROR ~~~")
            print("'brain' not of type Brain")
        else:
          self.brain = brain

    def decide(self, game: Game, playable_actions: Iterable[Action]):
        
        """Should return one of the playable_actions.

        Args:
            game (Game): complete game state. read-only.
            playable_actions (Iterable[Action]): options to choose from
        Return:
            action (Action): Chosen element of playable_actions
        """
        # ===== YOUR CODE HERE =====
        return self.brain.decide(game, playable_actions)
        # As an example we simply return the first action:

        print(game)
        return playable_actions[0]
        # ===== END YOUR CODE =====