from skipbo.agent import Agent


class DqnAgent(Agent):

    def __init__(self):
        super().__init__()

    def action(self, observation, allowed_actions, reward, extra):
        print(extra["human_readable_allowed_actions"])
        print(extra["human_readable_game_state"])

    def done(self, observation, reward):
        pass
