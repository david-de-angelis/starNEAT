from __future__ import print_function

import neat

from starNEAT.BrainGenome import BrainGenome
from starNEAT.nn.FeedForward import FeedForward
from starNEAT.BrainEmulator import EmulatedBrain

class starNEAT():

  def __init__(self, config_file_path, epochs, checkpoint = None):
    assert len(self.lobes) > 0

    self.config_file_path = config_file_path
    self.epochs = epochs
    self.statistics_reporter = None
    self.neural_network_type = FeedForward
    self.config = neat.Config(BrainGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, self.config_file_path)
    # the population is the top-level object for the NEAT algorithm.
    if checkpoint == None:
      print("Initialising population from scratch:")
      self.population = neat.Population(self.config)
    else:
      print("Initialising population with checkpoint:", checkpoint)
      self.population = self.get_population_from_checkpoint(checkpoint) 

    print("starNEAT initialisation complete.")

  def get_population_from_checkpoint(self, checkpoint):
    population = neat.Checkpointer.restore_checkpoint(checkpoint)
    return population

  """
    Runs the starNEAT algorithm
    Return:
      type=BrainGenome: The genome of the best agent
  """
  def run(self, checkpoint = None):
    # Execute the evaluation & evolution.
    return self.population.run(self.evaluate_genomes, self.epochs)


  def evaluate_genomes(self, genomes, global_config):
    for genome_id, genome in genomes:
      self.evaluate_genome(genome, global_config.genome_config)


  def evaluate_genome(self, genome, genome_config): 
    brain = EmulatedBrain(genome, genome_config, self.neural_network_type, self.lobes)
    raise NotImplementedError("This is a context-specific function")
