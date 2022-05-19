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
import visualise.visualise as visualise

from MyPlayer import MyPlayer, MyBrain
from starNEAT.starNEAT import starNEAT
from custom_state_functions import get_fitness_from_game_state
from opponents.minimax import AlphaBetaPlayer, ValueFunctionPlayer
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
      AdvancedCheckpointer(generation_interval=50, time_interval_seconds=None, filename_prefix='checkpoints/{0}/starNEAT-checkpoint-'.format(time_stamp), epochs=self.epochs),
    ]

    for reporter in reporters:
      self.population.add_reporter(reporter)


  def evaluate_genomes(self, genomes, global_config):
    start_time = time.time()

    opponent_type = self.get_worthy_opponent_type()
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
      process = pool.apply_async(self.evaluate_genome_subset, args=(genome_subset, global_config.genome_config, opponent_type, self.neural_network_type, self.lobes))

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
  def evaluate_genome_subset(genome_subset, genome_config, opponent_type, neural_network_type, lobes):
    subset_fitness = {}
    for genome_id, genome in genome_subset:
        fitness, games_won = Experiment.evaluate_genome(genome, genome_config, opponent_type, neural_network_type, lobes, num_games=10)
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
  def evaluate_genome(genome, genome_config, opponent_type, neural_network_type, lobes, num_games = 1): 
    brain = MyBrain(genome, genome_config, neural_network_type, lobes)

    games_won = 0
    player_cumulative_fitness = 0.0

    for i in range(num_games):
      game = Experiment.play_game(brain, opponent_type)
      # any value above 10 is effectively equal to 10 in the game of Catan, all are considered a win, none of which is better than the other.
      fitness_from_game = min(float(get_fitness_from_game_state(game, Color.BLUE)), 10.0) #User's player should always be BLUE.
      fitness_from_game -= game.state.num_turns * 0.005 # the fewer turns the better

      player_cumulative_fitness += fitness_from_game
      if game.winning_color() == Color.BLUE:
        games_won += 1
      
    fitness = player_cumulative_fitness
    return (fitness, games_won)


  @staticmethod
  def play_game(brain, opponent_type):
    player = MyPlayer(brain, Color.BLUE) #User's player should always be BLUE.
    opponent = Experiment.get_opponent_from_type(opponent_type, Color.RED)

    players = [ player, opponent ]

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
    genome_fitness, games_won = Experiment.evaluate_genome(genome, genome_config, RandomPlayer, neural_network_type, lobes, num_games=num_games)
    print("The best genome won", games_won, "games out of", str(num_games), "against Random Player!")

    # VictoryPointPlayer
    num_games = 1000
    genome_fitness, games_won = Experiment.evaluate_genome(genome, genome_config, VictoryPointPlayer, neural_network_type, lobes, num_games=num_games)
    print("The best genome won", games_won, "games out of", str(num_games), "against VictoryPoint Player!")

    # WeightedRandom Player
    num_games = 1000
    genome_fitness, games_won = Experiment.evaluate_genome(genome, genome_config, WeightedRandomPlayer, neural_network_type, lobes, num_games=num_games)
    print("The best genome won", games_won, "games out of", str(num_games), "against WeightedRandom Player!")

    # ValueFunction
    num_games = 25
    genome_fitness, games_won = Experiment.evaluate_genome(genome, genome_config, ValueFunctionPlayer, neural_network_type, lobes, num_games=num_games)
    print("The best genome won", games_won, "games out of", str(num_games), "against ValueFunction Player!")

    # AlphaBeta(n=2) - CATANATRON
    num_games = 25
    genome_fitness, games_won = Experiment.evaluate_genome(genome, genome_config, AlphaBetaPlayer, neural_network_type, lobes, num_games=num_games)
    print("The best genome won", games_won, "games out of", str(num_games), "against AlphaBeta(n=2) (CATANATRON)!")


  """
    TODO: consider making the opponent harder as the population becomes more evolved.
    Return: A valid catan opponent type
  """
  def get_worthy_opponent_type(self): 
    return ValueFunctionPlayer

  @staticmethod
  def get_opponent_from_type(opponent_type, opponent_color):
    if (opponent_type == RandomPlayer):
      return RandomPlayer(opponent_color)
    elif (opponent_type == VictoryPointPlayer):
      return VictoryPointPlayer(opponent_color)
    elif (opponent_type == WeightedRandomPlayer):
      return WeightedRandomPlayer(opponent_color)
    elif (opponent_type == ValueFunctionPlayer):
      return ValueFunctionPlayer(opponent_color, is_bot=False)
    elif (opponent_type == AlphaBetaPlayer):
      return AlphaBetaPlayer(opponent_color, 2, True)
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


#e.g. $ python3 catanatron_startNEAT.py 20 checkpoints/starNEAT-checkpoint-16
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
