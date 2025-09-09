from typing import List
from .card import Card

class Zone:
    """
    Represents a generic area in the game that can hold cards, such as
    the Hand, Graveyard, or Battlefield.
    """
    def __init__(self, name: str):
        """
        Initializes a Zone instance.

        Args:
            name (str): The name of the zone (e.g., "Hand").
        """
        self.name = name
        self.cards: List[Card] = []

    def add(self, card: Card):
        """Adds a card to this zone."""
        if not isinstance(card, Card):
            raise TypeError("Only Card objects can be added to a Zone.")
        self.cards.append(card)

    def remove(self, card: Card):
        """Removes a card from this zone."""
        if card in self.cards:
            self.cards.remove(card)
        else:
            raise ValueError(f"Card {card} not found in zone {self.name}.")

    def get_cards(self) -> List[Card]:
        """Returns the list of cards in this zone."""
        return self.cards

    def __len__(self) -> int:
        """Returns the number of cards in this zone."""
        return len(self.cards)

    def __repr__(self) -> str:
        """Provides a developer-friendly string representation of the zone."""
        return f"Zone(Name: '{self.name}', Cards: {len(self)})"