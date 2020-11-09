class MultiAgentEnv:

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
