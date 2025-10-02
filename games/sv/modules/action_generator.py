from typing import List

from framework.core.game_state import GameState
from framework.core.player import Player
from framework.simulation.action import Action
from framework.simulation.base_action_generator import BaseActionGenerator
from .resource_manager import SvResourceManager

class SvActionGenerator(BaseActionGenerator):
    def get_possible_actions(self, game_state: GameState, player: Player) -> List[Action]:
        actions: List[Action] = []
        resources: SvResourceManager = player.resources

        # 1. Generate "Play Card" actions
        if len(player.board.get_cards()) < 5:
            for card in player.hand.get_cards():
                if resources.can_play_card(card):
                    actions.append(Action(
                        player_id=player.name,
                        action_type="PLAY_CARD",
                        details={"card_instance_id": card.instance_id}
                    ))

        # 2. Generate "Attack" actions
        opponent = next(p for p in game_state.players if p is not player)
        
        # Get all potential targets on the opponent's side that are followers
        opponent_followers = [f for f in opponent.board.get_cards() if f.get_property("type") == "Follower"]
        
        # Determine valid targets first, respecting Ward
        ward_followers = [f for f in opponent_followers if "Ward" in f.get_property("effect_text", "")]
        
        for follower in player.board.get_cards():
            if follower.get_property("type") != "Follower":
                continue # Skip amulets

            if follower.attacks_made_this_turn >= follower.max_attacks_per_turn:
                continue

            can_attack_followers = False
            can_attack_leader = False
            effect_text = follower.get_property("effect_text", "")
            was_played_this_turn = (follower.turn_played == game_state.turn_number)

            if not was_played_this_turn:
                can_attack_followers = True
                can_attack_leader = True
            else:
                if "Storm" in effect_text:
                    can_attack_followers = True
                    can_attack_leader = True
                elif "Rush" in effect_text:
                    can_attack_followers = True
                elif follower.get_property('gained_rush_this_turn', False):
                    can_attack_followers = True
            
            if not can_attack_followers and not can_attack_leader:
                continue

            possible_targets = []
            if ward_followers:
                if can_attack_followers:
                    possible_targets.extend(ward_followers)
            else:
                if can_attack_leader:
                    possible_targets.append(opponent)
                if can_attack_followers:
                    possible_targets.extend(opponent_followers)

            for target in possible_targets:
                target_id = target.instance_id if hasattr(target, 'instance_id') else target.name
                actions.append(Action(
                    player_id=player.name,
                    action_type="ATTACK",
                    details={"attacker_id": follower.instance_id, "target_id": target_id}
                ))
        
        # 3. Generate "Evolve" actions
        if resources.can_evolve():
            evolve_targets = [
                f for f in player.board.get_cards() 
                if f.get_property("type") == "Follower" and not f.get_property("is_evolved", False)
            ]
            for target in evolve_targets:
                actions.append(Action(
                    player_id=player.name,
                    action_type="EVOLVE",
                    details={"target_id": target.instance_id}
                ))
        
        # 4. Generate "Super Evolve" actions
        if resources.can_super_evolve():
            super_evolve_targets = [
                f for f in player.board.get_cards() 
                if f.get_property("type") == "Follower" and f.get_property("is_evolved", False)
            ]
            for target in super_evolve_targets:
                 actions.append(Action(
                    player_id=player.name,
                    action_type="SUPER_EVOLVE",
                    details={"target_id": target.instance_id}
                ))

        # 5. Generate "End Turn" action
        actions.append(Action(player_id=player.name, action_type="END_TURN"))

        return actions