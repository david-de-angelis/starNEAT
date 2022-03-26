from decimal import InvalidOperation
from neat import DefaultGenome
from neat.genes import DefaultConnectionGene, DefaultNodeGene

from starNEAT.BrainGenomeConfig import BrainGenomeConfig
from starNEAT.Lobe import Lobe

class BrainGenome(DefaultGenome):

    """
    A genome for star-neat neural networks.

    Terminology
        pin: Point at which the network is conceptually connected to the external world;
             pins are either input or output.
        node: Analog of a physical neuron.
        connection: Connection between a pin/node output and a node's input, or between a node's
             output and a pin/node input.
        key: Identifier for an object, unique within the set of similar objects.

    Design assumptions and conventions.
        1. Each output pin is connected only to the output of its own unique
           neuron by an implicit connection with weight one. This connection
           is permanently enabled.
        2. The output pin's key is always the same as the key for its
           associated neuron.
        3. Output neurons can be modified but not deleted.
        4. The input values are applied to the input pins unmodified.
    """
    @classmethod
    def parse_config(cls, param_dict):
        #Note: DefaultNodeGene & DefaultConnectionGene are common between all lobes 
        # (functionality has not been implemented to support different Node/Conenction Genes per lobe)
        param_dict['node_gene_type'] = DefaultNodeGene
        param_dict['connection_gene_type'] = DefaultConnectionGene
        return BrainGenomeConfig(param_dict)


    def __init__(self, key):
        super().__init__(key)

        self.lobes = {}

        # these are no longer applicable, as the brain is now split into seperate lobes (NNs)
        del self.connections
        del self.nodes


    def configure_new(self, config):
        """Configure a new genome based on the given configuration."""
        
        self.initialise_empty_lobes(config)

        for lobe in self.lobes.values():
            lobe_config = config.brain_lobes_config[lobe.name]
            lobe.configure_new(lobe_config)


    def initialise_empty_lobes(self, config):
        if self.lobes != {}:
            raise Exception("Cannot overwrite an existing brain")

        for lobe_name in config.brain_lobes_config.keys():
            lobe = self.create_lobe(lobe_name)
            self.lobes[lobe_name] = lobe

    def create_lobe(self, name, connections = None, nodes = None):
        return Lobe(name, connections, nodes)


    def configure_crossover(self, parent_brain_1, parent_brain_2, config):
        """ Configure a new genome by crossover from two parent genomes. """
        self.initialise_empty_lobes(config)
        
        assert len(self.lobes) == len(parent_brain_1.lobes)
        assert len(self.lobes) == len(parent_brain_2.lobes)

        for lobe in self.lobes.values():
            pb1_lobe = parent_brain_1.lobes[lobe.name]
            pb2_lobe = parent_brain_2.lobes[lobe.name]

            if (pb1_lobe == None or pb2_lobe == None):
                raise Exception("Lobe", lobe.name, "not found on one of the parents during cross_over")

            lobe_config = config.brain_lobes_config[lobe.name]
            if lobe_config.lobe_inherits_fitness:
                if (pb1_lobe.fitness == None):
                    pb1_lobe.fitness = parent_brain_1.fitness

                if (pb2_lobe.fitness == None):
                    pb2_lobe.fitness = parent_brain_2.fitness

            lobe.configure_crossover(pb1_lobe, pb2_lobe, lobe_config)


    def mutate(self, config):
        """ Mutates this genome. """
        for lobe in self.lobes.values():
            lobe_config = config.brain_lobes_config[lobe.name]
            lobe.mutate(lobe_config)


    def distance(self, other, config):
        """
        Returns the genetic distance between this genome and the other. This distance value
        is used to compute genome compatibility for speciation.
        """
        distance = 0.0
        for lobe in self.lobes.values():
            other_lobe = other.lobes[lobe.name]
            lobe_config = config.brain_lobes_config[lobe.name]

            distance += lobe.distance(other_lobe, lobe_config)
            
        return distance / float(len(self.lobes))


    # I believe this is only for reporting purposes... if not, this may have to be re-worked
    def size(self):
        """
        Returns genome 'complexity', taken to be
        (number of nodes, number of enabled connections)
        """
        num_enabled_connections = 0
        num_nodes = 0
        for lobe in self.lobes.values():
            num_enabled_connections += sum([1 for cg in lobe.connections.values() if cg.enabled])
            num_nodes += len(lobe.nodes)
        return num_nodes, num_enabled_connections


    def __str__(self):
        """ Results a string representation of the brain object """
        result = [ 
            "Brain:",
            "Key: {0}\nFitness: {1}\n".format(self.key, self.fitness),
        ]

        for lobe in self.lobes.values():
            result.append("Lobe: " + lobe.name)
            result.append(str(lobe))
        
        return '\n'.join(result)


    @staticmethod
    def create_connection(config, input_id, output_id): raise InvalidOperation("A connection cannot be created at the brain level")
    def add_connection(self, config, input_key, output_key, weight, enabled): raise InvalidOperation("A connection cannot be created at the brain level")
    def mutate_add_connection(self, config):    raise InvalidOperation("A connection cannot be created at the brain level")
    def mutate_delete_connection(self):         raise InvalidOperation("A connection cannot be deleted at the brain level")


    @staticmethod
    def create_node(config, node_id):           raise InvalidOperation("A node cannot be created at the brain level")
    def mutate_add_node(self, config):          raise InvalidOperation("A node cannot be created at the brain level")
    def mutate_delete_node(self, config):       raise InvalidOperation("A node cannot be deleted at the brain level")


    def compute_full_connections(self, config, direct):     raise NotImplementedError()
    def connect_full_nodirect(self, config):        raise NotImplementedError()
    def connect_full_direct(self, config):          raise NotImplementedError()


    def connect_partial_nodirect(self, config):     raise NotImplementedError()
    def connect_partial_direct(self, config):       raise NotImplementedError()


    def connect_fs_neat_nohidden(self, config):     raise NotImplementedError()
    def connect_fs_neat_hidden(self, config):       raise NotImplementedError()
