from typing import List, Optional

from framework.core.game_state import GameState
from framework.core.player import Player
from framework.core.card import Card
from framework.simulation.action import Action
from framework.simulation.base_game_engine import BaseGameEngine
from framework.scripting.lua_engine import LuaEngine
from .modules.resource_manager import SvResourceManager
from .modules.action_generator import SvActionGenerator
from .modules.trigger_manager import TriggerManager
from .api.script_api import ScriptAPI

class SvEngine(BaseGameEngine):
    """
    The concrete game engine for Shadowverse and Shadowverse: Worlds Beyond.
    """
    def __init__(self, game_mode: str):
        super().__init__(game_mode)
        
        self.game_state: Optional[GameState] = None
        self.action_generator = SvActionGenerator(game_mode)
        self.script_api = ScriptAPI(self)
        self.lua_engine = LuaEngine(self.script_api)
        self.trigger_manager = TriggerManager(self)

    def setup_game(self, game_state: GameState):
        self.game_state = game_state
        hand_size = 4 if self.game_mode == 'SVWB' else 3
        for player in game_state.players:
            player.resources = SvResourceManager(player, game_state, self.game_mode)
            player.life = 20
            for _ in range(hand_size):
                player.draw_card()
        game_state.players[1].draw_card()

    def get_possible_actions(self, game_state: GameState) -> List[Action]:
        active_player = game_state.active_player
        return self.action_generator.get_possible_actions(game_state, active_player)

    def apply_action(self, game_state: GameState, action: Action):
        player = next(p for p in game_state.players if p.name == action.player_id)

        if action.action_type == "END_TURN":
            return

        elif action.action_type == "PLAY_CARD":
            card_id = action.details['card_instance_id']
            card = next((c for c in player.hand.get_cards() if c.instance_id == card_id), None)
            if card and player.resources.can_play_card(card):
                player.resources.spend_resources_for_card(card)
                player.hand.remove(card)
                player.board.add(card)
                print(f"{player.name} played {card.name}.")
                self.trigger_manager.post_event("on_play", card=card)
        
        # --- ATTACK LOGIC RESTORED AND IMPLEMENTED ---
        elif action.action_type == "ATTACK":
            player = next(p for p in game_state.players if p.name == action.player_id)
            attacker = next((c for c in player.board.get_cards() if c.instance_id == action.details['attacker_id']), None)
            opponent = next(p for p in game_state.players if p is not player)
            target_id = action.details['target_id']
            target = next((c for c in opponent.board.get_cards() if c.instance_id == target_id), None)
            if not target and opponent.name == target_id:
                target = opponent

            if attacker and target:
                print(f"{attacker.name} ({attacker.get_property('atk')}/{attacker.get_property('def')}) attacks {target.name if isinstance(target, Player) else target.name}!")
                
                # --- NEW: Increment the attack counter ---
                attacker.attacks_made_this_turn += 1
                
                # Deal damage
                if isinstance(target, Player):
                    target.life -= attacker.get_property('atk', 0)
                else: # Target is a follower
                    target.properties['def'] -= attacker.get_property('atk', 0)
                    attacker.properties['def'] -= target.get_property('atk', 0)
                
                # Check for destroyed followers
                if not isinstance(target, Player) and target.get_property('def', 0) <= 0:
                    opponent.board.remove(target)
                    opponent.graveyard.add(target)
                    print(f"{target.name} was destroyed.")
                    self.trigger_manager.post_event("on_destroy", card=target)

                if attacker.get_property('def', 0) <= 0:
                    player.board.remove(attacker)
                    player.graveyard.add(attacker)
                    print(f"{attacker.name} was destroyed.")
                    self.trigger_manager.post_event("on_destroy", card=attacker)
        
        # --- EVOLVE LOGIC RESTORED AND IMPLEMENTED ---
        elif action.action_type == "EVOLVE":
            if player.resources.can_evolve():
                player.resources.spend_ep()
                target_id = action.details['target_id']
                target = next((c for c in player.board.get_cards() if c.instance_id == target_id), None)
                if target:
                    print(f"{player.name} evolves {target.name}!")
                    
                    # Apply default +2/+2 stat boost
                    target.properties['atk'] += 2
                    target.properties['def'] += 2
                    target.properties['is_evolved'] = True
                    print(f"{target.name} is now a {target.get_property('atk')}/{target.get_property('def')}.")

                    # Post an on_evolve event for the TriggerManager to handle
                    self.trigger_manager.post_event("on_evolve", card=target)

    def check_win_condition(self, game_state: GameState) -> Optional[Player]:
        """
        A player wins if their opponent's life is 0 or less,
        OR if the opponent has decked out.
        """
        for player in game_state.players:
            opponent = next(p for p in game_state.players if p is not player)
            
            # Check for life total win
            if opponent.life <= 0:
                print(f"--- Win Condition Met: {opponent.name}'s life is {opponent.life} ---")
                return player # This player is the winner

            # --- NEW: Check for deck out win ---
            if opponent.has_decked_out:
                print(f"--- Win Condition Met: {opponent.name} has decked out ---")
                return player # This player is the winner

        return None # No winner yet