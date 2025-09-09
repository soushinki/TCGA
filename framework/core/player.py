from typing import List, Dict
from .card import Card
from .deck import Deck
from .zone import Zone

class Player:
    """

    Represents a player in the game. Manages the player's life total,
    and all zones associated with the player (Hand, Deck, Graveyard).
    """
    def __init__(self, name: str, life: int = 20):
        """
        Initializes a Player instance.

        Args:
            name (str): The player's name.
            life (int, optional): The starting life total. Defaults to 20.
        """
        self.name = name
        self.life = life
        self.zones: Dict[str, Zone] = {
            "Hand": Zone("Hand"),
            "Graveyard": Zone("Graveyard"),
            "Deck": Deck() # Deck is a specialized Zone
        }

    @property
    def hand(self) -> Zone:
        """A convenient property to access the player's hand zone."""
        return self.zones["Hand"]

    @property
    def deck(self) -> Deck:
        """A convenient property to access the player's deck."""
        return self.zones["Deck"]

    @property
    def graveyard(self) -> Zone:
        """A convenient property to access the player's graveyard."""
        return self.zones["Graveyard"]

    def setup_deck(self, cards: List[Card]):
        """Sets up the player's deck with a list of cards and shuffles it."""
        self.deck.cards = cards
        self.deck.shuffle()

    def draw_card(self):
        """Draws a card from the deck and puts it into the hand."""
        card = self.deck.draw()
        if card:
            self.hand.add(card)
        return card

    def __repr__(self) -> str:
        """Provides a developer-friendly string representation of the player."""
        return (f"Player(Name: '{self.name}', Life: {self.life}, "
                f"Deck: {len(self.deck)}, Hand: {len(self.hand)})")