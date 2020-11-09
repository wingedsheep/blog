class DqnAgentParameters:

    def __init__(self, dictionary):
        self.starting_epsilon = dictionary["starting_epsilon"]
        self.epsilon_decay = dictionary["epsilon_decay"]
        self.minimum_epsilon = dictionary["minimum_epsilon"]
        self.epsilon_decay_factor_per_episode = dictionary["epsilon_decay_factor_per_episode"]
        self.replay_buffer_size = dictionary["replay_buffer_size"]
        self.target_network_replace_frequency_steps = dictionary["target_network_replace_frequency_steps"]
        self.training_batch_size = dictionary["training_batch_size"]
        self.training_start = dictionary["training_start"]
        self.discount_factor = dictionary["discount_factor"]
        self.backup_frequency_steps = dictionary["backup_frequency_steps"]
