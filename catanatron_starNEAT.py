from __future__ import print_function
import math
import time
from catanatron.game import Color, Game
from catanatron.models.player import RandomPlayer
from starNEAT.starNEAT import starNEAT
from custom_state_functions import get_fitness_from_game_state

import os
import sys
import neat
import random
import multiprocessing
import visualise.visualise as visualise

from MyPlayer import MyBrain
from MyPlayer import MyPlayer

class Experiment(starNEAT):
  lobes = ["move_robber", "build_road", "build_settlement", "build_city", "play_year_of_plenty", "play_monopoly", "maritime_trade", "decide_action_type"]
  def __init__(self, config_file_path, epochs):
    super().__init__(config_file_path, epochs)


  """
    Before Run: Add Reporters
    After Run: Give Summary

    Return:
      best_genome (starNeat.BrainGenome.BrainGenome): the best genome in the evolved population
  """
  def run(self, checkpoint = None):
    # Add execution reporters (monitors the execution throughout its lifetime)
    self.add_reporters()
    best_genome = super().run(checkpoint)
    #perform post-run analysis
    self.wrap_up(best_genome)
    return best_genome


  def add_reporters(self):
    self.statistics_reporter = neat.StatisticsReporter()
    reporters = [
      neat.StdOutReporter(True),
      self.statistics_reporter,
      neat.Checkpointer(generation_interval=25, filename_prefix='checkpoints/starNEAT-checkpoint-'),
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
      start_index = batch_size * batch_index
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
    for batch, batch_fitness in zip(batches, batch_fitnesses):
      for (genome_id, genome), fitness in zip(batch, batch_fitness):
        genome.fitness = fitness
      
    time_taken = time.time() - start_time
    print("Peformed 1000 games multithreadedly in", time_taken, "seconds...")

  @staticmethod
  def evaluate_genome_subset(genome_subset, genome_config, opponent_type, neural_network_type, lobes):
    subset_fitness = []
    for genome_id, genome in genome_subset:
        fitness, games_won = Experiment.evaluate_genome(genome, genome_config, opponent_type, neural_network_type, lobes, num_games=10)
        subset_fitness.append(fitness)

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
      player_cumulative_fitness += min(get_fitness_from_game_state(game, Color.BLUE), 10.0) #User's player should always be BLUE.
      if game.winning_color() == Color.BLUE:
        games_won += 1
      
    fitness = player_cumulative_fitness
    # genome.fitness = 
    return (fitness, games_won)


  @staticmethod
  def play_game(brain, opponent_type):
    player = MyPlayer(brain, Color.BLUE) #User's player should always be BLUE.
    opponent = opponent_type(Color.RED)

    # player-order impacts win-likelihood significantly, especially with two players (as opposed to 4).
    players = [ player, opponent ]
    random.shuffle(players)

    game = Game(players)
    winning_color = game.play()

    #player_fitness = get_fitness_from_game_state(game, player.color)
    #opponent_fitness = get_fitness_from_game_state(game, opponent.color)

    # print("Winning color:", winning_color, "PLAYER FITNESS: ", player_fitness, "OPPONENT FITNESS: ", opponent_fitness)
    return game


  def formally_evaluate_best_genome(self, best_genome):
    num_games = 100
    genome_fitness, games_won = self.evaluate_genome(best_genome, self.config.genome_config, RandomPlayer, self.neural_network_type, self.lobes, num_games=num_games)
    print("The best genome won", games_won, "games out of", str(num_games), "against a RandomPlayer!")


  def wrap_up(self, best_genome):
    # Show output of the most fit genome against training data.
    print('\nOutput:')
    self.formally_evaluate_best_genome(best_genome)
    self.show_statistics()


  """
    TODO: consider making the opponent harder as the population becomes more evolved.
    Return: A valid catan opponent type
  """
  def get_worthy_opponent_type(self): 
    return RandomPlayer


  def show_statistics(self):
    try:
      visualise.plot_stats(self.statistics_reporter, ylog=False, view=True)
    except:
       print("Failed to load 'plot_stats' visualisation...")

    try:
      visualise.plot_species(self.statistics_reporter, view=True)
    except:
      print("Failed to load 'plot_species' visualisation...")

if __name__ == '__main__':
  # Determine path to configuration file. This path manipulation is
  # here so that the script will run successfully regardless of the
  # current working directory.
  local_dir = os.path.dirname(__file__)
  config_path = os.path.join(local_dir, 'config-feedforward')

  epochs = int(sys.argv[1]) if len(sys.argv) > 1 else 20
  checkpoint = None #"neat-checkpoint-349"
  
  print("Running", epochs, "epochs ", end="")
  if (checkpoint != None):
    print("on", checkpoint, end="")
  print("...", checkpoint)
  
  Experiment(config_path, epochs).run()
  