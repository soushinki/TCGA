import random
from typing import List

from framework.core.game_state import GameState
from framework.simulation.action import Action
from .base_agent import BaseAgent

class SimpleAiAgent(BaseAgent):
    """
    A basic AI agent that makes decisions by choosing a random valid action.
    """
    def choose_action(self, game_state: GameState, possible_actions: List[Action]) -> Action:
        """
        Chooses a random action from the list of possible actions.
        """
        # For now, the "strategy" is to simply pick a random available move.
        chosen_action = random.choice(possible_actions)
        return chosen_action