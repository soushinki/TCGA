from typing import List

from framework.core.game_state import GameState
from framework.simulation.action import Action
from framework.simulation.base_game_engine import BaseGameEngine

class RuleSetOneEngine(BaseGameEngine):
    """
    A concrete implementation of a GameEngine for a very simple TCG.
    This engine enforces the rules of our first simple game.
    """

    def setup_game(self, game_state: GameState):
        """
        Initializes the game: sets player life and has each player draw 3 cards.
        """
        for player in game_state.players:
            player.life = 10  # Set starting life
            player.draw_card()
            player.draw_card()
            player.draw_card()
        print("RuleSetOneEngine: Game setup complete. Players have 10 life and 3 cards.")

    def get_possible_actions(self, game_state: GameState) -> List[Action]:
        """
        Determines the possible actions for the active player.
        In this game, they can play any card from their hand, or pass.
        """
        actions = []
        active_player = game_state.active_player
        
        # Action to play each card in hand
        for card in active_player.hand.get_cards():
            actions.append(Action(
                player_id=active_player.name,
                action_type="PLAY_CARD",
                details={"card_instance_id": card.instance_id}
            ))
            
        # Action to pass the turn
        actions.append(Action(player_id=active_player.name, action_type="PASS_TURN"))
        
        return actions

    def apply_action(self, game_state: GameState, action: Action):
        """
        Applies an action and modifies the game state according to the rules.
        """
        active_player = game_state.active_player

        if action.action_type == "PASS_TURN":
            print(f"{active_player.name} passes the turn.")
            return

        if action.action_type == "PLAY_CARD":
            card_instance_id = action.details["card_instance_id"]
            
            # Find the card in the player's hand
            card_to_play = next((c for c in active_player.hand.get_cards() if c.instance_id == card_instance_id), None)
            
            if card_to_play:
                print(f"{active_player.name} plays {card_to_play.name}.")
                
                # Move card from hand to graveyard
                active_player.hand.remove(card_to_play)
                active_player.graveyard.add(card_to_play)

                # Apply the card's effect based on its card_id
                if card_to_play.card_id == "ATTACK_BOT":
                    # Find opponent (assumes a 2-player game for simplicity)
                    opponent = next(p for p in game_state.players if p is not active_player)
                    opponent.life -= 1
                    print(f"{card_to_play.name} deals 1 damage to {opponent.name}. {opponent.name} is at {opponent.life} life.")

                elif card_to_play.card_id == "DRAW_BOT":
                    active_player.draw_card()
                    print(f"{card_to_play.name} allows {active_player.name} to draw a card.")
            else:
                print(f"ERROR: Card with instance ID {card_instance_id} not found in hand.")