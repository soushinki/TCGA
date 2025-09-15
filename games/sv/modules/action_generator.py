from typing import List

from ....framework.core.game_state import GameState
from ....framework.core.player import Player
from ....framework.simulation.action import Action
from ....framework.simulation.base_action_generator import BaseActionGenerator
from .resource_manager import SvResourceManager

class SvActionGenerator(BaseActionGenerator):
    """
    Generates all possible actions for a player in a Shadowverse game.
    """
    def get_possible_actions(self, game_state: GameState, player: Player) -> List[Action]:
        actions: List[Action] = []
        resources: SvResourceManager = player.resources

        # 1. Generate "Play Card" actions
        # Assumes a 'Board' zone exists, check if it's full.
        if len(player.board.get_cards()) < 5:
            for card in player.hand.get_cards():
                if resources.can_play_card(card):
                    actions.append(Action(
                        player_id=player.name,
                        action_type="PLAY_CARD",
                        details={"card_instance_id": card.instance_id}
                    ))

        # 2. Generate "Attack" actions
        # TODO: This logic should be expanded to correctly handle Ward.
        attackers = [f for f in player.board.get_cards() if f.get_property("can_attack", True)] # Assume True for now
        opponent = next(p for p in game_state.players if p is not player)
        valid_targets = opponent.board.get_cards() + [opponent]

        for attacker in attackers:
            for target in valid_targets:
                # --- THIS IS THE IMPROVEMENT ---
                # Use instance_id for cards, but the player's name for the player object
                target_id = target.instance_id if hasattr(target, 'instance_id') else target.name
                actions.append(Action(
                    player_id=player.name,
                    action_type="ATTACK",
                    details={"attacker_id": attacker.instance_id, "target_id": target_id}
                ))

        # 3. Generate "Evolve" actions
        if resources.can_evolve():
            evolve_targets = [f for f in player.board.get_cards() if not f.get_property("is_evolved", False)]
            for target in evolve_targets:
                actions.append(Action(
                    player_id=player.name,
                    action_type="EVOLVE",
                    details={"target_id": target.instance_id}
                ))
        
        # 4. Generate "Super Evolve" actions
        if resources.can_super_evolve():
            super_evolve_targets = [f for f in player.board.get_cards() if f.get_property("is_evolved", False)]
            for target in super_evolve_targets:
                 actions.append(Action(
                    player_id=player.name,
                    action_type="SUPER_EVOLVE",
                    details={"target_id": target.instance_id}
                ))

        # 5. Generate "End Turn" action
        actions.append(Action(player_id=player.name, action_type="END_TURN"))

        return actions