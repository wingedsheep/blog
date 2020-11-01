import random


class Env:

    def __init__(self):
        """
        Initialize the environment
        """

    def play(self, agents, options):
        """
        Play a single game with a number of agents.

        When an agent has to decide on an action, the environment calls the
        agent.action(observation, allowed_actions, previous_reward) method.

        When the game is over for an agent the environment calls
        agent.done(reward).

        Options contains game specific settings.
        """


class Agent:

    def __init__(self):
        """
        Initialize the agent
        """

    def action(self, observation, allowed_actions, previous_reward):
        """
        This method is called when an agent has to decide an action. The
        chosen action is returned.
        """

    def done(self, previous_reward):
        """
      This method is called when a game is over for this agent. It
      includes the final reward for this agent.
      """


class RockPaperScissorsEnv(Env):
    allowed_actions = [1, 2, 3]

    action_map = {
        1: "Rock",
        2: "Paper",
        3: "Scissors"
    }

    def __init__(self):
        super().__init__()

    def play(self, agents, options=None):
        winner = None
        while winner is None:
            action_0 = agents[0].action([], self.allowed_actions, 0)
            print(f"agent 0 picked action {self.action_map[action_0]}")
            action_1 = agents[1].action([], self.allowed_actions, 0)
            print(f"agent 1 picked action {self.action_map[action_1]}")
            winner = RockPaperScissorsEnv.determine_winner(action_0, action_1)
            if winner == 0:
                print(f"agent 0 won the game!")
                agents[0].done(1)
                agents[1].done(-1)
            elif winner == 1:
                print(f"agent 1 won the game!")
                agents[0].done(-1)
                agents[1].done(1)

    @staticmethod
    def determine_winner(action_0, action_1):
        if action_0 == action_1:
            return None
        if action_0 == 1:
            if action_1 == 2:
                return 1
            elif action_1 == 3:
                return 0
        elif action_0 == 2:
            if action_1 == 1:
                return 0
            elif action_1 == 3:
                return 1
        elif action_0 == 3:
            if action_1 == 1:
                return 1
            elif action_1 == 2:
                return 0


class RockPaperScissorsAgent(Agent):

    def __init__(self):
        super().__init__()

    def action(self, observation, allowed_actions, previous_reward):
        return random.choice(allowed_actions)

    def done(self, previous_reward):
        pass


agent0 = RockPaperScissorsAgent()
agent1 = RockPaperScissorsAgent()
environment = RockPaperScissorsEnv()
environment.play([agent0, agent1])
