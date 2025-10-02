from typing import List
from .player import Player

class GameState:
    """
    Represents the complete state of the game at any given moment.

    This is the top-level container that holds all players, tracks the
    current turn, and manages any global game zones.
    """
    def __init__(self, players: List[Player], game_engine: 'BaseGameEngine'):
        """
        Initializes the GameState.

        Args:
            players (List[Player]): A list of Player objects participating in the game.
        """
        if not players or len(players) < 1:
            raise ValueError("GameState requires at least one player.")
        
        self.players = players
        self.game_engine = game_engine
        self.turn_number = 0
        self.active_player_index = -1 # No active player until the game starts

    @property
    def active_player(self) -> Player:
        """Returns the player whose turn it is currently."""
        if 0 <= self.active_player_index < len(self.players):
            return self.players[self.active_player_index]
        return None

    def start_game(self):
        """Initializes the game, setting the turn to 1 and the first player as active."""
        print("Game is starting...")
        self.turn_number = 1
        self.active_player_index = 0
        print(f"Turn {self.turn_number}: It is {self.active_player.name}'s turn.")

    def end_turn(self):
        """Ends the current turn and advances to the next player."""
        # Simple turn progression: cycle through players.
        self.active_player_index = (self.active_player_index + 1) % len(self.players)
        
        # If we've looped back to the first player, it's a new round of turns.
        if self.active_player_index == 0:
            self.turn_number += 1

        print(f"Turn {self.turn_number}: It is now {self.active_player.name}'s turn.")

    def __repr__(self) -> str:
        """Provides a developer-friendly string representation of the game state."""
        return (f"GameState(Turn: {self.turn_number}, "
                f"Active Player: '{self.active_player.name if self.active_player else 'None'}')")