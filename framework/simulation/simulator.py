from typing import List

# We will create BaseAgent in the next step, for now we just type hint it.
from ..agents.base_agent import BaseAgent 
from ..core.game_state import GameState
from ..core.player import Player
from .base_game_engine import BaseGameEngine

class GameSimulator:
    """
    The main orchestrator for running a game simulation.

    It is initialized with a specific game engine and a list of agents.
    It then runs the main game loop, asking agents for actions and using
    the game engine to apply them. This class is game-agnostic.
    """
    def __init__(self, game_engine: BaseGameEngine, agents: List[BaseAgent]):
        """
        Initializes the GameSimulator.

        Args:
            game_engine (BaseGameEngine): A concrete implementation of the game engine.
            agents (List[BaseAgent]): A list of agents that will play the game.
        """
        if len(agents) < 1:
            raise ValueError("Simulator requires at least one agent.")
        
        self.game_engine = game_engine
        self.agents = agents
        
        # Create players and the initial game state
        players = [Player(name=agent.name) for agent in self.agents]
        self.game_state = GameState(players=players)

    def run(self, max_turns: int = 50):
        """
        Runs the entire game simulation from start to finish.

        Args:
            max_turns (int): A safety limit to prevent infinite loops.
        """
        # Associate agents with players
        agent_player_map = {agent.name: player for agent, player in zip(self.agents, self.game_state.players)}

        # Perform initial game setup (e.g., draw starting hands)
        self.game_engine.setup_game(self.game_state)
        self.game_state.start_game()
        
        # Main game loop
        while self.game_state.turn_number <= max_turns:
            active_player = self.game_state.active_player
            # Find the agent corresponding to the active player
            active_agent = next(agent for agent in self.agents if agent.name == active_player.name)
            
            print("-" * 30)
            print(f"Current State: {self.game_state}")
            print(f"Active Player: {active_player}")
            
            # 1. Get all possible actions from the game engine
            possible_actions = self.game_engine.get_possible_actions(self.game_state)

            if not possible_actions:
                print(f"No possible actions for {active_player.name}. The game may be over.")
                break # End simulation if no actions can be taken

            # 2. Ask the active agent to choose an action
            chosen_action = active_agent.choose_action(self.game_state, possible_actions)

            print(f"Agent '{active_agent.name}' chose action: {chosen_action}")

            # 3. Apply the chosen action using the game engine
            self.game_engine.apply_action(self.game_state, chosen_action)

            # 4. End the current player's turn
            self.game_state.end_turn()

        print("=" * 30)
        print(f"Simulation finished after {self.game_state.turn_number - 1} turns.")