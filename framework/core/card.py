import uuid
from typing import Optional

# Forward reference for type hinting Player without circular imports
'Player'

class Card:
    """
    Represents a single, generic card in the game.
    """
    def __init__(self, card_id: str, name: str, properties: dict = None):
        self.instance_id = str(uuid.uuid4())
        self.card_id = card_id
        self.name = name
        self.properties = properties if properties is not None else {}
        
        # --- NEW ATTRIBUTE ---
        # This will be set by a Zone when a card enters it.
        self.owner: Optional['Player'] = None

    def get_property(self, key: str, default=None):
        """Safely retrieves a property from the card."""
        return self.properties.get(key, default)

    def __repr__(self) -> str:
        """Provides a developer-friendly string representation of the card."""
        return f"Card(ID: {self.card_id}, Name: '{self.name}')"