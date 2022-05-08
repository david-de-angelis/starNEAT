from catanatron.game import Game, Color, Player
from catanatron.state_functions import player_key
from catanatron.models.enums import BuildingType, Action
from catanatron.models.map import Tile
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
def get_trinary_building_ownership(game: Game, color: Color): # 0 for self-owned or vacant, 1 for enemy owned buildings (city or settlement)
  built_buildings = {}
  for node_id, (building_owned_by_color, building_type) in game.state.board.buildings.items():
    value = 1 if building_owned_by_color == color else -1
    built_buildings[node_id] = value

  trinary_building_ownership = constants.all_buildings.copy() # copy established dictionary setting all roads to 0
  trinary_building_ownership.update(built_buildings) # overwrite any values for owned fields with 1 for self-owned, or -1 for enemy owned.
  return trinary_building_ownership

# Features: 54
def get_own_settlements(game: Game, color: Color): # 0 for enemy owned or vacant, 1 for self-owned settlements
  built_settlements = {}
  for node_id, (building_owned_by_color, building_type) in game.state.board.buildings.items():
    if (building_type == BuildingType.SETTLEMENT):
      value = 1 if building_owned_by_color == color else 0
      built_settlements[node_id] = value

  settlement_ownership = constants.all_buildings.copy() # copy established dictionary setting all roads to 0
  settlement_ownership.update(built_settlements) # overwrite any values for owned fields with 1 for self-owned, or -1 for enemy owned.
  return settlement_ownership

# Features: 54
def get_own_cities(game: Game, color: Color): # 0 for enemy owned or vacant, 1 for self-owned cities
  built_cities = {}
  for node_id, (building_owned_by_color, building_type) in game.state.board.buildings.items(): # since the roads dictionary has bi-directional roads e.g (0 -> 5) & (5 -> 0) even though they mean the same thing, we are iterating through each road twice, but not too much of a performance hit - could possibly be addressed in the future, maybe skip every other item?
    if (building_type == BuildingType.CITY):
      value = 1 if building_owned_by_color == color else 0
      built_cities[node_id] = value

  city_ownership = constants.all_buildings.copy() # copy established dictionary setting all roads to 0
  city_ownership.update(built_cities) # overwrite any values for owned fields with 1 for self-owned, or -1 for enemy owned.
  return city_ownership

# Features: 54 * N
def get_all_settlement_allocation(game: Game, color: Color):
  # initialise all players with 0 (false) for road ownership
  all_players_settlement_allocation_dictionary = {} 
  for player in game.state.players:
    player: Player = player
    all_players_settlement_allocation_dictionary[player.color] = constants.all_buildings.copy()
  
  # for each populated road, find and update the correct players ownership
  for node_id, (building_owned_by_color, building_type) in game.state.board.buildings.items():
    if (building_type == BuildingType.SETTLEMENT):
      all_players_settlement_allocation_dictionary[building_owned_by_color][node_id] = 1

  # compress all_road_allocation dictionary to be a flat array - own roads should be laid out first
  all_players_settlement_allocation = []
  for player_color, player_settlement_allocation_dictionary in all_players_settlement_allocation_dictionary.items():
    if player_color == color:
      all_players_settlement_allocation.insert(0, list(player_settlement_allocation_dictionary.values())) #append to start
    else:
      all_players_settlement_allocation.append(list(player_settlement_allocation_dictionary.values()))

  return all_players_settlement_allocation

# Features: 54 * N
def get_all_city_allocation(game: Game, color: Color):
   # initialise all players with 0 (false) for road ownership
  all_players_settlement_allocation_dictionary = {} 
  for player in game.state.players:
    player: Player = player
    all_players_settlement_allocation_dictionary[player.color] = constants.all_buildings.copy()
  
  # for each populated road, find and update the correct players ownership
  for node_id, (building_owned_by_color, building_type) in game.state.board.buildings.items():
    if (building_type == BuildingType.CITY):
      all_players_settlement_allocation_dictionary[building_owned_by_color][node_id] = 1

  # compress all_road_allocation dictionary to be a flat array - own roads should be laid out first
  all_players_settlement_allocation = []
  for player_color, player_settlement_allocation_dictionary in all_players_settlement_allocation_dictionary.items():
    if player_color == color:
      all_players_settlement_allocation.insert(0, list(player_settlement_allocation_dictionary.values())) #append to start
    else:
      all_players_settlement_allocation.append(list(player_settlement_allocation_dictionary.values()))

  return all_players_settlement_allocation

# Features: 54 * (N-1)
def get_enemy_city_allocation(game: Game, color: Color):
  # initialise all players with 0 (false) for road ownership
  all_players_settlement_allocation_dictionary = {} 
  for player in game.state.players:
    player: Player = player
    if (player.color != color): # do not include own player
      all_players_settlement_allocation_dictionary[player.color] = constants.all_buildings.copy()
  
  # for each populated road, find and update the correct players ownership
  for node_id, (building_owned_by_color, building_type) in game.state.board.buildings.items():
    if (building_type == BuildingType.CITY and building_owned_by_color != color):
      all_players_settlement_allocation_dictionary[building_owned_by_color][node_id] = 1

  # compress all_road_allocation dictionary to be a flat array - own roads should be laid out first
  enemy_players_settlement_allocation = []
  for player_color, player_settlement_allocation_dictionary in all_players_settlement_allocation_dictionary.items():
    enemy_players_settlement_allocation.append(list(player_settlement_allocation_dictionary.values()))

  return enemy_players_settlement_allocation

