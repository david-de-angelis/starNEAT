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

    def get_best_valid_action_type(self, output_array, playable_action_types_dictionary):
      output_dictionary = {index: element for index, element in enumerate(output_array)} # map each value to its index in the array
      for index in sorted(output_dictionary, key=output_dictionary.get, reverse=True): # enumerate over the array by grabbing the key/index of the entries with the highest 'value' first
        action_type_id = index
        action_type = constants.action_type_id_to_action_type[action_type_id]
        if (playable_action_types_dictionary[action_type]):
          return action_type

      print(output_array)
      print(playable_action_types_dictionary)
      raise Exception("Returned no action type")


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
      
      # pick a colour to steal from - we dont know who has what resource though, so maybe just guess, or take from the highest scoring player...
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

      match game.state.current_prompt:
        case ActionPrompt.BUILD_INITIAL_SETTLEMENT:
          return self.build_settlement(game, playable_actions_id_set)
        case ActionPrompt.BUILD_INITIAL_ROAD:
          return self.build_road(game, playable_actions_id_set)
        case ActionPrompt.MOVE_ROBBER:
          return self.move_robber(game, playable_actions_id_set, playable_actions)
        case ActionPrompt.PLAY_TURN:
          return self.play_turn(game, playable_actions_id_set, playable_action_types_seen)
        case ActionPrompt.DISCARD:
          raise Exception("This can't occur, as it would have been addressed as the only option earlier.")
        case _:
          raise Exception("Unknown ActionPrompt", game.state.current_prompt, playable_actions)


    def play_turn(self, game, playable_actions_id_set, playable_action_types_seen):
      if (game.state.is_road_building):
        return self.build_road(game, playable_actions_id_set)
      else:
        action_type = self.decide_action_type(game, playable_action_types_seen)
        match action_type:
          case ActionType.BUILD_ROAD:
            return self.build_road(game, playable_actions_id_set)
          case ActionType.BUILD_SETTLEMENT:
            return self.build_settlement(game, playable_actions_id_set)
          case ActionType.BUILD_CITY:
            raise NotImplementedError() # ❌ lobe_build_city
          case ActionType.BUY_DEVELOPMENT_CARD:
            return self.buy_development_card()
          case ActionType.PLAY_KNIGHT_CARD:
            return self.play_knight_card()
          case ActionType.PLAY_YEAR_OF_PLENTY:
            raise NotImplementedError() # ❌ lobe_play_year_of_plenty
          case ActionType.PLAY_ROAD_BUILDING:
            self.play_road_building()
          case ActionType.PLAY_MONOPOLY:
            raise NotImplementedError() # ❌ lobe_play_monopoly 
          case ActionType.MARITIME_TRADE:
            raise NotImplementedError() # ❌ lobe_maritime_trade
          case ActionType.END_TURN:
            return self.end_turn()
          case _:
            raise Exception("Unknown ActionType", action_type, playable_actions_id_set)


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
      input_trinary_road_ownership = custom_state_functions.get_trinary_road_ownership(game, self.color)
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
      input_bank_resources_array = custom_state_functions.get_bank_resources_array(game)
      input_all_settlement_allocation = custom_state_functions.get_all_settlement_allocation(game, self.color)
      input_all_city_allocation = custom_state_functions.get_all_city_allocation(game, self.color)
      input_tile_resource_allocation = custom_state_functions.get_tile_resource_allocation(game)
      input_tile_probabilities = custom_state_functions.get_tile_probabilities(game)
      input_own_actual_victory_points = custom_state_functions.get_own_actual_victory_points(game, self.color)
      input_own_resources = custom_state_functions.get_own_resources(game, self.color)
      input_own_development_cards = custom_state_functions.get_own_development_cards(game, self.color)
      input_all_public_victory_points = custom_state_functions.get_all_public_victory_points(game, self.color)

      input = list(itertools.chain(input_bank_resources_array, input_all_settlement_allocation, input_all_city_allocation, input_tile_resource_allocation, input_tile_probabilities, input_own_actual_victory_points, input_own_resources, input_own_development_cards, input_all_public_victory_points))
      output = self.lobe_move_robber.activate(input)
      unhydrated_action = self.get_best_valid_action(output, ActionType.MOVE_ROBBER, playable_actions_id_set)
      action = self.hydrate_move_robber_action(playable_actions, unhydrated_action)
      return action


    def decide_action_type(self, game: Game, playable_action_types_seen):
      input_resources_array = custom_state_functions.get_bank_resources_array(game)
      input_bank_development_cards_count = custom_state_functions.get_bank_development_cards_count(game)
      input_all_road_allocation = custom_state_functions.get_all_road_allocation(game, self.color)
      input_all_settlement_allocation = custom_state_functions.get_all_settlement_allocation(game, self.color)
      input_all_city_allocation = custom_state_functions.get_all_city_allocation(game, self.color)
      input_port_resource_allocation = custom_state_functions.get_port_resource_allocation(game)
      input_tile_robber_allocation = custom_state_functions.get_tile_robber_allocation(game)
      input_tile_resource_allocation = custom_state_functions.get_tile_resource_allocation(game)
      input_tile_probabilities = custom_state_functions.get_tile_probabilities(game)
      input_own_actual_victory_points = custom_state_functions.get_own_actual_victory_points(game, self.color)
      input_own_resources = custom_state_functions.get_own_resources(game, self.color)
      input_own_development_cards = custom_state_functions.get_own_development_cards(game, self.color)
      input_all_players_development_cards_count = custom_state_functions.get_all_players_development_cards_count(game, self.color)
      input_all_players_resource_count = custom_state_functions.get_all_players_resource_count(game, self.color)
      input_largest_army_trophy_allocation = custom_state_functions.get_largest_army_trophy_allocation(game, self.color)
      input_longest_road_trophy_allocation = custom_state_functions.get_longest_road_trophy_allocation(game, self.color)
      input_all_player_roads_left = custom_state_functions.get_all_player_roads_left(game, self.color)
      input_all_player_settlements_left = custom_state_functions.get_all_player_settlements_left(game, self.color)
      input_all_player_cities_left = custom_state_functions.get_all_player_cities_left(game, self.color)
      input_all_player_longest_road_length = custom_state_functions.get_all_player_longest_road_length(game, self.color)
      input_all_public_victory_points = custom_state_functions.get_all_public_victory_points(game, self.color)
      input_all_player_development_card_played = custom_state_functions.get_all_player_development_card_played(game, self.color)

      input = list(itertools.chain(input_resources_array, input_bank_development_cards_count, input_all_road_allocation, input_all_settlement_allocation, input_all_city_allocation, input_port_resource_allocation, input_tile_robber_allocation, input_tile_resource_allocation, input_tile_probabilities, input_own_actual_victory_points, input_own_resources, input_own_development_cards, input_all_players_development_cards_count, input_all_players_resource_count, input_largest_army_trophy_allocation, input_longest_road_trophy_allocation, input_all_player_roads_left, input_all_player_settlements_left, input_all_player_cities_left, input_all_player_longest_road_length, input_all_public_victory_points, input_all_player_development_card_played))
      output = self.lobe_decide_action_type.activate(input)
      action_type = self.get_best_valid_action_type(output, playable_action_types_seen)
      return action_type

    def buy_development_card():
      return (ActionType.BUY_DEVELOPMENT_CARD, None)

    def play_knight_card():
      return (ActionType.PLAY_KNIGHT_CARD, None)
    
    def play_road_building():
      return (ActionType.PLAY_ROAD_BUILDING, None)

    def end_turn():
      return (ActionType.END_TURN, None)
