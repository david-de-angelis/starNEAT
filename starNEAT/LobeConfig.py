from neat.activations import ActivationFunctionSet
from neat.aggregations import AggregationFunctionSet
from neat.config import ConfigParameter
from neat.genome import DefaultGenomeConfig

class LobeConfig(DefaultGenomeConfig):
  
  def __init__(self, lobe_name, params):
    self.lobe_name = lobe_name
    
    prefix = self.lobe_name + "_"
    lobe_params_metadata = [
        ConfigParameter(prefix + 'num_inputs', int),
        ConfigParameter(prefix + 'num_outputs', int),
        ConfigParameter(prefix + 'num_hidden', int),
        ConfigParameter(prefix + 'feed_forward', bool),
        ConfigParameter(prefix + 'compatibility_disjoint_coefficient', float),
        ConfigParameter(prefix + 'compatibility_weight_coefficient', float),
        ConfigParameter(prefix + 'conn_add_prob', float),
        ConfigParameter(prefix + 'conn_delete_prob', float),
        ConfigParameter(prefix + 'node_add_prob', float),
        ConfigParameter(prefix + 'node_delete_prob', float),
        ConfigParameter(prefix + 'single_structural_mutation', bool, 'false'),
        ConfigParameter(prefix + 'structural_mutation_surer', str, 'default'),
        ConfigParameter(prefix + 'initial_connection', str, 'unconnected'),
        ConfigParameter(prefix + 'lobe_inherits_fitness', bool, 'true'),
    ]

    for pm in lobe_params_metadata:
      setattr(self, pm.name[len(prefix):], pm.interpret(params))
    
    self.initialise_activation_and_aggregation_functions()
    self.inititalise_node_and_connection_gene_type(params)
    self.initialise_io_keys()
    
    self.verify_initial_connection_type_is_valid()
    self.verify_structural_mutation_surer_is_valid()

    self.node_indexer = None


  def initialise_activation_and_aggregation_functions(self):
    # Create full set of available activation & aggregation functions. (name difference [on aggregation] for backward compatibility)
    self.activation_defs = ActivationFunctionSet()
    self.aggregation_function_defs = AggregationFunctionSet()
    self.aggregation_defs = self.aggregation_function_defs


  def inititalise_node_and_connection_gene_type(self, params):
    self.other_params_metadata = []
    # Gather configuration data from the gene classes. #note: not lobe specific, but being individually applied to each lobe for compatibility
    self.node_gene_type = params['node_gene_type'] 
    self.other_params_metadata += self.node_gene_type.get_config_params()

    self.connection_gene_type = params['connection_gene_type']
    self.other_params_metadata += self.connection_gene_type.get_config_params()

    # Use the configuration data to interpret the supplied parameters.
    for pm in self.other_params_metadata:
        setattr(self, pm.name, pm.interpret(params))


  def initialise_io_keys(self):
    # By convention, input pins have negative keys, and the output pins have keys 0,1,...
    self.input_keys = [-i - 1 for i in range(self.num_inputs)]
    self.output_keys = [i for i in range(self.num_outputs)]


  def verify_initial_connection_type_is_valid(self):
    self.connection_fraction = None
    if 'partial' in self.initial_connection:
      raise NotImplementedError("See original genome.py for implementation details if required")
    assert self.initial_connection in self.allowed_connectivity


  def verify_structural_mutation_surer_is_valid(self):
    # pylint: disable=access-member-before-definition
    if self.structural_mutation_surer.lower() in ['1','yes','true','on']:
        self.structural_mutation_surer = 'true'
    elif self.structural_mutation_surer.lower() in ['0','no','false','off']:
        self.structural_mutation_surer = 'false'
    elif self.structural_mutation_surer.lower() == 'default':
        self.structural_mutation_surer = 'default'
    else:
        error_string = "Invalid structural_mutation_surer {!r}".format(self.structural_mutation_surer)
        raise RuntimeError(error_string)
