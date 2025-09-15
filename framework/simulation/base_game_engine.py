from abc import ABC, abstractmethod
from typing import List, Optional

from ..core.game_state import GameState
from ..core.player import Player
from .action import Action

class BaseGameEngine(ABC):
    """
    Abstract Base Class (ABC) for a game engine.
    ...
    """
    # --- __init__ METHOD ADDED HERE ---
    def __init__(self, game_mode: str):
        """
        Initializes the base engine.

        Args:
            game_mode (str): A string identifying the game or ruleset (e.g., 'SV', 'SVWB').
        """
        self.game_mode = game_mode

    @abstractmethod
    def setup_game(self, game_state: GameState):
        pass

    @abstractmethod
    def get_possible_actions(self, game_state: GameState) -> List[Action]:
        pass

    @abstractmethod
    def apply_action(self, game_state: GameState, action: Action):
        pass

    @abstractmethod
    def check_win_condition(self, game_state: GameState) -> Optional[Player]:
        pass