#endregion

#region ### PORT ###

# Features: 54
def get_port_resource_allocation(game: Game):
  portsList = list(game.state.board.map.ports_by_id.values())
  portsResourceArray = []
  for i in range(len(portsList)):
    portResourceArray = [0]*6
    port = portsList[i]

    resource_type = get_resource_type(port.resource)
    resourceIndex = constants.resources_array.index(resource_type)

    portResourceArray[resourceIndex] = 1
    portsResourceArray.extend(portResourceArray)

  return portsResourceArray

#endregion

#region ### TILE ###

# Features: 19
def get_tile_robber_allocation(game: Game):
  robber_coordinates = game.state.board.robber_coordinate
  robber_tile_id = constants.board_coordinate_to_tile_id[robber_coordinates]

  tile_robber_allocation = [0]*19
  tile_robber_allocation[robber_tile_id] = 1

  assert len(tile_robber_allocation) == 19
  return tile_robber_allocation

# Features: 114
def get_tile_resource_allocation(game: Game):
  tile_resource_allocation = []
  for tile in game.state.board.map.tiles_by_id.values():
    resource_type = get_resource_type(tile.resource)
    resource_index = constants.resources_array.index(resource_type)

    tile_resource = [0]*6
    tile_resource[resource_index] = 1
    tile_resource_allocation.extend(tile_resource)

  assert len(tile_resource_allocation) == 114
  return tile_resource_allocation

# Features: 19
def get_tile_probabilities(game: Game):
  tile_probabilities = []
  for tile in game.state.board.map.tiles_by_id.values():
    tile_probabilities.append(constants.board_number_to_probability[tile.number])
  return tile_probabilities

#endregion

#region ### PLAYER ###

## Illegal - should not be able to view other players resources...
# # Features: 5N
# def get_all_player_resources(game: Game, color: Color): #Make sure own color first
#   all_player_resources_dictionary = {}
#   ps = game.state.player_state
#   for player in game.state.players:
#     player_index = game.state.color_to_index[player.color]
#     prefix = "P" + str(player_index) + "_"
#     player_resource_array = [
#       ps[prefix + "WOOD_IN_HAND"],
#       ps[prefix + "BRICK_IN_HAND"],
#       ps[prefix + "SHEEP_IN_HAND"],
#       ps[prefix + "WHEAT_IN_HAND"],
#       ps[prefix + "ORE_IN_HAND"],
#     ]
#     all_player_resources_dictionary[player_index] = player_resource_array

#   all_player_resources_array = []
#   current_player_index = game.state.color_to_index[color]
#   all_player_resources_array.extend(all_player_resources_dictionary[current_player_index])
#
#   # use get_flat_array_from_all_player_index_dictionary instead
#   for player_index, player_resources in all_player_resources_dictionary.items():
#     if (player_index == current_player_index):
#       continue
#     else:
#       all_player_resources_array.extend(player_resources)

#   return all_player_resources_array

# Features: 5N
def get_own_resources(game: Game, color: Color): #Make sure own color first
  current_player_index = game.state.color_to_index[color]
  prefix = "P" + str(current_player_index) + "_"

  ps = game.state.player_state
  player_resource_array = [
    ps[prefix + "WOOD_IN_HAND"],
    ps[prefix + "BRICK_IN_HAND"],
    ps[prefix + "SHEEP_IN_HAND"],
    ps[prefix + "WHEAT_IN_HAND"],
    ps[prefix + "ORE_IN_HAND"],
  ]

  return player_resource_array

# Features: 5
def get_own_development_cards(game: Game, color: Color):
  current_player_index = game.state.color_to_index[color]
  prefix = "P" + str(current_player_index) + "_"

  ps = game.state.player_state
  player_development_card_array = [
    ps[prefix + "KNIGHT_IN_HAND"],
    ps[prefix + "YEAR_OF_PLENTY_IN_HAND"],
    ps[prefix + "MONOPOLY_IN_HAND"],
    ps[prefix + "ROAD_BUILDING_IN_HAND"],
    ps[prefix + "VICTORY_POINT_IN_HAND"],
  ]

  return player_development_card_array

# Features: N
def get_longest_road_trophy_allocation(game: Game, color: Color): #Make sure own color first
  return get_player_state_statistics(game, color, ["HAS_ROAD"])
  # all_player_roads_dictionary = {}
  # ps = game.state.player_state
  # for player in game.state.players:
  #   player_index = game.state.color_to_index[player.color]
  #   prefix = "P" + str(player_index) + "_"
  #   player_has_longest_road_array = [
  #     ps[prefix + "HAS_ROAD"],
  #   ]
  #   all_player_roads_dictionary[player_index] = player_has_longest_road_array

  # all_player_roads_array = get_flat_array_from_all_player_index_dictionary(game, color, all_player_roads_dictionary)
  # return all_player_roads_array

