import itertools
from typing import Iterable
from catanatron.game import Action, Color, Game, Player
from catanatron.models.enums import ActionPrompt, ActionType, Action
from starNEAT.BrainEmulator import EmulatedBrain
import constants
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

    def generate_playable_actions_info(self, playable_actions):
      playable_action_types_seen = constants.action_type_seen_template.copy()
      playable_actions_id_set = set()
      for playable_action in playable_actions:
        print("playable_action")
        print(playable_action)
        print(playable_actions)
        action_type = playable_action.action_type
        playable_action_types_seen[action_type] = True
        if (action_type == ActionType.MOVE_ROBBER):
          action_skeleton = (action_type, playable_action.value[0]) #We don't consider the player selection as part of the action-space.
        else:
          action_skeleton = (action_type, playable_action.value)
        action_id = constants.action_skeleton_to_action_id[action_skeleton]
        playable_actions_id_set.add(action_id)
      
      return (playable_actions_id_set, playable_action_types_seen)


    def get_best_valid_action(self, output_array, action_type: ActionType, playable_actions_id_set: set):
      output_dictionary = {index: element for index, element in enumerate(output_array)} # map each value to its index in the array
      # print("output_dictionary")
      # print(output_dictionary)
      action_skeleton = None
      action_type_offset = constants.action_type_offsets[action_type]
      for index in sorted(output_dictionary, key=output_dictionary.get, reverse=True): # enumerate over the array by grabbing the key/index of the entries with the highest 'value' first
        # print(index, output_dictionary[index])
        action_id = action_type_offset + index
        if action_id in playable_actions_id_set:
          action_skeleton = constants.action_id_to_action_skeleton[action_id]
          break

      if action_skeleton != None:
        assert action_skeleton[0] == ActionType.BUILD_SETTLEMENT
        action = custom_state_functions.get_action_from_action_skeleton(self.color, action_skeleton)
        return action
      else:
        return None

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
      
      num_playable_actions = len(playable_actions)
      if (num_playable_actions <= 1):
        return playable_actions[0] if num_playable_actions == 1 else None

      playable_actions_id_set, playable_action_types_seen = self.generate_playable_actions_info(playable_actions)
      print(playable_action_types_seen)

      # Look at generate_playable_actions(state) in catanatron.models.actions.py
      if (game.state.is_initial_build_phase): #probably put me last, since I'll only ever be needed once per game...
        if (game.state.current_prompt == ActionPrompt.BUILD_INITIAL_SETTLEMENT):
          action = self.build_settlement(game, playable_actions_id_set)
          print("action chosen:")
          print(action)
          return action

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


    def build_settlement(self, game: Game, playable_actions_id_set):
      #building appropriate input for the lobe
      input_enemy_road_allocation = custom_state_functions.get_enemy_road_allocation(game, self.color)
      input_trinary_building_ownership = custom_state_functions.get_trinary_building_ownership(game, self.color)
      input_port_resource_allocation = custom_state_functions.get_port_resource_allocation(game)
      input_tile_robber_allocation = custom_state_functions.get_tile_robber_allocation(game)
      input_tile_resource_allocation = custom_state_functions.get_tile_resource_allocation(game)
      input_tile_probabilities = custom_state_functions.get_tile_probabilities(game)
      input_longest_road_trophy_allocation = custom_state_functions.get_longest_road_trophy_allocation(game, self.color)
      input_all_player_longest_road_length = custom_state_functions.get_all_player_longest_road_length(game, self.color)

      # print("input_enemy_road_allocation", len(input_enemy_road_allocation))
      # print("input_trinary_building_ownership", len(input_trinary_building_ownership))
      # print("input_port_resource_allocation", len(input_port_resource_allocation))
      # print("input_tile_robber_allocation", len(input_tile_robber_allocation))
      # print("input_tile_resource_allocation", len(input_tile_resource_allocation))
      # print("input_tile_probabilities", len(input_tile_probabilities))
      # print("input_longest_road_trophy_allocation", len(input_longest_road_trophy_allocation))
      # print("input_all_player_longest_road_length", len(input_all_player_longest_road_length))

      input = list(itertools.chain(input_enemy_road_allocation, input_trinary_building_ownership, input_port_resource_allocation, input_tile_robber_allocation, input_tile_resource_allocation, input_tile_probabilities, input_longest_road_trophy_allocation, input_all_player_longest_road_length))
      output = self.lobe_build_settlement.activate(input)
      action = self.get_best_valid_action(output, ActionType.BUILD_SETTLEMENT, playable_actions_id_set)
      return action