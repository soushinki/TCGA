import uuid

class Card:
    """
    Represents a single, generic card in the game.

    This class is intentionally simple. It holds a unique ID to link to a
    script, a name, and a dictionary of properties that can be used by
    a specific game engine to store data like cost, power, type, etc.
    """
    def __init__(self, card_id: str, name: str, properties: dict = None):
        """
        Initializes a Card instance.

        Args:
            card_id (str): The unique identifier for the card, linking to its script.
            name (str): The display name of the card.
            properties (dict, optional): Game-specific attributes. Defaults to None.
        """
        self.instance_id = str(uuid.uuid4()) # Unique ID for this specific instance of the card
        self.card_id = card_id
        self.name = name
        self.properties = properties if properties is not None else {}

    def get_property(self, key: str, default=None):
        """Safely retrieves a property from the card."""
        return self.properties.get(key, default)

    def __repr__(self) -> str:
        """Provides a developer-friendly string representation of the card."""
        return f"Card(ID: {self.card_id}, Name: '{self.name}')"