from abc import ABC, abstractmethod

from ..core.player import Player
from ..core.card import Card
from ..core.game_state import GameState

class BaseResourceManager(ABC):
    """
    Abstract Base Class for a game's resource manager.

    This defines the contract for how the core simulator interacts with
    a game's specific resource system (e.g., Mana, Play Points, etc.).
    """
    def __init__(self, player: Player, game_state: GameState, game_mode: str):
        self.player = player
        self.game_state = game_state
        self.game_mode = game_mode

    @abstractmethod
    def start_turn(self):
        """Handles all resource updates at the start of a player's turn."""
        pass

    @abstractmethod
    def can_play_card(self, card: Card) -> bool:
        """Checks if the player has enough resources to play a given card."""
        pass

    @abstractmethod
    def spend_resources_for_card(self, card: Card):
        """Deducts the resources required to play a given card."""
        pass