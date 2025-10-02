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
        self.attacks_made_this_turn: int = 0
        self.max_attacks_per_turn: int = self.properties.get("max_attacks", 1)

        # --- NEW ATTRIBUTE ---
        # Records the turn number this card was played on. 0 means it started in play or is not on board.
        self.turn_played: int = 0

    def get_property(self, key: str, default=None):
        return self.properties.get(key, default)

    def __repr__(self) -> str:
        return f"Card(ID: {self.card_id}, Name: '{self.name}')"