# Features: N
def get_all_player_roads_left(game: Game, color: Color): #Make sure own color first
  return get_player_state_statistics(game, color, ["ROADS_AVAILABLE"])
  # all_player_roads_left_dictionary = {}
  # ps = game.state.player_state
  # for player in game.state.players:
  #   player_index = game.state.color_to_index[player.color]
  #   prefix = "P" + str(player_index) + "_"
  #   player_roads_left_array = [
  #     ps[prefix + "ROADS_AVAILABLE"],
  #   ]
  #   all_player_roads_left_dictionary[player_index] = player_roads_left_array

  # all_player_roads_left_array = get_flat_array_from_all_player_index_dictionary(game, color, all_player_roads_left_dictionary)
  # return all_player_roads_left_array

# Features: N
def get_all_player_settlements_left(game: Game, color: Color): #Make sure own color first
  return get_player_state_statistics(game, color, ["SETTLEMENTS_AVAILABLE"])
  # all_player_settlements_left_dictionary = {}
  # ps = game.state.player_state
  # for player in game.state.players:
  #   player_index = game.state.color_to_index[player.color]
  #   prefix = "P" + str(player_index) + "_"
  #   player_settlements_left_array = [
  #     ps[prefix + "SETTLEMENTS_AVAILABLE"],
  #   ]
  #   all_player_settlements_left_dictionary[player_index] = player_settlements_left_array

  # all_player_settlements_left_array = get_flat_array_from_all_player_index_dictionary(game, color, all_player_settlements_left_dictionary)
  # return all_player_settlements_left_array

# Features: N
def get_all_player_cities_left(game: Game, color: Color): #Make sure own color first
  return get_player_state_statistics(game, color, ["CITIES_AVAILABLE"])
  # all_player_cities_left_dictionary = {}
  # ps = game.state.player_state
  # for player in game.state.players:
  #   player_index = game.state.color_to_index[player.color]
  #   prefix = "P" + str(player_index) + "_"
  #   player_cities_left_array = [
  #     ps[prefix + "CITIES_AVAILABLE"],
  #   ]
  #   all_player_cities_left_dictionary[player_index] = player_cities_left_array

  # all_player_cities_left_array = get_flat_array_from_all_player_index_dictionary(game, color, all_player_cities_left_dictionary)
  # return all_player_cities_left_array

# Features: N
def get_all_player_longest_road_length(game: Game, color: Color): #Make sure own color first
  return get_player_state_statistics(game, color, ["LONGEST_ROAD_LENGTH"])

# Features: 1
def get_own_actual_victory_points(game: Game, color: Color):
  current_player_index = game.state.color_to_index[color]
  prefix = "P" + str(current_player_index) + "_"

  ps = game.state.player_state
  player_own_actual_victory_points_array = [
    ps[prefix + "ACTUAL_VICTORY_POINTS"],
  ]

  return player_own_actual_victory_points_array

# Features: N
def get_all_public_victory_points(game: Game, color: Color): #Make sure own color first
  return get_player_state_statistics(game, color, ["VICTORY_POINTS"])

def get_all_player_development_card_played(game: Game, color: Color): #Make sure own color first
  return get_player_state_statistics(game, color, ["PLAYED_KNIGHT", "PLAYED_YEAR_OF_PLENTY", "PLAYED_MONOPOLY", "PLAYED_ROAD_BUILDING", "PLAYED_VICTORY_POINT"])

#endregion

#region ### HELPER ###

def get_dictionary_values_array(dict):
  return [*dict.values()] # more efficient than list(dict.values()) for relatively small dictionaries, which we are largly working with...

def get_fitness_from_game_state(game: Game, color: Color):
  key = player_key(game.state, color)
  return game.state.player_state[f"{key}_ACTUAL_VICTORY_POINTS"]

def get_resource_type(resource):
  resource_type = resource.value if resource != None else None
  return resource_type

def get_action_from_action_skeleton(color: Color, action_skeleton):
  return Action(color, action_skeleton[0], action_skeleton[1])

def get_flat_array_from_all_player_index_dictionary(game: Game,  color: Color, all_player_dictionary):
  current_player_index = game.state.color_to_index[color]
  all_player_array = all_player_dictionary[current_player_index]

  for player_index, player_resources in all_player_dictionary.items():
    if (player_index == current_player_index):
      continue
    else:
      all_player_array.extend(player_resources)

  return all_player_array

def get_player_state_statistics(game: Game, color: Color, statistics):
  all_player_statistics_dictionary = {}
  ps = game.state.player_state
  for player in game.state.players:
    player_index = game.state.color_to_index[player.color]
    prefix = "P" + str(player_index) + "_"
    player_statistics_array = []
    for statistic in statistics:
      player_statistics_array.append(ps[prefix + statistic])

    all_player_statistics_dictionary[player_index] = player_statistics_array

  all_player_statistics_array = get_flat_array_from_all_player_index_dictionary(game, color, all_player_statistics_dictionary)
  return all_player_statistics_array
#endregion
