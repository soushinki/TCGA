from abc import ABC, abstractmethod
from typing import List, Optional

# The Optional type hint is new
from ..core.game_state import GameState
from ..core.player import Player # Import Player for the type hint
from .action import Action

class BaseGameEngine(ABC):
    """
    Abstract Base Class (ABC) for a game engine.
    ...
    """

    @abstractmethod
    def setup_game(self, game_state: GameState):
        """
        ...
        """
        pass

    @abstractmethod
    def get_possible_actions(self, game_state: GameState) -> List[Action]:
        """
        ...
        """
        pass

    @abstractmethod
    def apply_action(self, game_state: GameState, action: Action):
        """
        ...
        """
        pass

    # --- NEW METHOD ADDED HERE ---
    @abstractmethod
    def check_win_condition(self, game_state: GameState) -> Optional[Player]:
        """
        Checks if the game has ended and returns the winner.

        Args:
            game_state (GameState): The current state of the game.

        Returns:
            Optional[Player]: The winning Player object, or None if the game has not ended.
        """
        pass