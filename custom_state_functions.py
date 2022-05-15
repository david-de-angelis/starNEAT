# NOTE: descriptive text for functions was sourced from https://catanatron.readthedocs.io/en/latest/catanatron_gym.envs.html

import itertools
from catanatron.game import Game, Color, Player
from catanatron.state_functions import player_key
from catanatron.models.enums import BuildingType, Action
from catanatron.models.map import Tile

import constants

#region ### BANK ###

# Number of cards of that resource in bank
# Features: 5
def get_bank_resources_array(game: Game):
  return game.state.resource_deck.array.tolist()

# Number of development cards in bank
# Features: 1
def get_bank_development_cards_count(game: Game):
  development_deck_resource_count = game.state.development_deck.array.tolist()
  return [sum(development_deck_resource_count)]

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
  return list(trinary_road_ownership.values())

# Whether edge (road) i is owned by player j
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

  return list(itertools.chain(*all_players_road_allocation))


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

  # compress all_road_allocation dictionary to be a flat array
  all_enemies_road_allocation = []
  for player_road_allocation_dictionary in all_enemies_road_allocation_dictionary.values():
      all_enemies_road_allocation.extend(list(player_road_allocation_dictionary.values()))

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
  return list(trinary_building_ownership.values())

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

# Whether player j has a city in node i
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

  return list(itertools.chain(*all_players_settlement_allocation))

# Features: 54
def get_trinary_settlement_ownership(game: Game, color: Color): # 0 for self-owned or vacant, 1 for enemy owned buildings (city or settlement)
  built_settlements = {}
  for node_id, (building_owned_by_color, building_type) in game.state.board.buildings.items():
    if (building_type == BuildingType.SETTLEMENT):
      value = 1 if building_owned_by_color == color else -1
      built_settlements[node_id] = value

  trinary_settlement_ownership = constants.all_buildings.copy() # copy established dictionary setting all settlements to 0 (unowned)
  trinary_settlement_ownership.update(built_settlements) # overwrite any values for owned fields with 1 for self-owned, or -1 for enemy owned.
  return list(trinary_settlement_ownership.values())

# Whether player j has a city in node i
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
  all_players_city_allocation = []
  for player_color, player_settlement_allocation_dictionary in all_players_settlement_allocation_dictionary.items():
    if player_color == color:
      all_players_city_allocation.insert(0, list(player_settlement_allocation_dictionary.values())) #append to start
    else:
      all_players_city_allocation.append(list(player_settlement_allocation_dictionary.values()))

  return list(itertools.chain(*all_players_city_allocation))

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

# Features: 54
def get_trinary_city_ownership(game: Game, color: Color): # 0 for self-owned or vacant, 1 for enemy owned buildings (city or settlement)
  built_cities = {}
  for node_id, (building_owned_by_color, building_type) in game.state.board.buildings.items():
    if (building_type == BuildingType.CITY):
      value = 1 if building_owned_by_color == color else -1
      built_cities[node_id] = value

  trinary_city_ownership = constants.all_buildings.copy() # copy established dictionary setting all cities to 0 (unowned)
  trinary_city_ownership.update(built_cities) # overwrite any values for owned fields with 1 for self-owned, or -1 for enemy owned.
  return list(trinary_city_ownership.values())

#endregion

#region ### PORT ###

# Whether node i is port of resource (or THREE_TO_ONE).
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

# Whether robber is on tile i.
# Features: 19
def get_tile_robber_allocation(game: Game):
  robber_coordinates = game.state.board.robber_coordinate
  robber_tile_id = constants.board_coordinate_to_tile_id[robber_coordinates]

  tile_robber_allocation = [0]*19
  tile_robber_allocation[robber_tile_id] = 1

  assert len(tile_robber_allocation) == 19
  return tile_robber_allocation

# Whether tile i yields resource (or DESERT).
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

