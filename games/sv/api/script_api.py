from ....framework.core.player import Player

class ScriptAPI:
    """
    Defines the set of functions that Lua scripts are allowed to call.
    This is the "sandbox" for our card effect logic.
    """
    def __init__(self, engine: 'SvEngine'):
        """
        Initializes the API with a reference to the main game engine
        to allow it to modify the game state.
        """
        self.engine = engine

    def draw_card(self, player: Player, count: int):
        """
        Instructs a player to draw a specified number of cards.

        Args:
            player (Player): The Player object who should draw.
            count (int): The number of cards to draw.
        """
        print(f"--- API CALL: {player.name} draws {count} card(s). ---")
        for _ in range(count):
            player.draw_card()