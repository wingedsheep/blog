class StateTransition:

    def __init__(self, old_state, allowed_actions, action, reward, new_state, done):
        self.old_state = old_state
        self.allowed_actions = allowed_actions
        self.action = action
        self.reward = reward
        self.new_state = new_state
        self.done = done
