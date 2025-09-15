from abc import ABC, abstractmethod
from typing import List

from framework.core.game_state import GameState
from framework.simulation.action import Action

class BaseAgent(ABC):
    """
    Abstract Base Class (ABC) for all player agents.

    This class defines the "contract" for any agent that wants to play the game.
    The GameSimulator interacts with agents solely through the methods defined here.
    """
    def __init__(self, name: str):
        """
        Initializes the agent.

        Args:
            name (str): The name of the agent/player.
        """
        self.name = name

    @abstractmethod
    def choose_action(self, game_state: GameState, possible_actions: List[Action]) -> Action:
        """
        The core decision-making method for an agent.

        Given the current state of the game and a list of all legal actions,
        this method must choose and return one of those actions.

        Args:
            game_state (GameState): The current state of the game.
            possible_actions (List[Action]): A list of valid Action objects.

        Returns:
            Action: The chosen action from the possible_actions list.
        """
        pass

    def __repr__(self) -> str:
        return f"Agent(Name: '{self.name}')"