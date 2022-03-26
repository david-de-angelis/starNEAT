from __future__ import print_function

import os
import neat
import visualize

from starNEAT.BrainGenome import BrainGenome
from starNEAT.nn.FeedForward import FeedForward

# 2-input XOR inputs and expected outputs.
xor_inputs = [(0.0, 0.0), (0.0, 1.0), (1.0, 0.0), (1.0, 1.0)]
xor_outputs = [   (0.0,),     (1.0,),     (1.0,),     (0.0,)]

class Execution():
    move_robber_id = "move_robber"
    build_city_id = "build_city"
    build_road_id = "build_road"
    build_settlement_id = "build_settlement"

    lobe_move_robber_config = None
    lobe_build_city_config = None
    lobe_build_road_config = None
    lobe_build_settlement_config = None


    @staticmethod
    def evaluate_genomes(genomes, global_config):
        for genome_id, genome in genomes:
            Execution.evaluate_genome(genome, global_config.genome_config)


    @staticmethod
    def evaluate_genome(genome, genome_config):

        #Establishing required variables
        Execution.set_lobe_config_cache(genome_config)
        lobe_move_robber = genome.lobes[Execution.move_robber_id]
        lobe_build_city = genome.lobes[Execution.build_city_id]
        lobe_build_road = genome.lobes[Execution.build_road_id]
        lobe_build_settlement = genome.lobes[Execution.build_settlement_id]

        #Evaluating Genome
        genome.fitness = 4.0
        nn_move_robber = FeedForward.create(lobe_move_robber, Execution.lobe_move_robber_config) #remember that this is currently only creating one lobe...
        for xi, xo in zip(xor_inputs, xor_outputs):
            output = nn_move_robber.activate(xi)
            # should probably also set the same fitness value for the lobes, 
            # (or if the use-case merits individual fitness, then that is also possible, 
            # however it would only impact the cross_over, and not the gene_pool selection itself)
            genome.fitness -= (output[0] - xo[0]) ** 2 


    @staticmethod
    def set_lobe_config_cache(genome_config):
        if (Execution.lobe_move_robber_config == None):
            Execution.lobe_move_robber_config = genome_config.brain_lobes_config[Execution.move_robber_id]
        if (Execution.lobe_build_city_config == None):
            Execution.lobe_build_city_config = genome_config.brain_lobes_config[Execution.build_city_id]
        if (Execution.lobe_build_road_config == None):
            Execution.lobe_build_road_config = genome_config.brain_lobes_config[Execution.build_road_id]
        if (Execution.lobe_build_settlement_config == None):
            Execution.lobe_build_settlement_config = genome_config.brain_lobes_config[Execution.build_settlement_id]
    
    @staticmethod
    def run(config_file, num_generations):
        # Initialise configuration.
        population_type = neat.Population
        genome_type = BrainGenome
        reproduction_type = neat.DefaultReproduction
        species_set_type = neat.DefaultSpeciesSet
        stagnation_type = neat.DefaultStagnation
        config = neat.Config(genome_type, reproduction_type, species_set_type, stagnation_type, config_file)

        # Create the population, which is the top-level object for a NEAT run.
        population = population_type(config)

        # Add execution reporters (monitors the execution throughout its lifetime)
        statistics_reporter = neat.StatisticsReporter()
        reporters = [
            neat.StdOutReporter(True),
            statistics_reporter,
            neat.Checkpointer(5)
        ]

        for reporter in reporters:
            population.add_reporter(reporter)

        # Execute the evaluation & evolution.
        best_genome = population.run(Execution.evaluate_genomes, num_generations)

        # Display the winning genome.
        print('\nBest genome:\n{!s}'.format(best_genome))

        # Show output of the most fit genome against training data.
        print('\nOutput:')
        winner_net = neat.nn.FeedForwardNetwork.create(best_genome, config)
        for xi, xo in zip(xor_inputs, xor_outputs):
            output = winner_net.activate(xi)
            print("input {!r}, expected output {!r}, got {!r}".format(xi, xo, output))

        node_names = {-1:'A', -2: 'B', 0:'A XOR B'}
        visualize.draw_net(config, best_genome, True, node_names=node_names)
        visualize.plot_stats(statistics_reporter, ylog=False, view=True)
        visualize.plot_species(statistics_reporter, view=True)

        population = neat.Checkpointer.restore_checkpoint('neat-checkpoint-4')
        population.run(Execution.evaluate_genomes, 10)


if __name__ == '__main__':
    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.

    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward')
    Execution.run(config_path, 300)
