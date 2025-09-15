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
        # ... (setup is unchanged)
        self.game_engine.setup_game(self.game_state)
        self.game_state.start_game()
        
        winner = None
        while self.game_state.turn_number <= max_turns:
            active_player = self.game_state.active_player
            active_agent = next(agent for agent in self.agents if agent.name == active_player.name)
            
            # --- GAME PACING FIX ---
            # Player draws a card at the start of their turn.
            active_player.draw_card()
            
            print("-" * 30)
            print(f"Current State: {self.game_state}")
            print(f"Active Player: {active_player}")
            
            possible_actions = self.game_engine.get_possible_actions(self.game_state)
            if not possible_actions:
                print(f"No possible actions for {active_player.name}.")
                break

            chosen_action = active_agent.choose_action(self.game_state, possible_actions)
            print(f"Agent '{active_agent.name}' chose action: {chosen_action}")
            
            self.game_engine.apply_action(self.game_state, chosen_action)
            
            # --- WIN CONDITION FIX ---
            # Check for a winner after every action.
            winner = self.game_engine.check_win_condition(self.game_state)
            if winner:
                print("=" * 30)
                print(f"GAME OVER! The winner is {winner.name}!")
                break # Exit the loop immediately
            
            self.game_state.end_turn()

        print("=" * 30)
        if not winner:
            print(f"Simulation finished after reaching the {max_turns} turn limit. No winner.")