import itertools
import random
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
      action_skeleton = None
      action_type_offset = constants.action_type_offsets[action_type]
      for index in sorted(output_dictionary, key=output_dictionary.get, reverse=True): # enumerate over the array by grabbing the key/index of the entries with the highest 'value' first
        action_id = action_type_offset + index
        if action_id in playable_actions_id_set:
          action_skeleton = constants.action_id_to_action_skeleton[action_id]
          break

      if action_skeleton != None:
        assert action_skeleton[0] == action_type
        return custom_state_functions.get_action_from_action_skeleton(self.color, action_skeleton)
      else:
        print(output_array)
        print(action_type)
        print(playable_actions_id_set)
        raise Exception("Returned no action")

    def hydrate_move_robber_action(self, playable_actions, unhydrated_action: Action):
      unhydrated_action_coordinate = unhydrated_action.value
      potential_actions = []
      for playable_action in playable_actions:
        playable_action : Action = playable_action
        if playable_action.action_type != ActionType.MOVE_ROBBER:
          print(playable_actions)
          raise Exception(playable_action)
        
        action_coordinate = playable_action.value[0]
        if (unhydrated_action_coordinate == action_coordinate):
          potential_actions.append(playable_action)
      
      action = random.choice(potential_actions) # TODO: take resources from other players where available
      return action


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
      action = self.decide_core(game, playable_actions)
      #print(game.state.current_prompt, "& Proceeding with action:", action)
      return action

    def decide_core(self, game: Game, playable_actions: Iterable[Action]):
      # list of all actions https://catanatron.readthedocs.io/en/latest/catanatron_gym.envs.html?highlight=actions#catanatron_gym.envs.catanatron_env.CatanatronEnv.get_valid_actions
      # https://catanatron.readthedocs.io/en/latest/catanatron.html#module-catanatron.state
      
      num_playable_actions = len(playable_actions)
      if (num_playable_actions <= 1):
        return playable_actions[0] if num_playable_actions == 1 else None

      playable_actions_id_set, playable_action_types_seen = self.generate_playable_actions_info(playable_actions)

      # Look at generate_playable_actions(state) in catanatron.models.actions.py
      match game.state.current_prompt:
        case ActionPrompt.BUILD_INITIAL_SETTLEMENT:
          return self.build_settlement(game, playable_actions_id_set)
        case ActionPrompt.BUILD_INITIAL_ROAD:
          return self.build_road(game, playable_actions_id_set)
        case ActionPrompt.MOVE_ROBBER:
          return self.move_robber(game, playable_actions_id_set, playable_actions)
        case ActionPrompt.PLAY_TURN:
          if (game.state.is_road_building):
            return self.build_road(game, playable_actions_id_set)
          
          #what if we had a neural network to decide which of these we want to do, it wouldnt decide the exact action, but it can decide which type of action to perform, i.e. whether to look at the options, which
          #involves the following:
          # - building road ✅ lobe_build_road
          # - building settlements ✅  lobe_build_settlement
          # - building cities ❌ lobe_build_city
          # - buying development cards ✅
          # - play knight card ✅
          # - play year of plenty ❌ lobe_play_year_of_plenty
          # - play road building ✅
          # - play monopoly ❌ lobe_play_monopoly
          # - performing trades ❌ lobe_perform trade
          # - ending the turn ✅
          pass
        case ActionPrompt.DISCARD:
          raise Exception("This can't occur, as it would have been addressed as the only option earlier.")
        case _:
          raise Exception("Unknown ActionPrompt", game.state.current_prompt, playable_actions)
      
      # current_prompt = 
      # if (game.state.is_initial_build_phase): #probably put me last, since I'll only ever be needed once per game...
      #   if (current_prompt == ActionPrompt.BUILD_INITIAL_SETTLEMENT):
      #     return self.build_settlement(game, playable_actions_id_set)
      #   elif (current_prompt == ActionPrompt.BUILD_INITIAL_ROAD):
      #     return self.build_road(game, playable_actions_id_set)
      #   else:
      #     raise Exception(game.state.current_prompt)
      # elif (current_prompt == ActionPrompt.MOVE_ROBBER):
      #   return self.move_robber(game, playable_actions_id_set, playable_actions)
      # elif current_prompt == ActionPrompt.DISCARD:
      #   pass
      # elif current_prompt == ActionPrompt.PLAY_TURN:
      #   pass
      # else:
      #   print(current_prompt)
      #   print(playable_actions)
      #   exit()
      #   raise RuntimeError("Unknown ActionPrompt")

      # if (game.state.is_moving_knight):
      #   print("is_moving_knight")
      # if (game.state.is_discarding):
      #   print("is_discarding")
      # if (game.state.is_road_building):
      #   return self.build_road(game, playable_actions_id_set)
      #   print("is_road_building")

      return random.choice(playable_actions)

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

      input = list(itertools.chain(input_enemy_road_allocation, input_trinary_building_ownership, input_port_resource_allocation, input_tile_robber_allocation, input_tile_resource_allocation, input_tile_probabilities, input_longest_road_trophy_allocation, input_all_player_longest_road_length))
      output = self.lobe_build_settlement.activate(input)
      action = self.get_best_valid_action(output, ActionType.BUILD_SETTLEMENT, playable_actions_id_set)
      return action


    def build_road(self, game: Game, playable_actions_id_set):
      #building appropriate input for the lobe
      input_trinary_road_ownership = custom_state_functions.get_trinary_road_ownership(game, self.color) # convert to flat list
      input_trinary_building_ownership = custom_state_functions.get_trinary_building_ownership(game, self.color)
      input_own_actual_victory_points = custom_state_functions.get_own_actual_victory_points(game, self.color)
      input_longest_road_trophy_allocation = custom_state_functions.get_longest_road_trophy_allocation(game, self.color)
      input_all_player_roads_left = custom_state_functions.get_all_player_roads_left(game, self.color)
      input_all_player_settlements_left = custom_state_functions.get_all_player_settlements_left(game, self.color)
      input_all_player_cities_left = custom_state_functions.get_all_player_cities_left(game, self.color)
      input_all_player_longest_road_length = custom_state_functions.get_all_player_longest_road_length(game, self.color)

      input = list(itertools.chain(input_trinary_road_ownership, input_trinary_building_ownership, input_own_actual_victory_points, input_longest_road_trophy_allocation, input_all_player_roads_left, input_all_player_settlements_left, input_all_player_cities_left, input_all_player_longest_road_length))
      output = self.lobe_build_road.activate(input)
      action = self.get_best_valid_action(output, ActionType.BUILD_ROAD, playable_actions_id_set)
      return action


    def move_robber(self, game: Game, playable_actions_id_set, playable_actions):
      #building appropriate input for the lobe
      input_resources_array = custom_state_functions.get_bank_resources_array(game)
      input_all_settlement_allocation = custom_state_functions.get_all_settlement_allocation(game, self.color) # flatten me
      input_all_city_allocation = custom_state_functions.get_all_city_allocation(game, self.color) # flatten me
      input_tile_resource_allocation = custom_state_functions.get_tile_resource_allocation(game)
      input_tile_probabilities = custom_state_functions.get_tile_probabilities(game)
      input_own_actual_victory_points = custom_state_functions.get_own_actual_victory_points(game, self.color)
      input_own_resources = custom_state_functions.get_own_resources(game, self.color)
      input_own_development_cards = custom_state_functions.get_own_development_cards(game, self.color)
      input_all_public_victory_points = custom_state_functions.get_all_public_victory_points(game, self.color)

      input = list(itertools.chain(input_resources_array, input_all_settlement_allocation, input_all_city_allocation, input_tile_resource_allocation, input_tile_probabilities, input_own_actual_victory_points, input_own_resources, input_own_development_cards, input_all_public_victory_points))
      output = self.lobe_move_robber.activate(input)
      unhydrated_action = self.get_best_valid_action(output, ActionType.MOVE_ROBBER, playable_actions_id_set)
      action = self.hydrate_move_robber_action(playable_actions, unhydrated_action) # pick a colour to steal from - we dont know who has what resource though, so maybe just guess, or take from the highest scoring player...
      return action