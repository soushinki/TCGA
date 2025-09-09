from dataclasses import dataclass, field
from typing import Any, Dict

@dataclass
class Action:
    """
    Represents a single, atomic action that a player can take.

    Using a dataclass provides a concise way to create a class primarily
    for storing data. It automatically generates methods like __init__ and __repr__.
    """
    player_id: str
    action_type: str
    details: Dict[str, Any] = field(default_factory=dict)

    def __repr__(self) -> str:
        """Provides a developer-friendly string representation of the action."""
        return (f"Action(Player: '{self.player_id}', Type: '{self.action_type}', "
                f"Details: {self.details})")