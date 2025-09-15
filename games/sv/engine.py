from typing import List, Optional

from ...framework.core.game_state import GameState
from ...framework.core.player import Player
from ...framework.simulation.action import Action
from ...framework.simulation.base_game_engine import BaseGameEngine
from .modules.resource_manager import SvResourceManager
from .modules.action_generator import SvActionGenerator

class SvEngine(BaseGameEngine):
    """
    The concrete game engine for Shadowverse and Shadowverse: Worlds Beyond.
    It assembles the various game logic modules and enforces the game's rules.
    """
    def __init__(self, game_mode: str):
        if game_mode not in ['SV', 'SVWB']:
            raise ValueError("Invalid game mode specified for SvEngine.")
        
        # This engine gets its own instance of the action generator.
        self.action_generator = SvActionGenerator(game_mode)
        self.game_mode = game_mode

    def setup_game(self, game_state: GameState):
        """
        Initializes players with SV-specific resources and starting hands.
        """
        # Determine starting hand size based on game mode
        hand_size = 4 if self.game_mode == 'SVWB' else 3
        
        for player in game_state.players:
            # Attach a configured resource manager to each player
            player.resources = SvResourceManager(player, game_state, self.game_mode)
            player.life = 20 # SV leaders start with 20 defense
            
            # Draw starting hand
            for _ in range(hand_size):
                player.draw_card()
        
        # Handle the second player's extra card draw
        game_state.players[1].draw_card()

    def get_possible_actions(self, game_state: GameState) -> List[Action]:
        """
        Delegates action generation to the action_generator module.
        """
        active_player = game_state.active_player
        return self.action_generator.get_possible_actions(game_state, active_player)

    def apply_action(self, game_state: GameState, action: Action):
        """
        Executes an action and modifies the game state. This is the core of rule enforcement.
        """
        player = next(p for p in game_state.players if p.name == action.player_id)

        if action.action_type == "END_TURN":
            return # The simulator handles advancing the turn

        elif action.action_type == "PLAY_CARD":
            card_id = action.details['card_instance_id']
            card = next((c for c in player.hand.get_cards() if c.instance_id == card_id), None)
            if card and player.resources.can_play_card(card):
                player.resources.spend_resources_for_card(card)
                player.hand.remove(card)
                
                # Simplified: assumes all non-spells go to board.
                # A real implementation would check card type.
                player.board.add(card)
                print(f"{player.name} played {card.name}.")
                # TODO: Trigger Fanfare effects via the Lua scripting engine.
            
        elif action.action_type == "ATTACK":
            attacker = next((c for c in player.board.get_cards() if c.instance_id == action.details['attacker_id']), None)
            opponent = next(p for p in game_state.players if p is not player)
            
            # Target could be a follower or the leader
            target_id = action.details['target_id']
            target = next((c for c in opponent.board.get_cards() if c.instance_id == target_id), None)
            if not target and opponent.instance_id == target_id: # Simplified way to check if target is leader
                 target = opponent
            
            if attacker and target:
                # Basic combat logic, needs expansion for keywords like Ward, Bane, etc.
                print(f"{attacker.name} attacks {target.name if isinstance(target, Player) else target.name}!")
                # TODO: Implement combat logic.
            
        elif action.action_tpye == "EVOLVE":
            if player.resources.can_evolve():
                player.resources.spend_ep()
                target_id = action.details['target_id']
                target = next((c for c in player.board.get_cards() if c.instance_id == target_id), None)
                print(f"{player.name} evolves {target.name}!")
                # TODO: Apply evolve stats and trigger on_evolve effects via Lua.

    def check_win_condition(self, game_state: GameState) -> Optional[Player]:
        """
        A player wins if their opponent's life is 0 or less.
        """
        for player in game_state.players:
            opponent = next(p for p in game_state.players if p is not player)
            if opponent.life <= 0:
                return player
        return None