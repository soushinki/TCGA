from abc import ABC, abstractmethod
from typing import List

from ..core.game_state import GameState
from .action import Action

class BaseGameEngine(ABC):
    """
    Abstract Base Class (ABC) for a game engine.

    This class defines the "contract" or interface that all specific TCG engines
    (like MtgEngine or YgoEngine) must adhere to. The GameSimulator will
    interact with any game engine through these methods, without needing to
    know the specific rules of the game it's running.
    """

    @abstractmethod
    def setup_game(self, game_state: GameState):
        """
        Performs any initial setup for the game.
        This is called once at the beginning of a simulation.
        For example, this is where players would draw their starting hands.
        """
        pass

    @abstractmethod
    def get_possible_actions(self, game_state: GameState) -> List[Action]:
        """
        Calculates and returns a list of all legal actions the active
        player can currently take.

        Args:
            game_state (GameState): The current state of the game.

        Returns:
            List[Action]: A list of valid Action objects.
        """
        pass

    @abstractmethod
    def apply_action(self, game_state: GameState, action: Action):
        """
        Applies a given action to the game state, modifying it according
        to the game's rules.

        This method contains the core rule enforcement logic. It will
        trigger effects, change player life totals, move cards between zones, etc.

        Args:
            game_state (GameState): The current state of the game to be modified.
            action (Action): The action to apply.
        """
        pass