# Whether tile i yields resource.
# Features: 95
def get_tile_resource_allocation_strict(game: Game):
  tile_resource_allocation = []
  for tile in game.state.board.map.tiles_by_id.values():
    resource_type = get_resource_type(tile.resource)

    tile_resource = [0]*5
    if (resource_type != None):
      resource_index = constants.resources_array.index(resource_type)
      tile_resource[resource_index] = 1
    tile_resource_allocation.extend(tile_resource)

  assert len(tile_resource_allocation) == 95
  return tile_resource_allocation

# Tile i’s probability of being rolled.
# Features: 19
def get_tile_probabilities(game: Game):
  tile_probabilities = []
  for tile in game.state.board.map.tiles_by_id.values():
    tile_probabilities.append(constants.board_number_to_probability[tile.number])
  return tile_probabilities

#endregion

#region ### PLAYER ###

# Number of each resource cards in hand
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

# Number of hidden resource cards player i has
# Features: N
def get_all_players_resource_count(game: Game, color: Color): #Make sure own color first
  all_player_array = [sum(get_own_resources(game, color))]

  for player_color in game.state.colors:
    if (player_color == color):
      continue #was already added earlier as the base of the array...
    else:
      all_player_array.append(sum(get_own_resources(game, player_color)))

  return all_player_array

# Number of dev-card cards in hand
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

# Number of dev-card cards in hand
# Features: 1
def get_own_road_building_development_card_count(game: Game, color: Color):
  current_player_index = game.state.color_to_index[color]
  prefix = "P" + str(current_player_index) + "_"

  ps = game.state.player_state
  player_development_card_array = [
    ps[prefix + "ROAD_BUILDING_IN_HAND"],
  ]

  return player_development_card_array

# Number of dev-card cards played
# Features: 1
def get_own_road_building_development_card_played_count(game: Game, color: Color):
  current_player_index = game.state.color_to_index[color]
  prefix = "P" + str(current_player_index) + "_"

  ps = game.state.player_state
  player_development_card_array = [
    ps[prefix + "PLAYED_ROAD_BUILDING"],
  ]

  return player_development_card_array

def get_all_road_building_development_card_played_count(game:Game, color: Color):
  return get_player_state_statistics(game, color, ["PLAYED_ROAD_BUILDING"])

# Number of hidden development cards player i has
# Features: N
def get_all_players_development_cards_count(game: Game, color: Color): #Make sure own color first
  all_player_array = [sum(get_own_development_cards(game, color))]

  for player_color in game.state.colors:
    if (player_color == color):
      continue #was already added earlier as the base of the array...
    else:
      all_player_array.append(sum(get_own_development_cards(game, player_color)))

  return all_player_array

# Whether player <i> has Longest Road
# Features: N
def get_longest_road_trophy_allocation(game: Game, color: Color):
  results = get_player_state_statistics(game, color, ["HAS_ROAD"])
  for i in range(len(results)):
    results[i] = 1 if results[i] else 0

  return results

# Whether player <i> has Largest Army
# Features: N
def get_largest_army_trophy_allocation(game: Game, color: Color):
  results = get_player_state_statistics(game, color, ["HAS_ARMY"])
  for i in range(len(results)):
    results[i] = results[i] = 1 if results[i] else 0

  return results

# Number of roads pieces player i has outside of board (left to build)
# Features: N
def get_all_player_roads_left(game: Game, color: Color):
  return get_player_state_statistics(game, color, ["ROADS_AVAILABLE"])

# Number of settlements player i has outside of board (left to build)
# Features: N
def get_all_player_settlements_left(game: Game, color: Color):
  return get_player_state_statistics(game, color, ["SETTLEMENTS_AVAILABLE"])

#Number of cities player i has outside of board (left to build)
# Features: N
def get_all_player_cities_left(game: Game, color: Color):
  return get_player_state_statistics(game, color, ["CITIES_AVAILABLE"])

# Whether player <i> has Longest Road
# Features: N
def get_all_player_longest_road_length(game: Game, color: Color):
  return get_player_state_statistics(game, color, ["LONGEST_ROAD_LENGTH"])

