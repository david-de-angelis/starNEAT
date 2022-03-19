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
        #Note: DefaultNodeGene & DefaultConnectionGene are common between all lobes (functionality has not been implemented to support different Node/Conenction Genes per lobe)
        param_dict['node_gene_type'] = DefaultNodeGene
        param_dict['connection_gene_type'] = DefaultConnectionGene
        return BrainGenomeConfig(param_dict)


    def __init__(self, key):
        super().__init__(key)

        self.connections = None # these are no longer applicable, as the brain is now split into seperate lobes (NNs)
        self.nodes = None # '' ^


    def configure_new(self, config):
      """Configure a new genome based on the given configuration."""
      #should this be here?
      self.lobes = {}
      for lobe_name, lobe_config in config.brain_lobes_config.items():
        lobe = self.create_lobe(lobe_name)
        self.lobes[lobe_name] = lobe

        lobe.configure_new(lobe_config)

    # def configure_crossover(self, genome1, genome2, config):
    #     """ Configure a new genome by crossover from two parent genomes. """
        

    # def mutate(self, config):
    #     """ Mutates this genome. """


    # def mutate_add_node(self, config):
    #     """ does something """


    # def add_connection(self, config, input_key, output_key, weight, enabled):
    #     """ does something """


    # def mutate_add_connection(self, config):
    #     """
    #     Attempt to add a new connection, the only restriction being that the output
    #     node cannot be one of the network input pins.
    #     """


    # def mutate_delete_node(self, config):
    #     """ does something """


    # def mutate_delete_connection(self):
    #     """ does something """


    # def distance(self, other, config):
    #     """
    #     Returns the genetic distance between this genome and the other. This distance value
    #     is used to compute genome compatibility for speciation.
    #     """


    # def size(self):
    #     """
    #     Returns genome 'complexity', taken to be
    #     (number of nodes, number of enabled connections)
    #     """
    #     num_enabled_connections = sum([1 for cg in self.connections.values() if cg.enabled])
    #     return len(self.nodes), num_enabled_connections


    # def __str__(self):
    #     """ does something """


    @staticmethod
    def create_lobe(name, connections = {}, nodes = {}):
        return Lobe(name, connections, nodes)


    # @staticmethod
    # def create_node(config, node_id):
    #     """ does something """


    # @staticmethod
    # def create_connection(config, input_id, output_id):
    #     """ does something """


    # def connect_fs_neat_nohidden(self, config):
    #     """
    #     Randomly connect one input to all output nodes
    #     (FS-NEAT without connections to hidden, if any).
    #     Originally connect_fs_neat.
    #     """


    # def connect_fs_neat_hidden(self, config):
    #     """
    #     Randomly connect one input to all hidden and output nodes
    #     (FS-NEAT with connections to hidden, if any).
    #     """


    # def compute_full_connections(self, config, direct):
    #     """
    #     Compute connections for a fully-connected feed-forward genome--each
    #     input connected to all hidden nodes
    #     (and output nodes if ``direct`` is set or there are no hidden nodes),
    #     each hidden node connected to all output nodes.
    #     (Recurrent genomes will also include node self-connections.)
    #     """


    # def connect_full_nodirect(self, config):
    #     """
    #     Create a fully-connected genome
    #     (except without direct input-output unless no hidden nodes).
    #     """


    # def connect_full_direct(self, config):
    #     """ Create a fully-connected genome, including direct input-output connections. """


    # def connect_partial_nodirect(self, config):
    #     """
    #     Create a partially-connected genome,
    #     with (unless no hidden nodes) no direct input-output connections."""


    # def connect_partial_direct(self, config):
    #     """
    #     Create a partially-connected genome,
    #     including (possibly) direct input-output connections.
    #     """
