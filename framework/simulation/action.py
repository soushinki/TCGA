from dataclasses import dataclass, field
from typing import Any, Dict

# We need a reference to GameState for type hinting
from ..core.game_state import GameState

@dataclass
class Action:
    """
    Represents a single, atomic action that a player can take.
    """
    player_id: str
    action_type: str
    details: Dict[str, Any] = field(default_factory=dict)
    
    # --- NEW METHOD TO MAKE THE ACTION'S STRING REPRESENTATION SMARTER ---
    def to_repr(self, game_state: GameState) -> str:
        """
        Creates a human-readable string representation of the action.
        This requires the game_state to look up card names from IDs.
        """
        player = next(p for p in game_state.players if p.name == self.player_id)
        
        if self.action_type == "PLAY_CARD":
            card_id = self.details['card_instance_id']
            card = next((c for c in player.hand.get_cards() if c.instance_id == card_id), None)
            return f"Play Card: {card.name if card else 'Unknown Card'}"

        if self.action_type == "ATTACK":
            attacker_id = self.details['attacker_id']
            target_id = self.details['target_id']
            
            attacker = next((c for c in player.board.get_cards() if c.instance_id == attacker_id), None)
            
            opponent = next(p for p in game_state.players if p is not player)
            target = next((c for c in opponent.board.get_cards() if c.instance_id == target_id), None)
            if not target and opponent.name == target_id:
                target = opponent # The target is the leader
            
            attacker_name = attacker.name if attacker else "Unknown"
            target_name = target.name if target else "Unknown"
            return f"Attack: {attacker_name} attacks {target_name}"

        if self.action_type == "EVOLVE":
            target_id = self.details['target_id']
            target = next((c for c in player.board.get_cards() if c.instance_id == target_id), None)
            return f"Evolve: {target.name if target else 'Unknown Follower'}"
        
        if self.action_type == "END_TURN":
            return "End Turn"

        # Fallback for any other action types
        return f"Action(Player: '{self.player_id}', Type: '{self.action_type}', Details: {self.details})"