# Total Victory Points (including Victory Point Development Cards)
# Features: 1
def get_own_actual_victory_points(game: Game, color: Color):
  current_player_index = game.state.color_to_index[color]
  prefix = "P" + str(current_player_index) + "_"

  ps = game.state.player_state
  player_own_actual_victory_points_array = [
    ps[prefix + "ACTUAL_VICTORY_POINTS"],
  ]

  return player_own_actual_victory_points_array


# Returns the trade opportunities available to a player
# Features: 5
def get_own_resource_trade_opportunities(game: Game, color: Color):
  port_resources_array = game.state.board.get_player_port_resources(color)
  trade_opportunities = [0]*6
  for port_resource in port_resources_array:
    trade_opportunity_index = constants.port_resource_to_trade_opportunity_index[port_resource]
    trade_opportunities[trade_opportunity_index] = 1
  
  return trade_opportunities

# Returns the trade opportunities available to each player
# Features: 5N
def get_all_resource_trade_opportunities(game: Game, color: Color):
  all_player_array = get_own_resource_trade_opportunities(game, color)

  for player_color in game.state.colors:
    if (player_color == color):
      continue #was already added earlier as the base of the array...
    else:
      all_player_array.extend(get_own_resource_trade_opportunities(game, player_color))

  return all_player_array

# Calculates how many of each resource the given player will generate in a single round.
# Features: 5
def get_own_resource_income_opportunities(game: Game, color: Color): #TODO: rewrite this to make it cleaner...
  all_buildings = game.state.buildings_by_color[color]
  settlements = all_buildings[BuildingType.SETTLEMENT]
  cities = all_buildings[BuildingType.CITY]
  
  
  resource_income_opportunities = [0] * 5
  for node_id in settlements:
    connected_tiles = game.state.board.map.adjacent_tiles[node_id]
    for tile in connected_tiles:
      if (tile.resource != None):
        tile_resource_index = constants.resource_to_resource_index[tile.resource]
        opportunity_value = constants.board_number_to_probability[tile.number]
        resource_income_opportunities[tile_resource_index] += opportunity_value

  for node_id in cities:
    connected_tiles = game.state.board.map.adjacent_tiles[node_id]
    for tile in connected_tiles:
      if (tile.resource != None):
        tile_resource_index = constants.resource_to_resource_index[tile.resource]
        opportunity_value = constants.board_number_to_probability[tile.number]
        opportunity_value *= 2 # because it is a city
        resource_income_opportunities[tile_resource_index] += opportunity_value

  return resource_income_opportunities

# Calculates how many of each resource each player will generate in a single round.
# Features: 5N
def get_all_resource_income_opportunities(game: Game, color: Color): #TODO: optimise this so we arent going through the all_buildings for loop in each call..
  all_player_array = get_own_resource_income_opportunities(game, color)

  for player_color in game.state.colors:
    if (player_color == color):
      continue #was already added earlier as the base of the array...
    else:
      all_player_array.extend(get_own_resource_income_opportunities(game, player_color))

  return all_player_array


# Amount of visible victory points for player i (i.e. doesn’t include hidden victory point cards; only army, road and settlements/cities).
# Features: N
def get_all_public_victory_points(game: Game, color: Color): #Make sure own color first
  return get_player_state_statistics(game, color, ["VICTORY_POINTS"])

# Amount of dev-card cards player i has played in game (VICTORY_POINT not included).
# Features: 4N
def get_all_player_development_card_played(game: Game, color: Color): #Make sure own color first
  return get_player_state_statistics(game, color, ["PLAYED_KNIGHT", "PLAYED_YEAR_OF_PLENTY", "PLAYED_MONOPOLY", "PLAYED_ROAD_BUILDING"]) #(VICTORY_POINT not included)

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

def get_flat_array_from_all_player_index_dictionary(game: Game,  color: Color, all_player_dictionary): #Make sure own color first
  current_player_index = game.state.color_to_index[color]
  all_player_array = all_player_dictionary[current_player_index]

  for player_index, player_resources in all_player_dictionary.items():
    if (player_index == current_player_index):
      continue #was already added earlier as the base of the array...
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
