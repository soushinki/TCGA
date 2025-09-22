from lupa import LuaRuntime
from typing import Any

from ..core.card import Card
from ..core.game_state import GameState

class LuaEngine:
    """
    A wrapper for the Lua runtime. It loads, executes, and provides a Python API
    to Lua scripts. This is the bridge between Python and Lua.
    """
    def __init__(self, script_api: Any):
        """
        Initializes the Lua runtime and injects the Python ScriptAPI.
        """
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        # Inject the Python API object into the Lua global namespace.
        # Lua scripts can now call Python functions via `api.function_name()`.
        self.lua.globals().api = script_api
        print("Lua Engine Initialized.")

    def run_script(self, script_path: str, function_name: str, card: Card, game_state: GameState):
        """
        Loads a script from a file and executes a specific function within it.

        Args:
            script_path (str): The full path to the .lua script.
            function_name (str): The name of the function to call inside the script.
            card (Card): The card object associated with this effect.
            game_state (GameState): The current state of the game.
        """
        try:
            with open(script_path, 'r') as f:
                lua_code = f.read()
            
            # Create a Lua function from the code string.
            # We pass `self` (the card) and `game_state` as arguments to the Lua function.
            lua_function = self.lua.eval(f'function(self, game_state) {lua_code} return {function_name}(self, game_state) end')
            
            # Execute the function
            lua_function(card, game_state)

        except FileNotFoundError:
            # It is perfectly normal for a card to have no script (e.g., a vanilla follower).
            # We can silently ignore this.
            pass
        except Exception as e:
            # Catch other potential Lua errors (e.g., syntax errors in the .lua file).
            print(f"!!! LUA ERROR in '{script_path}' -> {function_name}: {e}")