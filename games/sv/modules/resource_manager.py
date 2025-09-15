from framework.core.player import Player
from framework.core.card import Card
from framework.core.game_state import GameState
from framework.simulation.base_resource_manager import BaseResourceManager

class SvResourceManager(BaseResourceManager):
    """
    Manages the resources for Shadowverse and Shadowverse: Worlds Beyond.
    This includes Play Points (PP), Evolve Points (EP), and Super Evolve Points (SEP).
    """
    def __init__(self, player: Player, game_state: GameState, game_mode: str):
        super().__init__(player, game_state, game_mode)
        
        # Core resources
        self.pp: int = 0
        self.max_pp: int = 0
        
        # Evolution resources are mode-dependent
        self.ep: int = 0
        self.sep: int = 0 # Only used in SVWB

        # Determine if this player is going first or second
        self.is_first_player = (self.game_state.players[0] == self.player)

        # Set starting evolution points based on game mode and player order
        if self.game_mode == 'SVWB':
            self.ep = 2
            self.sep = 2
        else: # Classic SV
            self.ep = 3 if not self.is_first_player else 2

    def start_turn(self):
        """
        Increments max PP, refills PP, and checks if Evolve Points should be granted.
        """
        # Increment and refill Play Points
        if self.max_pp < 10:
            self.max_pp += 1
        self.pp = self.max_pp

        # In classic SV, EP is granted on turn 4 or 5
        if self.game_mode == 'SV':
            turn_to_evolve = 5 if self.is_first_player else 4
            if self.game_state.turn_number == turn_to_evolve:
                print(f"--- {self.player.name} can now evolve! ---")

    def can_play_card(self, card: Card) -> bool:
        """Checks if the player has enough PP to play the card."""
        # Assumes card.properties['cost'] holds the PP cost
        cost = card.get_property('cost', 0)
        return self.pp >= cost

    def spend_resources_for_card(self, card: Card):
        """Spends the PP for playing a card."""
        cost = card.get_property('cost', 0)
        if self.pp >= cost:
            self.pp -= cost
        else:
            # This should ideally not be reached if can_play_card is checked first
            raise ValueError("Not enough PP to play this card.")
            
    # --- SV-Specific Methods ---

    def can_evolve(self) -> bool:
        """Checks if the player can perform a classic evolution."""
        turn_to_evolve = 5 if self.is_first_player else 4
        return self.ep > 0 and self.game_state.turn_number >= turn_to_evolve

    def spend_ep(self, amount: int = 1):
        """Spends a classic Evolve Point."""
        if self.ep >= amount:
            self.ep -= amount
        else:
            raise ValueError("Not enough EP to evolve.")

    def can_super_evolve(self) -> bool:
        """Checks if the player can perform a Super Evolution."""
        return (self.game_mode == 'SVWB' and 
                self.sep > 0 and 
                self.game_state.turn_number >= 7)

    def spend_sep(self, amount: int = 1):
        """Spends a Super Evolve Point."""
        if self.sep >= amount:
            self.sep -= amount
        else:
            raise ValueError("Not enough SEP to super evolve.")

    def __repr__(self) -> str:
        """Provides a string representation of the player's current resources."""
        base_repr = f"PP: {self.pp}/{self.max_pp}, EP: {self.ep}"
        if self.game_mode == 'SVWB':
            return base_repr + f", SEP: {self.sep}"
        return base_repr