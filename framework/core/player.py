from typing import List, Dict, Optional # Optional is new
from .card import Card
from .deck import Deck
from .zone import Zone

# We need a forward reference for the type hint, as the files import each other
# This will resolve to the BaseResourceManager class at runtime.
'BaseResourceManager'

class Player:
    """
    Represents a player in the game. Manages the player's life total,
    and all zones associated with the player (Hand, Deck, Graveyard).
    """
    def __init__(self, name: str, life: int = 20):
        self.name = name
        self.life = life
        # --- ZONES NOW GET AN OWNER ---
        self.zones: Dict[str, Zone] = {
            "Hand": Zone("Hand", owner=self),
            "Graveyard": Zone("Graveyard", owner=self),
            "Deck": Deck(owner=self), # Deck needs owner too
            "Board": Zone("Board", owner=self)
        }
        self.resources: Optional['BaseResourceManager'] = None

    # ... (properties and other methods are unchanged)
    @property
    def hand(self) -> Zone:
        return self.zones["Hand"]

    @property
    def deck(self) -> Deck:
        return self.zones["Deck"]
        
    @property
    def graveyard(self) -> Zone:
        return self.zones["Graveyard"]

    @property
    def board(self) -> Zone:
        return self.zones["Board"]
        
    def setup_deck(self, cards: List[Card]):
        self.deck.cards = cards
        self.deck.shuffle()

    def draw_card(self):
        card = self.deck.draw()
        if card:
            self.hand.add(card)
        else:
            print(f"!!! {self.name}'s deck is empty. Cannot draw a card.")
        return card

    def __repr__(self) -> str:
        # We can also add the resources to our printout for better debugging
        resource_str = f", Resources: ({self.resources})" if self.resources else ""
        return (f"Player(Name: '{self.name}', Life: {self.life}, "
                f"Deck: {len(self.deck)}, Hand: {len(self.hand)}, Board: {len(self.board)}{resource_str})")