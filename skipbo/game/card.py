class Card:
    def __init__(self, card_type):
        """
        card_type 0 is a skipbo card
        card_type 1-12 are the normal value cards
        actual value indicates the value a skipbo card takes on after it is played
        """
        self.card_type = card_type
        self.actual_value = card_type if card_type > 0 else 0
