from skipbo.dqn_agent import DqnAgent
from skipbo.dqn_agent_parameters import DqnAgentParameters
from skipbo.model import ModelManager
from skipbo.skipbo_env import SkipboEnv

learning_rate = 0.001
regularization_factor = 0.001

model1 = ModelManager.create_model(250, 80, learning_rate, regularization_factor)
parameters1 = DqnAgentParameters({
    "starting_epsilon": 1.0,
    "epsilon_decay": 0.995,
    "minimum_epsilon": 0.01,
    "epsilon_decay_factor_per_episode": 0.995,
    "replay_buffer_size": 250000,
    "target_network_replace_frequency_steps": 1000,
    "training_batch_size": 128,
    "training_start": 256,
    "discount_factor": 0.99
})
agent1 = DqnAgent("Emily", model1, parameters1)

model2 = ModelManager.create_model(250, 80, learning_rate, regularization_factor)
parameters2 = DqnAgentParameters({
    "starting_epsilon": 1.0,
    "epsilon_decay": 0.995,
    "minimum_epsilon": 0.01,
    "epsilon_decay_factor_per_episode": 0.995,
    "replay_buffer_size": 250000,
    "target_network_replace_frequency_steps": 1000,
    "training_batch_size": 128,
    "training_start": 256,
    "discount_factor": 0.99
})
agent2 = DqnAgent("James", model2, parameters2)

environment = SkipboEnv()
for i in range(1000):
    environment.play([agent1, agent2], [])
