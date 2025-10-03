from dataclasses import dataclass, field
from typing import Any, Dict

from ..core.game_state import GameState

@dataclass
class Action:
    """
    Represents a single, atomic action that a player can take.
    """
    player_id: str
    action_type: str
    details: Dict[str, Any] = field(default_factory=dict)
    
    def to_repr(self, game_state: GameState) -> str:
        """
        Creates a human-readable string representation of the action.
        """
        player = next((p for p in game_state.players if p.name == self.player_id), None)
        if not player: return "Action by Unknown Player"

        if self.action_type == "PLAY_CARD":
            card_id = self.details['card_instance_id']
            card = next((c for c in player.hand.get_cards() if c.instance_id == card_id), None)
            if not card: card = next((c for c in player.board.get_cards() if c.instance_id == card_id), None)
            if not card: card = next((c for c in player.graveyard.get_cards() if c.instance_id == card_id), None)
            return f"Played {card.name}" if card else "Played Unknown Card"

        if self.action_type == "ATTACK":
            attacker_id = self.details['attacker_id']
            target_id = self.details['target_id']
            
            attacker = next((c for c in player.board.get_cards() if c.instance_id == attacker_id), None)
            
            opponent = next(p for p in game_state.players if p is not player)
            # --- FIX APPLIED HERE: Search board AND graveyard for the target ---
            target = next((c for c in opponent.board.get_cards() if c.instance_id == target_id), None)
            if not target: target = next((c for c in opponent.graveyard.get_cards() if c.instance_id == target_id), None)
            
            if not target and opponent.name == target_id:
                target = opponent
            
            attacker_name = attacker.name if attacker else "Unknown"
            target_name = target.name if target else "Unknown"
            return f"Attacked {target_name} with {attacker_name}"

        if self.action_type == "EVOLVE":
            target_id = self.details['target_id']
            target = next((c for c in player.board.get_cards() if c.instance_id == target_id), None)
            return f"Evolved {target.name}" if target else "Evolved Unknown Follower"
        
        if self.action_type == "END_TURN":
            return "Ended Turn"

        return f"Action(Type: '{self.action_type}')" # Fallback