import sys
from typing import List

# --- IMPORTS CORRECTED HERE ---
from framework.core.game_state import GameState
from framework.simulation.action import Action
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
        # --- THIS IS THE ONLY CHANGE ---
        # We now call the new to_repr() method and pass the game_state
        for i, action in enumerate(possible_actions):
            print(f"  {i}: {action.to_repr(game_state)}")
        
        prompt = "Enter the number of your choice (q to quit to menu, Ctrl+C to exit program): "

        while True:
            try:
                user_input = input(prompt)
                
                if user_input.lower() == 'q':
                    return None # Return the "quit to menu" signal

                choice_index = int(user_input)
                if 0 <= choice_index < len(possible_actions):
                    return possible_actions[choice_index]
                else:
                    print("Invalid number. Please choose from the list.")
            except ValueError:
                print("Invalid input. Please enter a number or 'q'.")
            except (KeyboardInterrupt, EOFError):
                print("\n\nExiting application...")
                sys.exit()