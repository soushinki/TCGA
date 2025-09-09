import random
from typing import List
from .zone import Zone
from .card import Card

class Deck(Zone):
    """
    Represents a player's deck of cards. It is a specialized Zone
    with added functionality for shuffling and drawing.
    """
    def __init__(self, cards: List[Card] = None):
        """
        Initializes a Deck instance.

        Args:
            cards (List[Card], optional): A list of cards to populate the deck.
        """
        super().__init__("Deck")
        if cards:
            self.cards = list(cards)

    def shuffle(self):
        """Shuffles the cards in the deck randomly."""
        random.shuffle(self.cards)

    def draw(self) -> Card:
        """
        Draws the top card from the deck.

        Returns:
            Card: The card from the top of the deck, or None if the deck is empty.
        """
        if len(self.cards) > 0:
            return self.cards.pop(0) # Draw from the "top" (index 0)
        return None

    def __repr__(self) -> str:
        """Provides a developer-friendly string representation of the deck."""
        return f"Deck(Cards: {len(self)})"