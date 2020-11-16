from skipbo.game.skipbo_game import SkipBoGame
from skipbo.multi_agent_env import MultiAgentEnv


class SkipboEnv(MultiAgentEnv):

    def __init__(self):
        super().__init__()
        self.game = None
        self.done = False

    def reset(self):
        """
        Creates a new Skip-Bo game for two players and returns the observed states and available actions per player
        """
        self.game = SkipBoGame()
        self.done = False
        observation = self.__get_observation(self.game, self.game.current_player)
        available_actions = self.__get_available_actions(self.game, self.game.current_player)
        return observation, available_actions

    def play(self, agents, options):
        observation, available_actions = self.reset()
        accumulated_rewards = [0, 0]

        while not self.done:
            player = self.game.current_player
            agent = agents[player]
            action = agent.action(observation, available_actions, accumulated_rewards[player], None)

            # Reset accumulated rewards for current player
            accumulated_rewards[player] = 0

            game_action = self.convert_action_from_rl_notation(action)

            # self.game.visualize()
            # print(f"Available actions {list(map(lambda x: self.convert_action_from_rl_notation(x), available_actions))}.")
            # print(f"Action taken {game_action}, by player {self.game.current_player}")
            # print(f"Cards in game: {self.game.cards_in_game()}")

            prev_remaining_skipbo_cards = [self.game.get_remaining_skipbo_cards(0),
                                           self.game.get_remaining_skipbo_cards(1)]
            could_draw_cards = self.game.play_card(game_action[0], game_action[1])
            remaining_skipbo_cards = [self.game.get_remaining_skipbo_cards(0), self.game.get_remaining_skipbo_cards(1)]

            # observation for the new player
            observation = self.__get_observation(self.game, self.game.current_player)

            # small penalty for finishing the turn by putting a card on player stacks
            if game_action[1] >= 4:
                accumulated_rewards[player] -= 0.05

            # points for playing skipbo cards
            accumulated_rewards[0] += prev_remaining_skipbo_cards[0] - remaining_skipbo_cards[0]
            accumulated_rewards[1] += prev_remaining_skipbo_cards[1] - remaining_skipbo_cards[1]

            available_actions = []
            if remaining_skipbo_cards[0] == 0:
                accumulated_rewards[0] += 10
                accumulated_rewards[1] -= 10
                self.done = True
                agents[0].done(observation, accumulated_rewards[0])
                agents[1].done(observation, accumulated_rewards[1])
                print(f"Game {options['episode']} finished. {agents[0].name}: {self.game.get_remaining_skipbo_cards(0)}, {agents[1].name}: {self.game.get_remaining_skipbo_cards(1)}")
            elif remaining_skipbo_cards[1] == 0:
                accumulated_rewards[0] -= 10
                accumulated_rewards[1] += 10
                self.done = True
                agents[0].done(observation, accumulated_rewards[0])
                agents[1].done(observation, accumulated_rewards[1])
                print(f"Game {options['episode']} finished. {agents[0].name}: {self.game.get_remaining_skipbo_cards(0)}, {agents[1].name}: {self.game.get_remaining_skipbo_cards(1)}")
            elif could_draw_cards:
                # Available actions for the new player
                available_actions = self.__get_available_actions(self.game, self.game.current_player)
            else:
                # Game finished because there are no more drawable cards
                self.done = True
                accumulated_rewards[0] -= 10
                accumulated_rewards[1] -= 10
                agents[0].done(observation, accumulated_rewards[0])
                agents[1].done(observation, accumulated_rewards[1])
                print(f"Game {options['episode']} finished. {agents[0].name}: {self.game.get_remaining_skipbo_cards(0)}, {agents[1].name}: {self.game.get_remaining_skipbo_cards(1)}")

    def __get_available_actions(self, game, player):
        return [self.convert_action_to_rl_notation(x) for x in game.get_available_actions(player)]

    def convert_action_to_rl_notation(self, game_action):
        return 8 * game_action[0] + game_action[1]

    def convert_action_from_rl_notation(self, rl_action):
        play_from = int(rl_action / 8)
        play_to = rl_action % 8
        return play_from, play_to

    def __get_observation(self, game, player):
        """
        Return an observation. The observation is an array containing the following information per index:
        0: Is it the given players' turn (0 = opponents' turn, 1 = current players' turn)
        1: Remaining cards on the skipbo stack for given player
        2: Remaining cards on the skipbo stack for opponent
        3-21: Positions containing a skipbo card
        22-40: Positions containing a 1 card
        41-59: Positions containing a 2 card
        60-78: Positions containing a 3 card
        79-97: Positions containing a 4 card
        98-116: Positions containing a 5 card
        117-135: Positions containing a 6 card
        136-154: Positions containing a 7 card
        155-173: Positions containing a 8 card
        174-192: Positions containing a 9 card
        192-211: Positions containing a 10 card
        212-230: Positions containing a 11 card
        231-249: Positions containing a 12 card
        250: Remaining playable cards
        """
        other_player = 0 if player == 1 else 1

        observation = []
        observation.append(1 if game.current_player == player else 0)
        observation.append(len(game.player_skipbo_stacks[player]) / 30.0)  # Normalized player skipbo cards
        observation.append(len(game.player_skipbo_stacks[other_player]) / 30.0)  # Normalized other player skipbo cards
        for i in range(13):
            observation.extend(self.__get_array_of_positions_containing_card(player, i, game))
        observation.append(len(self.game.cards) + len(self.game.discarded) / 92.0)  # Normalized number of cards left

        return observation

    def __get_top_card_from_stack(self, stack):
        if len(stack) == 0:
            return None
        else:
            return stack[0]

    def __card_value(self, card, center):
        if card is None:
            return -1
        else:
            if center:
                return card.actual_value
            else:
                return card.card_type

    def __get_array_of_positions_containing_card(self, current_player, card, game):
        """
        Return an array containing all the positions (from the given players' point of view) that contain the given card.
        """
        other_player = 0 if game.current_player == 1 else 1
        result = []

        result.append(1 if self.__card_value(self.__get_top_card_from_stack(game.player_skipbo_stacks[current_player]), False) == card else 0)

        result.append(1 if self.__card_value(game.player_hands[current_player][0], False) == card else 0)
        result.append(1 if self.__card_value(game.player_hands[current_player][1], False) == card else 0)
        result.append(1 if self.__card_value(game.player_hands[current_player][2], False) == card else 0)
        result.append(1 if self.__card_value(game.player_hands[current_player][3], False) == card else 0)
        result.append(1 if self.__card_value(game.player_hands[current_player][4], False) == card else 0)

        result.append(1 if self.__card_value(self.__get_top_card_from_stack(game.player_stacks[current_player][0]), False) == card else 0)
        result.append(1 if self.__card_value(self.__get_top_card_from_stack(game.player_stacks[current_player][1]), False) == card else 0)
        result.append(1 if self.__card_value(self.__get_top_card_from_stack(game.player_stacks[current_player][2]), False) == card else 0)
        result.append(1 if self.__card_value(self.__get_top_card_from_stack(game.player_stacks[current_player][3]), False) == card else 0)

        result.append(1 if self.__card_value(self.__get_top_card_from_stack(game.player_stacks[current_player][0][1:]), False) == card else 0)
        result.append(1 if self.__card_value(self.__get_top_card_from_stack(game.player_stacks[current_player][1][1:]), False) == card else 0)
        result.append(1 if self.__card_value(self.__get_top_card_from_stack(game.player_stacks[current_player][2][1:]), False) == card else 0)
        result.append(1 if self.__card_value(self.__get_top_card_from_stack(game.player_stacks[current_player][3][1:]), False) == card else 0)

        # result.append(1 if self.__card_value(self.__get_top_card_from_stack(game.player_stacks[current_player][0][2:]), False) == card else 0)
        # result.append(1 if self.__card_value(self.__get_top_card_from_stack(game.player_stacks[current_player][1][2:]), False) == card else 0)
        # result.append(1 if self.__card_value(self.__get_top_card_from_stack(game.player_stacks[current_player][2][2:]), False) == card else 0)
        # result.append(1 if self.__card_value(self.__get_top_card_from_stack(game.player_stacks[current_player][3][2:]), False) == card else 0)

        result.append(1 if self.__card_value(self.__get_top_card_from_stack(game.center_stacks[0]), True) == card else 0)
        result.append(1 if self.__card_value(self.__get_top_card_from_stack(game.center_stacks[1]), True) == card else 0)
        result.append(1 if self.__card_value(self.__get_top_card_from_stack(game.center_stacks[2]), True) == card else 0)
        result.append(1 if self.__card_value(self.__get_top_card_from_stack(game.center_stacks[3]), True) == card else 0)

        result.append(1 if self.__card_value(self.__get_top_card_from_stack(game.player_skipbo_stacks[other_player]), False) == card else 0)

        result.append(1 if self.__card_value(self.__get_top_card_from_stack(game.player_stacks[other_player][0]), False) == card else 0)
        result.append(1 if self.__card_value(self.__get_top_card_from_stack(game.player_stacks[other_player][1]), False) == card else 0)
        result.append(1 if self.__card_value(self.__get_top_card_from_stack(game.player_stacks[other_player][2]), False) == card else 0)
        result.append(1 if self.__card_value(self.__get_top_card_from_stack(game.player_stacks[other_player][3]), False) == card else 0)

        result.append(1 if self.__card_value(self.__get_top_card_from_stack(game.player_stacks[other_player][0][1:]), False) == card else 0)
        result.append(1 if self.__card_value(self.__get_top_card_from_stack(game.player_stacks[other_player][1][1:]), False) == card else 0)
        result.append(1 if self.__card_value(self.__get_top_card_from_stack(game.player_stacks[other_player][2][1:]), False) == card else 0)
        result.append(1 if self.__card_value(self.__get_top_card_from_stack(game.player_stacks[other_player][3][1:]), False) == card else 0)

        # result.append(1 if self.__card_value(self.__get_top_card_from_stack(game.player_stacks[other_player][0][2:]), False) == card else 0)
        # result.append(1 if self.__card_value(self.__get_top_card_from_stack(game.player_stacks[other_player][1][2:]), False) == card else 0)
        # result.append(1 if self.__card_value(self.__get_top_card_from_stack(game.player_stacks[other_player][2][2:]), False) == card else 0)
        # result.append(1 if self.__card_value(self.__get_top_card_from_stack(game.player_stacks[other_player][3][2:]), False) == card else 0)

        return result
