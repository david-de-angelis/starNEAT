from catanatron.game import Game, Color, Player
from catanatron.state_functions import player_key
from catanatron.models.enums import BuildingType
import constants

#region ### BANK ###

# Features: 5
def get_resources_array(game: Game):
  return game.state.resource_deck.array.tolist()

#endregion

#region ### ROAD ###

# Features: 72
def get_trinary_road_ownership(game: Game, color: Color): # -1 = enemy road, 0 = unassigned road, 1 = our road
  built_roads = {}
  for road_position_tuple, road_owned_by_color in game.state.board.roads.items(): # since the roads dictionary has bi-directional roads e.g (0 -> 5) & (5 -> 0) even though they mean the same thing, we are iterating through each road twice, but not too much of a performance hit - could possibly be addressed in the future, maybe skip every other item?
    key = constants.road_tuple_to_index[road_position_tuple]
    value = 1 if road_owned_by_color == color else -1
    built_roads[key] = value

  trinary_road_ownership = constants.all_roads.copy() # copy established dictionary setting all roads to 0
  trinary_road_ownership.update(built_roads) # overwrite any values for owned fields with 1 for self-owned, or -1 for enemy owned.
  return trinary_road_ownership

# Features: 72 * N
def get_all_road_allocation(game: Game, color: Color):
  # initialise all players with 0 (false) for road ownership
  all_players_road_allocation_dictionary = {} 
  for player in game.state.players:
    player: Player = player
    all_players_road_allocation_dictionary[player.color] = constants.all_roads.copy()
  
  # for each populated road, find and update the correct players ownership
  for road_position_tuple, road_owned_by_color in game.state.board.roads.items():
    road_index = constants.road_tuple_to_index[road_position_tuple]
    all_players_road_allocation_dictionary[road_owned_by_color][road_index] = 1

  # compress all_road_allocation dictionary to be a flat array - own roads should be laid out first
  all_players_road_allocation = []
  for player_color, player_road_allocation_dictionary in all_players_road_allocation_dictionary.items():
    if player_color == color:
      all_players_road_allocation.insert(0, list(player_road_allocation_dictionary.values())) #append to start
    else:
      all_players_road_allocation.append(list(player_road_allocation_dictionary.values()))

  return all_players_road_allocation


def get_enemy_road_allocation(game: Game, color: Color):
    # initialise all players with 0 (false) for road ownership
  all_enemies_road_allocation_dictionary = {} 
  for player in game.state.players:
    player: Player = player
    if (player.color != color): # do not include own player
      all_enemies_road_allocation_dictionary[player.color] = constants.all_roads.copy()
  
  # for each populated road, find and update the correct players ownership
  for road_position_tuple, road_owned_by_color in game.state.board.roads.items():
    if (road_owned_by_color != color):
      road_index = constants.road_tuple_to_index[road_position_tuple]
      all_enemies_road_allocation_dictionary[road_owned_by_color][road_index] = 1

  # compress all_road_allocation dictionary to be a flat array - own roads should be laid out first
  all_enemies_road_allocation = []
  for player_road_allocation_dictionary in all_enemies_road_allocation_dictionary.values():
      all_enemies_road_allocation.append(list(player_road_allocation_dictionary.values()))

  return all_enemies_road_allocation

#endregion

#region ### Building ###

# Features: 54
def get_enemy_building_exists(): # 0 for self-owned or vacant, 1 for enemy owned buildings (city or settlement)
  pass

# Features: 54
def get_own_settlement_exists(): # 0 for enemy owned or vacant, 1 for self-owned settlements
  pass

# Features: 54
def get_own_cities(game: Game, color: Color): # 0 for enemy owned or vacant, 1 for self-owned cities
  # self.buildings = dict()  # node_id => (color, building_type)
  built_cities = {}
  for node_id, (building_owned_by_color, building_type) in game.state.board.buildings.items(): # since the roads dictionary has bi-directional roads e.g (0 -> 5) & (5 -> 0) even though they mean the same thing, we are iterating through each road twice, but not too much of a performance hit - could possibly be addressed in the future, maybe skip every other item?
    if (building_type == BuildingType.CITY):
      value = 1 if building_owned_by_color == color else 0
      built_cities[node_id] = value

  trinary_road_ownership = constants.all_buildings.copy() # copy established dictionary setting all roads to 0
  trinary_road_ownership.update(built_cities) # overwrite any values for owned fields with 1 for self-owned, or -1 for enemy owned.
  return trinary_road_ownership

# Features: 54 * N
def get_all_settlement_allocation():
  pass

# Features: 54 * N
def get_all_city_allocation():
  pass

# Features: 54 * (N-1)
def get_enemy_city_allocation():
  pass

#endregion

#region ### PORT ###

# Features: 54
def get_port_resource_allocation():
  pass

#endregion

#region ### TILE ###

# Features: 19
def get_tile_robber_allocation():
  pass

# Features: 114
def get_tile_resource_allocation():
  pass

# Features: 19
def get_tile_probability():
  pass

#endregion

#region ### PLAYER ###

def get_own_resources():
  pass

def get_own_development_cards():
  pass

def get_longest_road_trophy_allocation():
  pass

def get_all_player_roads_left():
  pass

def get_all_player_settlements_left():
  pass

def get_all_player_cities_left():
  pass

def get_all_player_longest_road_length():
  pass

def get_own_actual_victory_points():
  pass

def get_all_public_victory_points():
  pass

def get_all_player_development_card_played():
  pass

#endregion

#region ### HELPER ###

def get_dictionary_values_array(dict):
  return [*dict.values()] # more efficient than list(dict.values()) for relatively small dictionaries, which we are largly working with...

def get_fitness_from_game_state(game: Game, color: Color):
  key = player_key(game.state, color)
  return game.state.player_state[f"{key}_ACTUAL_VICTORY_POINTS"]

#endregion