import os

import numpy as np
from tensorflow.python.keras import Sequential

from skipbo.agent import Agent
from skipbo.dqn_agent_parameters import DqnAgentParameters
from skipbo.model import ModelManager
from skipbo.q_functions import QFunctions
from skipbo.replay_buffer import ReplayBuffer
from skipbo.state_transition import StateTransition


class TrainedDqnAgent(Agent):

    def __init__(self, name: str, model: Sequential):
        super().__init__()
        self.name = name
        self.model = model
        self.episode_reward = 0

    def action(self, observation, allowed_actions, reward, extra):
        if reward != 0:
            self.episode_reward += reward

        q_values = QFunctions.get_q_values(self.model, observation)
        action = QFunctions.select_action_epsilon_greedy(q_values, 0, allowed_actions)
        return action

    def done(self, final_observation, reward):
        if reward != 0:
            self.episode_reward += reward

        print(f"{self.name} got a total reward of {self.episode_reward}.")
        self.reset_after_episode()

    def reset_after_episode(self):
        self.episode_reward = 0
