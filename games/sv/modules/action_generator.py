from typing import List

from ....framework.core.game_state import GameState
from ....framework.core.player import Player
from ....framework.simulation.action import Action
from ....framework.simulation.base_action_generator import BaseActionGenerator
from .resource_manager import SvResourceManager # We need to import this!

class SvActionGenerator(BaseActionGenerator):
    """
    Generates all possible actions for a player in a Shadowverse game,
    respecting the rules for SV and SVWB game modes.
    """
    def get_possible_actions(self, game_state: GameState, player: Player) -> List[Action]:
        """
        Builds a list of all valid moves for the player.
        """
        actions: List[Action] = []
        
        # We need to access the player's specific resource manager
        # In a real implementation, the player object would hold a reference to its resource manager.
        # For now, we'll assume we can get it. (This will be wired up in the main SvEngine).
        resources: SvResourceManager = player.resources

        # 1. Generate "Play Card" actions
        board_full = len(player.zones["Board"].get_cards()) >= 5 # Assuming a 'Board' zone
        if not board_full:
            for card in player.hand.get_cards():
                if resources.can_play_card(card):
                    actions.append(Action(
                        player_id=player.name,
                        action_type="PLAY_CARD",
                        details={"card_instance_id": card.instance_id}
                    ))

        # 2. Generate "Attack" actions
        # Simplified: doesn't account for Ward yet. We'll add that later.
        attackers = [f for f in player.zones["Board"].get_cards() if f.get_property("can_attack", False)]
        opponent = next(p for p in game_state.players if p is not player)
        valid_targets = opponent.zones["Board"].get_cards() + [opponent] # Followers + Leader

        for attacker in attackers:
            for target in valid_targets:
                actions.append(Action(
                    player_id=player.name,
                    action_type="ATTACK",
                    details={"attacker_id": attacker.instance_id, "target_id": target.instance_id}
                ))

        # 3. Generate "Evolve" actions
        if resources.can_evolve():
            # For now, assume any follower on board can be evolved.
            evolve_targets = [f for f in player.zones["Board"].get_cards() if not f.get_property("is_evolved", False)]
            for target in evolve_targets:
                actions.append(Action(
                    player_id=player.name,
                    action_type="EVOLVE",
                    details={"target_id": target.instance_id}
                ))
        
        # 4. Generate "Super Evolve" actions (for SVWB mode)
        if resources.can_super_evolve():
            # For now, assume any evolved follower can be super evolved.
            super_evolve_targets = [f for f in player.zones["Board"].get_cards() if f.get_property("is_evolved", False)]
            for target in super_evolve_targets:
                 actions.append(Action(
                    player_id=player.name,
                    action_type="SUPER_EVOLVE",
                    details={"target_id": target.instance_id}
                ))

        # 5. Generate "End Turn" action
        actions.append(Action(player_id=player.name, action_type="END_TURN"))

        return actions