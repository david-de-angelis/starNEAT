from typing import Iterable
from catanatron.game import Action, Color, Game, Player
from catanatron.models.enums import ActionPrompt
from starNEAT.BrainEmulator import EmulatedBrain
import custom_state_functions

class MyPlayer(Player):

  def __init__(self, brain, color):
    assert type(brain) == MyBrain
    self.brain = brain
    self.brain.color = color
    super().__init__(color)

  def decide(self, game: Game, playable_actions: Iterable[Action]):
    return self.brain.decide(game, playable_actions)


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
      # list of all actions https://catanatron.readthedocs.io/en/latest/catanatron_gym.envs.html?highlight=actions#catanatron_gym.envs.catanatron_env.CatanatronEnv.get_valid_actions
      # https://catanatron.readthedocs.io/en/latest/catanatron.html#module-catanatron.state
      # game.state.board
      # game.state.player_state
      num_playable_actions = len(playable_actions)
      # if (num_playable_actions <= 1):
      #   return playable_actions[0] if num_playable_actions == 1 else None


      print("----")
      print(game.state.board.roads)
      print()


      if (game.state.is_initial_build_phase): #probably put me last, since I'll only ever be needed once per game...
        # print("game.state.board.buildings")
        # print(game.state.board.buildings)
        print("is_initial_build_phase")
        # print(playable_actions)
        # print(game.state.player_state)
        if (game.state.current_prompt == ActionPrompt.BUILD_INITIAL_SETTLEMENT):
          
          print("is_initial_build_phase.build_initial_settlement")

        elif (game.state.current_prompt == ActionPrompt.BUILD_INITIAL_ROAD):
          print("is_initial_build_phase.build_inital_road")
        
      if (game.state.is_moving_knight):
        print("is_moving_knight")
      if (game.state.is_discarding):
        print("is_discarding")
      if (game.state.is_road_building):
        print("is_road_building")

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


    # potential wanted info:
    # - inventory
    # - turn number
    # - robber position
    # - roads + color_index
    # - buildings + color_index

    def build_settlement(game: Game, playable_actions: Iterable[Action]):
      pass