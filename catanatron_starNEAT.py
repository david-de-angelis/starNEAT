from __future__ import print_function

import os
import sys
import neat
import visualise.visualise as visualise

from starNEAT.BrainGenome import BrainGenome
from starNEAT.nn.FeedForward import FeedForward

# 2-input XOR inputs and expected outputs.
xor_inputs = [(0.0, 0.0), (0.0, 1.0), (1.0, 0.0), (1.0, 1.0)]
xor_outputs = [   (0.0,),     (1.0,),     (1.0,),     (0.0,)]

class Experiment():
    ### Catan Constants ###
    move_robber_id = "move_robber"
    build_city_id = "build_city"
    build_road_id = "build_road"
    build_settlement_id = "build_settlement"

    def __init__(self, config_file_path, epochs):
        ### starNEAT Parameters ###
        self.config_file_path = config_file_path
        self.population = None
        self.epochs = epochs
        self.statistics_reporter = None
        self.neural_network_type = FeedForward
        self.config = neat.Config(BrainGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, self.config_file_path)
    
        ### Catan Parameters ###
        self.lobe_move_robber_config = None
        self.lobe_build_city_config = None
        self.lobe_build_road_config = None
        self.lobe_build_settlement_config = None

    def run(self):
        # Create the population, which is the top-level object for a NEAT run.
        self.population = neat.Population(self.config)

        # Add execution reporters (monitors the execution throughout its lifetime)
        self.add_reporters()

        # Execute the evaluation & evolution.
        best_genome = self.population.run(self.evaluate_genomes, self.epochs)

        self.wrap_up(best_genome)


    def add_reporters(self):
        self.statistics_reporter = neat.StatisticsReporter()
        reporters = [
            neat.StdOutReporter(True),
            self.statistics_reporter,
            neat.Checkpointer(5)
        ]

        for reporter in reporters:
            self.population.add_reporter(reporter)


    def evaluate_genomes(self, genomes, global_config):
        for genome_id, genome in genomes:
            self.evaluate_genome(genome, global_config.genome_config)


    def evaluate_genome(self, genome, genome_config):
        #Establishing required variables
        self.set_lobe_config_cache(genome_config)
        lobe_move_robber = genome.lobes[Experiment.move_robber_id]
        lobe_build_city = genome.lobes[Experiment.build_city_id]
        lobe_build_road = genome.lobes[Experiment.build_road_id]
        lobe_build_settlement = genome.lobes[Experiment.build_settlement_id]

        #Evaluating Genome
        genome.fitness = 4.0
        nn_move_robber = self.neural_network_type.create(lobe_move_robber, self.lobe_move_robber_config) #remember that this is currently only creating one lobe...
        for xi, xo in zip(xor_inputs, xor_outputs):
            output = nn_move_robber.activate(xi)
            # should probably also set the same fitness value for the lobes, 
            # (or if the use-case merits individual fitness, then that is also possible, 
            # however it would only impact the cross_over, and not the gene_pool selection itself)
            genome.fitness -= (output[0] - xo[0]) ** 2 


    def set_lobe_config_cache(self, genome_config):
        if (self.lobe_move_robber_config == None):
            self.lobe_move_robber_config = genome_config.brain_lobes_config[Experiment.move_robber_id]

        if (self.lobe_build_city_config == None):
            self.lobe_build_city_config = genome_config.brain_lobes_config[Experiment.build_city_id]

        if (self.lobe_build_road_config == None):
            self.lobe_build_road_config = genome_config.brain_lobes_config[Experiment.build_road_id]
            
        if (self.lobe_build_settlement_config == None):
            self.lobe_build_settlement_config = genome_config.brain_lobes_config[Experiment.build_settlement_id]


    def wrap_up(self, best_genome):
      ## Display the winning genome.
      # print('\nBest genome:\n{!s}'.format(best_genome))

      # Show output of the most fit genome against training data.
      print('\nOutput:')
      self.formally_evaluate_best_genome(best_genome)
      
      # node_names = {-1:'A', -2: 'B', 0:'A XOR B'}
      # visualise.draw_net(self.config, best_genome, True, node_names=node_names)
      visualise.plot_stats(self.statistics_reporter, ylog=False, view=True)
      visualise.plot_species(self.statistics_reporter, view=True)

      # # How to restore a population from a checkpoint:
      # population = neat.Checkpointer.restore_checkpoint('neat-checkpoint-4')
      # population.run(self.evaluate_genomes, 10)

if __name__ == '__main__':
  # Determine path to configuration file. This path manipulation is
  # here so that the script will run successfully regardless of the
  # current working directory.
  local_dir = os.path.dirname(__file__)
  config_path = os.path.join(local_dir, 'config-feedforward')

  epochs = int(sys.argv[1]) if len(sys.argv) > 1 else 20
  Experiment(config_path, epochs).run()
