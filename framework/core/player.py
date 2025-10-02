from typing import List, Dict, Optional

from .card import Card
from .deck import Deck
from .zone import Zone
'BaseResourceManager'

class Player:
    def __init__(self, name: str, life: int = 20):
        self.name = name
        self.life = life
        self.zones: Dict[str, Zone] = {
            "Hand": Zone("Hand", owner=self),
            "Graveyard": Zone("Graveyard", owner=self),
            "Deck": Deck(owner=self),
            "Board": Zone("Board", owner=self)
        }
        self.resources: Optional['BaseResourceManager'] = None
        self.has_decked_out: bool = False

    # ... (properties are unchanged)
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

    # --- METHOD UPDATED HERE ---
    def draw_card(self, game_state: 'GameState'): # Add game_state as an argument
        """
        Draws a card from the deck.
        Checks the hand size limit against the game engine's rule.
        """
        card = self.deck.draw()
        if not card:
            self.has_decked_out = True
            print(f"!!! {self.name}'s deck is empty. They will lose if the turn ends!")
            return None

        # --- UPDATED LOGIC ---
        # Get the hand size limit dynamically from the game engine.
        hand_limit = game_state.game_engine.max_hand_size
        
        if len(self.hand) >= hand_limit:
            print(f"!!! {self.name}'s hand is full (limit: {hand_limit})! '{card.name}' is discarded. !!!")
            self.graveyard.add(card)
        else:
            self.hand.add(card)
        
        return card

    def __repr__(self) -> str:
        # We can also add the resources to our printout for better debugging
        resource_str = f", Resources: ({self.resources})" if self.resources else ""
        return (f"Player(Name: '{self.name}', Life: {self.life}, "
                f"Deck: {len(self.deck)}, Hand: {len(self.hand)}, Board: {len(self.board)}{resource_str})")