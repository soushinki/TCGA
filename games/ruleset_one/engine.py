from typing import List, Optional

from framework.core.player import Player # Import Player
from framework.core.game_state import GameState
from framework.simulation.action import Action
from framework.simulation.base_game_engine import BaseGameEngine

class RuleSetOneEngine(BaseGameEngine):
    """
    ...
    """
    def setup_game(self, game_state: GameState):
        # ... (no changes here)
        for player in game_state.players:
            player.life = 10
            player.draw_card()
            player.draw_card()
            player.draw_card()
        print("RuleSetOneEngine: Game setup complete. Players have 10 life and 3 cards.")

    def get_possible_actions(self, game_state: GameState) -> List[Action]:
        # ... (no changes here)
        actions = []
        active_player = game_state.active_player
        for card in active_player.hand.get_cards():
            actions.append(Action(
                player_id=active_player.name,
                action_type="PLAY_CARD",
                details={"card_instance_id": card.instance_id}
            ))
        actions.append(Action(player_id=active_player.name, action_type="PASS_TURN"))
        return actions

    def apply_action(self, game_state: GameState, action: Action):
        # ... (no changes here)
        active_player = game_state.active_player
        if action.action_type == "PASS_TURN":
            print(f"{active_player.name} passes the turn.")
            return
        if action.action_type == "PLAY_CARD":
            card_instance_id = action.details["card_instance_id"]
            card_to_play = next((c for c in active_player.hand.get_cards() if c.instance_id == card_instance_id), None)
            if card_to_play:
                print(f"{active_player.name} plays {card_to_play.name}.")
                active_player.hand.remove(card_to_play)
                active_player.graveyard.add(card_to_play)
                if card_to_play.card_id == "ATTACK_BOT":
                    opponent = next(p for p in game_state.players if p is not active_player)
                    opponent.life -= 1
                    print(f"{card_to_play.name} deals 1 damage to {opponent.name}. {opponent.name} is at {opponent.life} life.")
                elif card_to_play.card_id == "DRAW_BOT":
                    active_player.draw_card()
                    print(f"{card_to_play.name} allows {active_player.name} to draw a card.")
            else:
                print(f"ERROR: Card with instance ID {card_instance_id} not found in hand.")

    # --- NEW METHOD IMPLEMENTED HERE ---
    def check_win_condition(self, game_state: GameState) -> Optional[Player]:
        """
        In RuleSetOne, a player wins if their opponent's life is 0 or less.
        """
        for player in game_state.players:
            # Find the opponent
            opponent = next(p for p in game_state.players if p is not player)
            if opponent.life <= 0:
                return player # This player is the winner
        return None # No winner yet