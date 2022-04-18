from typing import Iterable
from catanatron.game import Action, Game, Player
from starNEAT.BrainEmulator import EmulatedBrain

class MyBrain(EmulatedBrain):

    def __init__(self, genome, genome_config, neural_network_type, lobes):
        super().__init__(genome, genome_config, neural_network_type, lobes)


    """ 
      Based on the perceived environment take an action...
      This involves the following primary steps:
        1. Deciding which lobe(s) to invoke
        2. Probing the lobe(s) for a response
        3. Mapping the response to a valid action.

      Args:
        game (Game): complete game state. read-only.
        playable_actions (Iterable[Action]): options to choose from

      Return: 
        action (catanatron.game.Action): a valid action
    """
    def decide(self, game: Game, playable_actions: Iterable[Action]):
      return playable_actions[0]

      # raise NotImplementedError("still needs to be developed")
      #e.g.
      # if (canBuyABuilding):
      #     return buyABuilding (returns an Action) #buyABuilding is a function which interacts with a specific lobe (NN) of the brain.
      # if (canBuy...):
      #    return whatever
      # if (has more than 7 cards)
      #    do whatever
      # 

      # for xi, xo in zip(xor_inputs, xor_outputs):
      #   output = nn_move_robber.activate(xi)
      #   # should probably also set the same fitness value for the lobes, 
      #   # (or if the use-case merits individual fitness, then that is also possible, 
      #   # however it would only impact the cross_over, and not the gene_pool selection itself)
      #   genome.fitness -= (output[0] - xo[0]) ** 2 

class MyPlayer(Player):

  def __init__(self, brain, colour):
    assert type(brain) == MyBrain
    self.brain = brain

    super().__init__(colour)


  """
    Should return one of the playable_actions.

    Args:
        game (Game): complete game state. read-only.
        playable_actions (Iterable[Action]): options to choose from

    Return:
        action (catanatron.game.Action): Chosen element of playable_actions
  """
  def decide(self, game: Game, playable_actions: Iterable[Action]):
    return self.brain.decide(game, playable_actions)