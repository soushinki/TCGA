from typing import List

from agents.base_agent import BaseAgent
from ..core.game_state import GameState
from ..core.player import Player
from .base_game_engine import BaseGameEngine

class GameSimulator:
    # ... (__init__ is unchanged)
    def __init__(self, game_engine: BaseGameEngine, agents: List[BaseAgent]):
        if len(agents) < 1:
            raise ValueError("Simulator requires at least one agent.")
        self.game_engine = game_engine
        self.agents = agents
        players = [Player(name=agent.name) for agent in self.agents]
        self.game_state = GameState(players=players)


    def run(self, max_turns: int = 50):
        self.game_engine.setup_game(self.game_state)
        self.game_state.start_game()
        
        winner = None
        while self.game_state.turn_number <= max_turns:
            active_player = self.game_state.active_player
            active_agent = next(agent for agent in self.agents if agent.name == active_player.name)
            
            if active_player.resources:
                active_player.resources.start_turn()
            active_player.draw_card()
            
            print("-" * 30)
            print(f"Current State: {self.game_state}")
            print(f"Active Player: {active_player}")
            
            # --- NEW: Inner loop for the player's turn ---
            while True:
                # 1. Get all possible actions from the game engine
                possible_actions = self.game_engine.get_possible_actions(self.game_state)
                if not possible_actions:
                    print(f"No possible actions for {active_player.name}.")
                    break # No actions, so the turn must end.

                # 2. Ask the active agent to choose an action
                chosen_action = active_agent.choose_action(self.game_state, possible_actions)
                if chosen_action is None: # Signal to quit to menu
                    print("\n--- Game aborted by user. Returning to main menu. ---")
                    return

                # --- FIX #1: Use the human-readable representation in the log ---
                print(f"Agent '{active_agent.name}' chose: {chosen_action.to_repr(self.game_state)}")

                # 3. Apply the chosen action using the game engine
                self.game_engine.apply_action(self.game_state, chosen_action)
                
                # Check for a winner after every single action
                winner = self.game_engine.check_win_condition(self.game_state)
                if winner:
                    break # Exit the inner turn loop if the game is over

                # --- FIX #2: Only end the turn if the action was END_TURN ---
                if chosen_action.action_type == "END_TURN":
                    break # Exit the inner turn loop

            if winner:
                print("=" * 30)
                print(f"GAME OVER! The winner is {winner.name}!")
                break # Exit the main game loop
            
            self.game_state.end_turn()

        if not winner:
            print("=" * 30)
            print(f"Simulation finished after reaching the {max_turns} turn limit. No winner.")