class EmulatedBrain():
    """ 
      The EmulatedBrain class will efficiently load all of the lobes from the brain genome.
      NOTE: for lobe name 'test', the property 'lobe_test' will become available on this object.
    """
    def __init__(self, genome, genome_config, neural_network_type, lobes):
        self.genome = genome
        self.genome_config = genome_config
        self.neural_network_type = neural_network_type
        self.lobes = lobes
        #should set lobes based on config...

        self.init_lazy_loadable_lobes()


    """ create a lazy-loadable lobe cache (see in combination with __getattr_ func) """
    def init_lazy_loadable_lobes(self):
        for lobe in self.lobes:
            lobename = "_lobe_" + lobe
            setattr(self, lobename, None)


    """ 
      Create a lobe instance (of the specified neural_network_type) from the genome and associated config
      NOTE: will throw error if lobe is not found (intended)
    """
    def create_lobe_instance(self, lobe_name):
        err_msg_prefix = "Tried lazy loading '" +  lobe_name + "' but was unable to "

        lobe_config = self.genome_config.brain_lobes_config[lobe_name]
        if not bool(lobe_config):
          raise Exception(err_msg_prefix + "find the lobe config on the genome config.")

        lobe_data = self.genome.lobes[lobe_name]
        if not bool(lobe_data):
          raise Exception(err_msg_prefix + "find the lobe data on the genome instance.")

        lobe_instance = self.neural_network_type.create(lobe_data, lobe_config)
        if not bool(lobe_instance):
          raise Exception(err_msg_prefix + "create a lobe instance.")

        return lobe_instance


    """  Supporting lazy-loaded variables, lobes are not actually loaded into memory unless they are called """
    def __getattr__(self, name):
        lobe_prefix = "lobe_"

        if (name.startswith(lobe_prefix)):
          private_name = '_' + name
          cached_value = getattr(self, private_name, None)

          if cached_value == None:
            lobe_name = name[len(lobe_prefix):]
            lazy_loaded_value = self.create_lobe_instance(lobe_name)
            setattr(self, private_name, lazy_loaded_value)
            cached_value = lazy_loaded_value

          return cached_value

        else:
          return getattr(super, name)
