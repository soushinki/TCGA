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
        if game_mode not in ['SV', 'SVWB']:
            raise ValueError("Invalid game mode specified for SvEngine.")
        
        self.max_hand_size = 9
        
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
                player.draw_card(game_state)
        game_state.players[1].draw_card(game_state)

    def get_possible_actions(self, game_state: GameState) -> List[Action]:
        active_player = game_state.active_player
        return self.action_generator.get_possible_actions(game_state, active_player)

    def apply_action(self, game_state: GameState, action: Action):
        player = next(p for p in game_state.players if p.name == action.player_id)
        resources: SvResourceManager = player.resources

        if action.action_type == "END_TURN":
            return

        elif action.action_type == "PLAY_CARD":
            card_id = action.details['card_instance_id']
            card = next((c for c in player.hand.get_cards() if c.instance_id == card_id), None)
            
            if card and resources.can_play_card(card):
                resources.spend_resources_for_card(card)
                player.hand.remove(card)
                
                card_type = card.get_property("type")
                if card_type in ["Follower", "Amulet"]:
                    player.board.add(card)
                    if card_type == "Follower":
                        card.turn_played = game_state.turn_number
                else:
                    player.graveyard.add(card)
                
                # self.trigger_manager is now the only one that prints during an action
                self.trigger_manager.post_event("on_play", card=card)
        
        elif action.action_type == "ATTACK":
            attacker = next((c for c in player.board.get_cards() if c.instance_id == action.details['attacker_id']), None)
            opponent = next(p for p in game_state.players if p is not player)
            target_id = action.details['target_id']
            target = next((c for c in opponent.board.get_cards() if c.instance_id == target_id), None)
            if not target and opponent.name == target_id:
                target = opponent

            if attacker and target:
                attacker.attacks_made_this_turn += 1
                
                if isinstance(target, Player):
                    target.life -= attacker.get_property('atk', 0)
                else:
                    target.properties['def'] -= attacker.get_property('atk', 0)
                    attacker.properties['def'] -= target.get_property('atk', 0)
                
                if not isinstance(target, Player) and target.get_property('def', 0) <= 0:
                    opponent.board.remove(target)
                    opponent.graveyard.add(target)
                    self.trigger_manager.post_event("on_destroy", card=target)

                if attacker.get_property('def', 0) <= 0:
                    player.board.remove(attacker)
                    player.graveyard.add(attacker)
                    self.trigger_manager.post_event("on_destroy", card=attacker)
        
        elif action.action_type == "EVOLVE":
            if resources.can_evolve():
                resources.has_evolved_this_turn = True
                resources.spend_ep()
                target_id = action.details['target_id']
                target = next((c for c in player.board.get_cards() if c.instance_id == target_id), None)
                if target:
                    target.properties['atk'] += 2
                    target.properties['def'] += 2
                    target.properties['is_evolved'] = True
                    target.properties['gained_rush_this_turn'] = True
                    self.trigger_manager.post_event("on_evolve", card=target)

        elif action.action_type == "SUPER_EVOLVE":
            if resources.can_super_evolve():
                resources.has_evolved_this_turn = True
                resources.spend_sep()
                # TODO: Implement Super Evolve logic

    def check_win_condition(self, game_state: GameState) -> Optional[Player]:
        for player in game_state.players:
            opponent = next(p for p in game_state.players if p is not player)
            
            if opponent.life <= 0:
                return player

            if opponent.has_decked_out:
                return player

        return None