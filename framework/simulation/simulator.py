from typing import List

from agents.base_agent import BaseAgent
from ..core.game_state import GameState
from ..core.player import Player
from .base_game_engine import BaseGameEngine
from ..utils.display import Display

class GameSimulator:
    def __init__(self, game_engine: BaseGameEngine, agents: List[BaseAgent]):
        if len(agents) < 1:
            raise ValueError("Simulator requires at least one agent.")
        self.game_engine = game_engine
        self.agents = agents
        players = [Player(name=agent.name) for agent in self.agents]
        self.game_state = GameState(players=players, game_engine=self.game_engine)
        self.display = Display()

    def run(self, max_turns: int = 50, log_level: str = 'pretty'):
        self.game_engine.setup_game(self.game_state)
        self.game_state.start_game()
        
        winner = None
        while self.game_state.turn_number <= max_turns:
            active_player = self.game_state.active_player
            active_agent = next(agent for agent in self.agents if agent.name == active_player.name)
            
            if active_player.resources:
                active_player.resources.start_turn()
            active_player.draw_card(self.game_state)
            
            if log_level == 'pretty':
                self.display.display_board(self.game_state)
            else:
                print("-" * 30)
                print(f"Turn {self.game_state.turn_number}: {active_player.name}")

            # Inner loop for player's turn
            while True:
                possible_actions = self.game_engine.get_possible_actions(self.game_state)
                if not possible_actions:
                    break

                chosen_action = active_agent.choose_action(self.game_state, possible_actions)
                
                # --- FIX APPLIED HERE ---
                # Check for the quit signal IMMEDIATELY after the agent makes its choice.
                if chosen_action == "quit_to_menu":
                    print("\n--- Game aborted by user. Returning to main menu. ---")
                    return # Exit the run method before the action is processed further.

                self.game_engine.apply_action(self.game_state, chosen_action)
                
                if log_level == 'pretty':
                    self.display.display_board(self.game_state)
                elif log_level == 'simple':
                    print(f"  > {chosen_action.to_repr(self.game_state)}")

                winner = self.game_engine.check_win_condition(self.game_state)
                if winner:
                    break
                if chosen_action.action_type == "END_TURN":
                    break

            if winner:
                print("=" * 30)
                print(f"GAME OVER! The winner is {winner.name}!")
                break
            
            self.game_state.end_turn()

        if not winner:
            print("=" * 30)
            print(f"Simulation finished after reaching the {max_turns} turn limit. No winner.")