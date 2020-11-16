import random

import numpy as np


class QFunctions:

    @staticmethod
    def select_action_epsilon_greedy(q_values, epsilon, allowed_actions):
        random_value = random.uniform(0, 1)
        if random_value < epsilon:
            return random.choice(allowed_actions)
        else:
            adjusted_q_values = [q_values[index] for index in allowed_actions]
            selected_index_allowed_actions = np.argmax(adjusted_q_values)
            return allowed_actions[selected_index_allowed_actions]

    @staticmethod
    def select_best_action(q_values, allowed_actions):
        adjusted_q_values = [q_values[index] for index in allowed_actions]
        selected_index_allowed_actions = np.argmax(adjusted_q_values)
        return allowed_actions[selected_index_allowed_actions]

    @staticmethod
    def get_q_values(model, state):
        model_input = np.asarray(state)[np.newaxis, ...]
        return model.predict(model_input)[0]

    @staticmethod
    def get_multiple_q_values(model, states):
        return model.predict(states)
