from abc import ABC, abstractmethod
from typing import List

from ..core.game_state import GameState
from ..core.player import Player
from .action import Action

class BaseActionGenerator(ABC):
    """
    Abstract Base Class for a game's action generator.

    This defines the contract for a module that is responsible for
    determining all possible legal moves for a given player and game state.
    """
    def __init__(self, game_mode: str):
        self.game_mode = game_mode

    @abstractmethod
    def get_possible_actions(self, game_state: GameState, player: Player) -> List[Action]:
        """
        Calculates all possible actions for the given player.

        Args:
            game_state (GameState): The current state of the game.
            player (Player): The player whose actions are to be generated.

        Returns:
            List[Action]: A list of all valid Action objects.
        """
        pass