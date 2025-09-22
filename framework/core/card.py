import uuid
from typing import Optional

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
        self.owner: Optional['Player'] = None

        # --- NEW ATTRIBUTES FOR FLEXIBLE ATTACK LOGIC ---
        # Tracks how many times this follower has attacked this turn.
        self.attacks_made_this_turn: int = 0
        
        # Most followers can only attack once. This can be overridden by card effects.
        # We can get this from properties, but a direct attribute is also fine for now.
        self.max_attacks_per_turn: int = self.properties.get("max_attacks", 1)


    def get_property(self, key: str, default=None):
        return self.properties.get(key, default)

    def __repr__(self) -> str:
        return f"Card(ID: {self.card_id}, Name: '{self.name}')"