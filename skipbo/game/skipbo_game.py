import random

from skipbo.game.card import Card


def validate_stack(stack):
    count = 1
    for card in reversed(stack):
        if card.actual_value != count:
            return False
        count += 1
    return True


class SkipBoGame:
    """
    Play from:
      0   = Skip-Bo stack
      1-5 = Hand cards
      6-9 = Player stacks
    Play to:
      0-3 = Center stacks
      4-7 = Player stacks
    """

    def __init__(self):
        self.cards = []
        self.discarded = []
        self.player_skipbo_stacks = [[], []]
        self.player_hands = [[], []]
        self.player_stacks = [[[], [], [], []], [[], [], [], []]]
        self.center_stacks = [[], [], [], []]
        self.current_player = 0
        self.done = False

        # 0 is the skipbo card
        self.cards.extend([Card(0) for _ in range(18)])

        for i in range(1, 13):
            self.cards.extend([Card(i) for _ in range(18)])

        self.shuffle()

        for i in range(2):
            skipbo_stack = self.draw_cards(30)
            hand_cards = self.draw_cards(5)
            self.player_skipbo_stacks[i].extend(skipbo_stack)
            self.player_hands[i].extend(hand_cards)

    def draw_cards(self, nr):
        to_draw = min(nr, len(self.cards))
        drawn = self.cards[:nr]
        self.cards = self.cards[nr:]

        if len(self.cards) == 0:
            self.move_discarded_to_cards()
            remaining = nr - len(drawn)
            drawn.extend(self.cards[:remaining])
            self.cards = self.cards[remaining:]

        return drawn

    def move_discarded_to_cards(self):
        self.cards.extend(self.discarded)
        self.shuffle()
        self.discarded = []

    def shuffle(self):
        random.shuffle(self.cards)

    def get_available_actions(self, player):
        if self.current_player != player:
            return []
        else:
            available_actions = []
            for play_from in range(10):
                for play_to in range(8):
                    if self.is_playable(player, play_from, play_to):
                        available_actions.append((play_from, play_to))
            return available_actions

    def get_remaining_skipbo_cards(self, player):
        return len(self.player_skipbo_stacks[player])

    def is_playable(self, player, play_from, play_to):
        if self.current_player != player:
            return False
        elif play_from == 0:
            # Play from skipbo stack
            if play_to >= 4:
                # Can't play to player stacks
                return False
            else:
                # Play to center stacks
                card_to_play = self.__top_of_stack(self.player_skipbo_stacks[player])
                if card_to_play.card_type == 0:
                    # Can always play skipbo card
                    return True
                else:
                    top_of_stack = self.__top_of_stack(self.center_stacks[play_to])
                    if top_of_stack is None:
                        return card_to_play.card_type == 1
                    else:
                        # print(f"Card to play {card_to_play.card_type}. Top of stack {top_of_stack.actual_value}")
                        return card_to_play.card_type - 1 == top_of_stack.actual_value
        elif play_from < 6:
            # Play from hand
            index = play_from - 1
            card_to_play = self.player_hands[player][index]
            if card_to_play is None:
                return False
            elif play_to >= 4:
                return True
            elif play_to < 4:
                if card_to_play.card_type == 0:
                    # Can always play skipbo card
                    return True
                top_of_stack = self.__top_of_stack(self.center_stacks[play_to])
                if top_of_stack is None:
                    return card_to_play.card_type == 1
                else:
                    return card_to_play.card_type - 1 == top_of_stack.actual_value
        else:
            # Play from player stacks
            index = play_from - 6
            card_to_play = self.__top_of_stack(self.player_stacks[player][index])
            if card_to_play is None:
                return False
            elif play_to >= 4:
                # Can not play from player stacks to player stacks
                return False
            elif play_to < 4:
                if card_to_play.card_type == 0:
                    # Can always play skipbo card
                    return True
                top_of_stack = self.__top_of_stack(self.center_stacks[play_to])
                if top_of_stack is None:
                    return card_to_play.card_type == 1
                else:
                    return card_to_play.card_type - 1 == top_of_stack.actual_value

        return False

    def __top_of_stack(self, stack):
        if len(stack) == 0:
            return None
        else:
            return stack[0]

    def __hand_is_empty(self, player):
        return self.player_hands[player].count(None) == 5

    def play_card(self, play_from, play_to):
        card = self.__take_card(play_from)
        self.put_card(card, play_to)
        if play_to >= 4:
            could_refill_hand = self.switch_turn()
            if not could_refill_hand:
                return False
        elif self.__hand_is_empty(self.current_player):
            could_refill_hand = self.refill_hand(self.current_player)
            if not could_refill_hand:
                return False
        return True

    def refill_hand(self, player):
        nr_of_new_cards = self.player_hands[player].count(None)
        new_cards = self.draw_cards(nr_of_new_cards)

        # Not enough cards remaining. Game is finished.
        if len(new_cards) < nr_of_new_cards:
            return False

        for index, card in enumerate(self.player_hands[player]):
            if card is None:
                self.player_hands[player][index] = new_cards.pop()

        return True

    def put_card(self, card, play_to):
        if play_to < 4:
            # play to center stacks
            played_card = card
            if card.card_type == 0:
                top_of_stack = self.__top_of_stack(self.center_stacks[play_to])
                if top_of_stack is None:
                    played_card.actual_value = 1
                else:
                    played_card.actual_value = top_of_stack.actual_value + 1

            if played_card.actual_value == 12:
                self.center_stacks[play_to].insert(0, played_card)
                if len(self.center_stacks[play_to]) < 12:
                    print(f"Discarded: {list(map(lambda x: self.__visualize_card(x), self.center_stacks[play_to]))}")
                self.discarded.extend(self.center_stacks[play_to])
                self.center_stacks[play_to] = []
            else:
                self.center_stacks[play_to].insert(0, played_card)

            if not validate_stack(self.center_stacks[play_to]):
                print(f"Invalid stack: {list(map(lambda x: self.__visualize_card(x), self.center_stacks[play_to]))}")

        else:
            # play to player stacks
            index = play_to - 4
            self.player_stacks[self.current_player][index].insert(0, card)

    def switch_turn(self):
        self.current_player = 1 if self.current_player == 0 else 0
        return self.refill_hand(self.current_player)

    def __take_card(self, play_from):
        if play_from == 0:
            # play from skipbo stack
            return self.player_skipbo_stacks[self.current_player].pop(0)
        elif 1 <= play_from <= 5:
            # play from hand
            index = play_from - 1
            card = self.player_hands[self.current_player][index]
            self.player_hands[self.current_player][index] = None
            return card
        elif 6 <= play_from <= 9:
            # play from player stacks
            index = play_from - 6
            return self.player_stacks[self.current_player][index].pop(0)

    def __visualize_position(self, player, position):
        if player is None:
            # get from center stacks
            card = None
            if len(self.center_stacks[position]) > 0:
                card = self.center_stacks[position][0]
            return self.__visualize_card(card)
        else:
            if position == 0:
                # get from skipbo stack
                card = None
                if len(self.player_skipbo_stacks[player]) > 0:
                    card = self.player_skipbo_stacks[player][0]
                return self.__visualize_card(card)
            elif 1 <= position <= 5:
                # get from hand
                index = position - 1
                card = self.player_hands[player][index]
                return self.__visualize_card(card)
            elif 6 <= position <= 9:
                # get from player stacks
                index = position - 6
                card = None
                if len(self.player_stacks[player][index]) > 0:
                    card = self.player_stacks[player][index][0]
                return self.__visualize_card(card)

    def __visualize_card(self, card):
        if card is None:
            return 'xx'
        elif card.card_type == 0:
            return 'sb'
        else:
            return format(card.card_type, '02d')

    def visualize(self):
        print(
            f"{self.__visualize_position(0, 0)} [{format(len(self.player_skipbo_stacks[0]), '2d')}]     {self.__visualize_position(0, 1)} {self.__visualize_position(0, 2)} {self.__visualize_position(0, 3)} {self.__visualize_position(0, 4)} {self.__visualize_position(0, 5)}")
        print(f"                               {'<-- turn' if self.current_player == 0 else ''}")
        print(
            f"             {self.__visualize_position(0, 6)} {self.__visualize_position(0, 7)} {self.__visualize_position(0, 8)} {self.__visualize_position(0, 9)}")
        print("------------------------------")
        print("")
        print(
            f"             {self.__visualize_position(None, 0)} {self.__visualize_position(None, 1)} {self.__visualize_position(None, 2)} {self.__visualize_position(None, 3)}")
        print("")
        print("------------------------------")
        print(
            f"             {self.__visualize_position(1, 6)} {self.__visualize_position(1, 7)} {self.__visualize_position(1, 8)} {self.__visualize_position(1, 9)}")
        print(f"                               {'<-- turn' if self.current_player == 1 else ''}")
        print(
            f"{self.__visualize_position(1, 0)} [{format(len(self.player_skipbo_stacks[1]), '2d')}]     {self.__visualize_position(1, 1)} {self.__visualize_position(1, 2)} {self.__visualize_position(1, 3)} {self.__visualize_position(1, 4)} {self.__visualize_position(1, 5)}")
