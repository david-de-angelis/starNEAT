from __future__ import print_function
import math
import time
from datetime import datetime
from catanatron.game import Color, Game
from catanatron.models.player import RandomPlayer
from catanatron.players.weighted_random import WeightedRandomPlayer
from catanatron.players.search import VictoryPointPlayer
import os
import sys
import neat
import random
import multiprocessing
from opponents.mcts import MCTSPlayer
import visualise.visualise as visualise

from MyPlayer import MyPlayer, MyBrain
from starNEAT.starNEAT import starNEAT
from custom_state_functions import get_fitness_from_game_state
from opponents.minimax import AlphaBetaPlayer, ValueFunctionPlayer
from opponents.playouts import GreedyPlayoutsPlayer
from reporters.AdvancedCheckpointer import AdvancedCheckpointer

class Experiment(starNEAT):
  lobes = ["move_robber", "build_road", "build_settlement", "build_city", "play_year_of_plenty", "play_monopoly", "maritime_trade", "decide_action_type"]
  def __init__(self, config_file_path, epochs, checkpoint = None):
    super().__init__(config_file_path, epochs, checkpoint)


  """
    Before Run: Add Reporters
    After Run: Give Summary

    Return:
      best_genome (starNeat.BrainGenome.BrainGenome): the best genome in the evolved population
  """
  def run(self):
    # Add execution reporters (monitors the execution throughout its lifetime)
    self.add_reporters()
    best_genome = super().run()

    #perform post-run analysis
    self.wrap_up(best_genome)
    return best_genome


  def add_reporters(self):
    time_stamp = datetime.now().strftime("%y-%m-%d-%H-%M")

    self.statistics_reporter = neat.StatisticsReporter()
    reporters = [
      neat.StdOutReporter(True),
      self.statistics_reporter,
      AdvancedCheckpointer(generation_interval=100, time_interval_seconds=None, filename_prefix='checkpoints/{0}/starNEAT-checkpoint-'.format(time_stamp), epochs=self.epochs),
    ]

    for reporter in reporters:
      self.population.add_reporter(reporter)


  def evaluate_genomes(self, genomes, global_config):
    start_time = time.time()

    opponent_type_list = self.get_worthy_opponent_type_list()
    # Multithreading the game running...
    num_genomes = len(genomes)
    remaining_genomes = num_genomes
    
    num_processors = multiprocessing.cpu_count()
    pool = multiprocessing.Pool(num_processors)
    processes = []

    standard_batch_size = math.ceil(num_genomes/num_processors)
    batch_index = 0
    batches = []

    while remaining_genomes > 0:
      batch_size = min(standard_batch_size, remaining_genomes)
      start_index = standard_batch_size * batch_index
      end_index = start_index + batch_size

      genome_subset = genomes[start_index:end_index]
      process = pool.apply_async(self.evaluate_genome_subset, args=(genome_subset, global_config.genome_config, opponent_type_list, self.neural_network_type, self.lobes))

      processes.append(process)
      batches.append(genome_subset)

      remaining_genomes -= batch_size
      batch_index += 1

    #retrieve all of the results from the multiprocessed instances
    batch_fitnesses = [p.get() for p in processes]

    #Assign the calculated fitnesses from the multiprocessing to the genome objects.
    fitnesses = {}
    for batch_fitness in batch_fitnesses:
      fitnesses.update(batch_fitness)

    for genome_id, genome in genomes:
      genome.fitness = fitnesses[genome_id]
      
    time_taken = time.time() - start_time
    print("Peformed 1000 games multithreadedly in", time_taken, "seconds...")

  @staticmethod
  def evaluate_genome_subset(genome_subset, genome_config, opponent_type_list, neural_network_type, lobes):
    subset_fitness = {}
    for genome_id, genome in genome_subset:
        fitness, games_won = Experiment.evaluate_genome(genome, genome_config, opponent_type_list, neural_network_type, lobes, num_games=10)
        subset_fitness[genome_id] = fitness

    return subset_fitness


  """
    create an agent from the brain
    create a game environment
    place the agent in the game environment
    calculate the agent's fitness within the environment

    Return:
      games_won (int): the number of games won
  """
  @staticmethod
  def evaluate_genome(genome, genome_config, opponent_type_list, neural_network_type, lobes, num_games = 1): 
    brain = MyBrain(genome, genome_config, neural_network_type, lobes)

    games_won = 0
    player_cumulative_fitness = 0.0
    opponent_type_list_index = 0

    for i in range(num_games):
      starting_game_index, opponent_type, reward_power = None, None, None
      if (len(opponent_type_list) > opponent_type_list_index + 1):
        next_starting_game_index, next_opponent_type, next_reward_power = opponent_type_list[opponent_type_list_index + 1]
        if i >= next_starting_game_index:
          opponent_type_list_index += 1
          starting_game_index, opponent_type, reward_power = next_starting_game_index, next_opponent_type, next_reward_power
    
      if (opponent_type is None):
        starting_game_index, opponent_type, reward_power = opponent_type_list[opponent_type_list_index]


      game = Experiment.play_game(brain, opponent_type)
      player_cumulative_fitness += Experiment.measure_fitness_from_game(game, reward_power, brain.color, opponent_type)

      if game.winning_color() == brain.color:
        games_won += 1
      
    fitness = player_cumulative_fitness
    return (fitness, games_won)

  @staticmethod
  def measure_fitness_from_game(game: Game, reward_power, color, opponent_type):
    fitness_from_game = get_fitness_from_game_state(game, color) # User's player should always be BLUE.
    fitness_from_game = min(float(fitness_from_game), 10.0) # any value above 10 is effectively equal to 10 in the game of Catan, all are considered a win, none of which is better than the other.

    num_turns = game.state.num_turns
    if (num_turns > 125):
      fitness_from_game -= game.state.num_turns * 0.005 # the fewer turns the better

    #bonus point if they actually won the game, (before the pow modifier, which will amplify result)
    if ((opponent_type == ValueFunctionPlayer or opponent_type == AlphaBetaPlayer) and (game.winning_color() == color)):
      fitness_from_game += 1
    
    fitness_from_game = max(fitness_from_game, 0) # should not be negative...
    fitness_from_game = math.pow(fitness_from_game, reward_power) # certain opponents may have a higher reward than others.

    return fitness_from_game


  @staticmethod
  def play_game(brain, opponent_type):
    player = MyPlayer(brain, Color.BLUE) #User's player should always be BLUE.
    opponent = Experiment.get_opponent_from_type(opponent_type, Color.RED)

    players = [ player, opponent ]
    random.shuffle(players)

    game = Game(players)
    winning_color = game.play()
    return game

  def wrap_up(self, best_genome):
    # Show output of the most fit genome against training data.
    print('\nOutput:')
    self.formally_evaluate_genome(best_genome, self.config.genome_config, self.neural_network_type, self.lobes)
    self.show_statistics()


  @staticmethod
  def formally_evaluate_genome(genome, genome_config, neural_network_type, lobes):
    print("~~~~~")
    print("Formally evaluating genome...")
    print("~~~~~")

    # Random
    num_games = 1000
    genome_fitness, games_won = Experiment.evaluate_genome(genome, genome_config, [(0, RandomPlayer, 1)], neural_network_type, lobes, num_games=num_games)
    print("The best genome won", games_won, "games out of", str(num_games), "against Random Player!")
    print(genome_fitness/num_games)

    # # VictoryPointPlayer
    # num_games = 1000
    # genome_fitness, games_won = Experiment.evaluate_genome(genome, genome_config, VictoryPointPlayer, neural_network_type, lobes, num_games=num_games)
    # print("The best genome won", games_won, "games out of", str(num_games), "against VictoryPoint Player!")

    # # WeightedRandom Player
    # num_games = 1000
    # genome_fitness, games_won = Experiment.evaluate_genome(genome, genome_config, WeightedRandomPlayer, neural_network_type, lobes, num_games=num_games)
    # print("The best genome won", games_won, "games out of", str(num_games), "against WeightedRandom Player!")

    # # GreedyPlayouts Player
    # num_games = 15
    # genome_fitness, games_won = Experiment.evaluate_genome(genome, genome_config, GreedyPlayoutsPlayer, neural_network_type, lobes, num_games=num_games)
    # print("The best genome won", games_won, "games out of", str(num_games), "against GreedyPlayouts Player!")

    # ValueFunction
    num_games = 25
    genome_fitness, games_won = Experiment.evaluate_genome(genome, genome_config, [(0, ValueFunctionPlayer, 1)], neural_network_type, lobes, num_games=num_games)
    print("The best genome won", games_won, "games out of", str(num_games), "against ValueFunction Player!")
    print(genome_fitness/num_games)

    # AlphaBeta(n=2) - CATANATRON
    num_games = 25
    genome_fitness, games_won = Experiment.evaluate_genome(genome, genome_config, [(0, AlphaBetaPlayer, 1)], neural_network_type, lobes, num_games=num_games)
    print("The best genome won", games_won, "games out of", str(num_games), "against AlphaBeta(n=2) (CATANATRON)!")
    print(genome_fitness/num_games)


  """
    TODO: consider making the opponent harder as the population becomes more evolved.
    Return: A valid catan opponent type
  """
  def get_worthy_opponent_type_list(self): 
    #from game 0, play a weighted random player, from game 5, play a value function player...
    return [(0, WeightedRandomPlayer, 1.5), (5, ValueFunctionPlayer, 2.0)] # (starting_game_index, opponent_type, reward_power)

  @staticmethod
  def get_opponent_from_type(opponent_type, opponent_color):
    #there is no good 'switch' implementation yet in this version of python :(

    if (opponent_type == RandomPlayer):
      return RandomPlayer(opponent_color) # 3 seconds per generation

    elif (opponent_type == VictoryPointPlayer):
      return VictoryPointPlayer(opponent_color) # 3 seconds per generation
      
    elif (opponent_type == WeightedRandomPlayer):
      return WeightedRandomPlayer(opponent_color) # 3 seconds per generation

    elif (opponent_type == MCTSPlayer):
      return MCTSPlayer(opponent_color) # >1 hour per generation

    elif (opponent_type == GreedyPlayoutsPlayer):
      return GreedyPlayoutsPlayer(opponent_color) # >10 minutes per generation

    elif (opponent_type == ValueFunctionPlayer): 
      return ValueFunctionPlayer(opponent_color, is_bot=False) # 20 seconds per generation
      
    elif (opponent_type == AlphaBetaPlayer):
      return AlphaBetaPlayer(opponent_color, 2, True) # 3 minutes per generation

    else:
      raise Exception("Unrecognised Opponent Type:", opponent_type)
    

  def show_statistics(self):
    try:
      visualise.plot_stats(self.statistics_reporter, ylog=False, view=True)
    except:
       print("Failed to load 'plot_stats' visualisation...")

    try:
      visualise.plot_species(self.statistics_reporter, view=True)
    except:
      print("Failed to load 'plot_species' visualisation...")


# e.g. $ python3 catanatron_startNEAT.py 20 checkpoints/starNEAT-checkpoint-16
if __name__ == '__main__':
  # Determine path to configuration file. This path manipulation is
  # here so that the script will run successfully regardless of the
  # current working directory.
  local_dir = os.path.dirname(__file__)
  config_path = os.path.join(local_dir, 'config-feedforward')

  epochs = int(sys.argv[1]) if len(sys.argv) > 1 else 20
  checkpoint = sys.argv[2] if len(sys.argv) > 2 else None
  
  print("Running", epochs, "epochs ", end="")
  if (checkpoint != None):
    print("on", checkpoint, end="")
  print("...")
  
  Experiment(config_path, epochs, checkpoint).run()
