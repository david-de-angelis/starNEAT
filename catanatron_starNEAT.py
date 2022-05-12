from __future__ import print_function
from catanatron.game import Color, Game
from catanatron.models.player import RandomPlayer
from starNEAT.starNEAT import starNEAT
from custom_state_functions import get_fitness_from_game_state

import os
import sys
import neat
import random
import visualise.visualise as visualise

from MyPlayer import MyBrain
from MyPlayer import MyPlayer

class Experiment(starNEAT):
  lobes = ["move_robber", "build_city", "build_road", "build_settlement"]

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
      neat.Checkpointer(generation_interval=100, filename_prefix='checkpoints/starNEAT-checkpoint-')
    ]

    for reporter in reporters:
      self.population.add_reporter(reporter)


  def evaluate_genomes(self, genomes, global_config):
    # Get the same (type of) opponent for all of the population
    opponent_type = self.get_worthy_opponent_type()
    for genome_id, genome in genomes:
      num_games = 1 # should we only play one game per genome to evaluate the population?
      self.evaluate_genome(genome, global_config.genome_config, opponent_type, num_games=num_games)


  """
    TODO: consider making the opponent harder as the population becomes more evolved.
    Return: A valid catan opponent type
  """
  def get_worthy_opponent_type(self): 
    return RandomPlayer


  """
    create an agent from the brain
    create a game environment
    place the agent in the game environment
    calculate the agent's fitness within the environment

    Return:
      games_won (int): the number of games won
  """
  def evaluate_genome(self, genome, genome_config, opponent_type, num_games = 1): 
    brain = MyBrain(genome, genome_config, self.neural_network_type, self.lobes)

    games_won = 0
    player_cumulative_fitness = 0.0

    for i in range(num_games):
      game = self.play_game(brain, opponent_type)
      # any value above 10 is effectively equal to 10 in the game of Catan, all are considered a win, none of which is better than the other.
      player_cumulative_fitness += min(get_fitness_from_game_state(game, Color.BLUE), 10.0) #User's player should always be BLUE.
      if game.winning_color() == Color.BLUE:
        games_won += 1
      

    genome.fitness = player_cumulative_fitness / num_games
    return games_won


  def play_game(self, brain, opponent_type):
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
    games_won = self.evaluate_genome(best_genome, self.config.genome_config, RandomPlayer, 100)
    print("The best genome won", games_won, "games out of 100 against a RandomPlayer!")


  def wrap_up(self, best_genome):
    # Show output of the most fit genome against training data.
    print('\nOutput:')
    self.formally_evaluate_best_genome(best_genome)
    self.show_statistics()

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
  checkpoint = "neat-checkpoint-349"
  
  print("Running", epochs, "epochs ", end="")
  if (checkpoint != None):
    print("on", checkpoint, end="")
  print("...", checkpoint)
  exit()
  Experiment(config_path, epochs, checkpoint).run()
  