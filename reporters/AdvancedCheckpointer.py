"""Uses `pickle` to save and restore populations (and other aspects of the simulation state)."""
from __future__ import print_function
import time
from neat import Checkpointer

import os
import gzip
import random

try:
    import cPickle as pickle # pylint: disable=import-error
except ImportError:
    import pickle # pylint: disable=import-error


class AdvancedCheckpointer(Checkpointer):
    """
    A reporter class that performs checkpointing using `pickle`
    to save and restore populations (and other aspects of the simulation state).
    """
    def __init__(self, generation_interval=100, time_interval_seconds=300, filename_prefix='neat-checkpoint-', epochs = None):
      self.epochs = epochs
      self.global_best_genome_fitness = None
      self.local_best_genome_fitness = None
      self.local_best_genome = None
      self.createPathIfNotExists(filename_prefix)
      super().__init__(generation_interval, time_interval_seconds, filename_prefix)
      print("~~~~~~~~~ AdvancedCheckpointer INITIALISED! ~~~~~~~~~")

    def createPathIfNotExists(self, filename):
      path = '/'.join(filename.split('/')[0:-1])
      isExist = os.path.exists(path)
      if not isExist:
        # Create a new directory because it does not exist 
        os.makedirs(path)
        print("Created checkpoint path:", path)

    def post_evaluate(self, config, population, species, population_best_genome):

        # reset the local-maxima every x generations
        if (self.current_generation > 0 and self.current_generation % self.generation_interval == 0):
            self.save_genome(config, population_best_genome, self.current_generation, 'local')
            self.local_best_genome_fitness = None 

        # store value if it is the local maxima
        if self.local_best_genome_fitness == None or population_best_genome.fitness > self.local_best_genome_fitness: 
            self.local_best_genome_fitness = population_best_genome.fitness
            self.local_best_genome = population_best_genome

        if self.global_best_genome_fitness == None or population_best_genome.fitness > self.global_best_genome_fitness: 
            self.global_best_genome_fitness = population_best_genome.fitness
            self.save_genome(config, population_best_genome, self.current_generation, 'global-maxima')

    def end_generation(self, config, population, species_set):
        checkpoint_due = False

        if self.time_interval_seconds is not None:
            dt = time.time() - self.last_time_checkpoint
            if dt >= self.time_interval_seconds:
                checkpoint_due = True

        if (checkpoint_due is False) and (self.generation_interval is not None):
            dg = self.current_generation - self.last_generation_checkpoint
            if dg >= self.generation_interval:
                checkpoint_due = True

        if (self.epochs != None) and ((self.current_generation + 1) == self.epochs): #current_generations is 0-based.
          checkpoint_due = True

        if checkpoint_due:
            self.save_checkpoint(config, population, species_set, self.current_generation)
            self.last_generation_checkpoint = self.current_generation
            self.last_time_checkpoint = time.time()

    def save_genome(self, config, best, generation, suffix):
        """ Save the current simulation state. """
        filename = '{0}{1}-{2}'.format(self.filename_prefix, generation, suffix)
        print("Saving best genome yet to {0}".format(filename))

        with gzip.open(filename, 'w', compresslevel=5) as f:
            data = (config, best, random.getstate())
            pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)

    @staticmethod
    def restore_genome(filename):
        """Restores a genome from a previous saved point."""
        with gzip.open(filename) as f:
            config, best, rndstate = pickle.load(f)
            random.setstate(rndstate)
            return (config, best)