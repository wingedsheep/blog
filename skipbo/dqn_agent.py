import numpy as np
from tensorflow.python.keras import Sequential

from skipbo.agent import Agent
from skipbo.dqn_agent_parameters import DqnAgentParameters
from skipbo.model import ModelManager
from skipbo.q_functions import QFunctions
from skipbo.replay_buffer import ReplayBuffer
from skipbo.state_transition import StateTransition


class DqnAgent(Agent):

    def __init__(self, name: str, model: Sequential, parameters: DqnAgentParameters):
        super().__init__()
        self.name = name
        self.model = model
        self.target_model = ModelManager.copy_model(model)
        self.current_epsilon = parameters.starting_epsilon
        self.epsilon_decay = parameters.epsilon_decay
        self.minimum_epsilon = parameters.minimum_epsilon
        self.epsilon_decay_factor_per_episode = parameters.epsilon_decay_factor_per_episode
        self.target_network_replace_frequency_steps = parameters.target_network_replace_frequency_steps
        self.training_start = parameters.training_start
        self.training_batch_size = parameters.training_batch_size
        self.discount_factor = parameters.discount_factor
        self.backup_frequency_steps = parameters.backup_frequency_steps
        self.previous_observation = None
        self.previous_action = None
        self.replay_buffer = ReplayBuffer(parameters.replay_buffer_size)
        self.step_count = 0

    def action(self, observation, allowed_actions, reward, extra):
        if self.previous_observation is not None:
            if reward > 0:
                print(f"{self.name} got a reward of {reward}.")
            self.process_state_transition(observation, reward, False)

        q_values = QFunctions.get_q_values(self.model, observation)
        action = QFunctions.select_action_epsilon_greedy(q_values, self.current_epsilon, allowed_actions)
        self.previous_observation = observation
        self.previous_action = action
        self.step_count += 1
        return action

    def done(self, final_observation, reward):
        self.process_state_transition(self.previous_observation, reward, True)
        self.current_epsilon *= self.epsilon_decay_factor_per_episode
        self.current_epsilon = max(self.minimum_epsilon, self.current_epsilon)

    def reset_after_episode(self):
        self.previous_observation = None
        self.previous_action = None

    def process_state_transition(self, observation, reward, done):
        state_transition = StateTransition(
            self.previous_observation,
            self.previous_action,
            reward,
            observation,
            done)
        self.replay_buffer.add(state_transition)

        if self.step_count % self.target_network_replace_frequency_steps == 0:
            print(self.name, "Updating target model")
            self.target_model = ModelManager.copy_model(self.model)

        if self.step_count != 0 and self.step_count % self.backup_frequency_steps == 0:
            backup_file = f"models/{self.name}/{self.step_count}.h5"
            print(f"Backing up model to {backup_file}")
            self.model.save(backup_file)

        if self.replay_buffer.length() >= self.training_start:
            batch = self.replay_buffer.get_batch(batch_size=self.training_batch_size)
            targets = self.calculate_target_values(batch)
            states = np.array([state_transition.old_state for state_transition in batch])
            self.model.fit(states, targets, epochs=1, batch_size=len(targets), verbose=0)

    def calculate_target_values(self, state_transitions):
        states = []
        new_states = []
        for transition in state_transitions:
            states.append(transition.old_state)
            new_states.append(transition.new_state)

        new_states = np.array(new_states)

        q_values_new_state = QFunctions.get_multiple_q_values(self.model, new_states)
        q_values_new_state_target_model = QFunctions.get_multiple_q_values(self.target_model, new_states)

        targets = []
        for index, state_transition in enumerate(state_transitions):
            # TODO Pick best action only from available actions
            best_action = QFunctions.select_best_action(q_values_new_state[index])
            best_action_next_state_q_value = q_values_new_state_target_model[index][best_action]

            if state_transition.done:
                target_value = state_transition.reward
            else:
                target_value = state_transition.reward + self.discount_factor * best_action_next_state_q_value

            target_vector = [0] * 80    # TODO replace by non-hardcoded
            target_vector[state_transition.action] = target_value
            targets.append(target_vector)

        return np.array(targets)
