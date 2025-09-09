from typing import List

from ..framework.core.game_state import GameState
from ..framework.simulation.action import Action
from .base_agent import BaseAgent

class HumanAgent(BaseAgent):
    """
    An agent that allows a human player to make decisions via the command line.
    """
    def choose_action(self, game_state: GameState, possible_actions: List[Action]) -> Action:
        """
        Prompts the human player to choose an action from the list of possibilities.
        """
        print(f"\n{self.name}, it's your turn. Choose an action:")
        for i, action in enumerate(possible_actions):
            print(f"  {i}: {action}")

        while True:
            try:
                choice_index = int(input("Enter the number of your choice: "))
                if 0 <= choice_index < len(possible_actions):
                    return possible_actions[choice_index]
                else:
                    print("Invalid number. Please choose from the list.")
            except ValueError:
                print("Invalid input. Please enter a number.")
            except (KeyboardInterrupt, EOFError):
                print("\nExiting.")
                # Default to the first action on exit.
                return possible_actions[0]