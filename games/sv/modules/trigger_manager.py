# --- IMPORTS CORRECTED HERE ---
from framework.core.card import Card
from framework.scripting.lua_engine import LuaEngine

# Forward reference to avoid circular import with SvEngine
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..engine import SvEngine

class TriggerManager:
    """
    Listens for game events and triggers appropriate card effects via the Lua engine.
    """
    def __init__(self, engine: 'SvEngine'):
        self.engine = engine
        self.lua_engine: LuaEngine = engine.lua_engine

    def post_event(self, event_type: str, **kwargs):
        """
        The main entry point for an event. The SvEngine calls this method
        when something happens in the game.
        """
        if event_type == "on_play":
            card: Card = kwargs.get("card")
            if "Fanfare" in card.get_property("effect_text", ""):
                print(f"--- TriggerManager: Detected Fanfare for {card.name}. Running script. ---")
                self._run_card_script(card, "on_fanfare")
        
        # We can add a new event for when a follower is destroyed
        elif event_type == "on_destroy":
            card: Card = kwargs.get("card")
            if "Last Words" in card.get_property("effect_text", ""):
                print(f"--- TriggerManager: Detected Last Words for {card.name}. Running script. ---")
                self._run_card_script(card, "on_last_words")


    def _run_card_script(self, card: Card, function_name: str):
        """Helper to find the correct script path and execute it."""
        script_path = f"games/sv/scripts/{card.card_id}.lua"
        # The card and game_state are now passed from the engine to the run_script method
        self.lua_engine.run_script(script_path, function_name, card, self.engine.game_state)