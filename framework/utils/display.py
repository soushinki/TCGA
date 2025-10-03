import os
import shutil

from ..core.game_state import GameState
from ..core.card import Card # Import Card for type hinting

def clear_screen():
    """Clears the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

class Display:
    """
    Handles the visual presentation of the game state to the console.
    """
    def _format_board_card(self, card: Card) -> str:
        """Helper to format a card on the board."""
        if card.get_property('type') == 'Follower':
            return f"[{card.name} ({card.get_property('atk')}/{card.get_property('def')})]"
        else: # Amulets
            return f"[{card.name}]"

    def display_board(self, game_state: GameState):
        """
        Clears the screen and prints the full "pretty" board state.
        """
        clear_screen()
        
        active_player = game_state.active_player
        opponent = next(p for p in game_state.players if p is not active_player)
        width = shutil.get_terminal_size((80, 20)).columns
        
        print("=" * width)
        print(f"TURN {game_state.turn_number} - {active_player.name}".center(width))
        print("=" * width)
        print()

        print(f"    {opponent.name:<25} Life: {opponent.life:<5} Deck: {len(opponent.deck):<5} Hand: {len(opponent.hand):<5} {opponent.resources}")
        print("-" * width)
        
        opponent_board_cards = opponent.board.get_cards()
        opponent_board_str = "    " + "   ".join([self._format_board_card(c) for c in opponent_board_cards])
        print(opponent_board_str if opponent_board_cards else "    (Board is empty)")
        print()

        player_board_cards = active_player.board.get_cards()
        player_board_str = "    " + "   ".join([self._format_board_card(c) for c in player_board_cards])
        print(player_board_str if player_board_cards else "    (Board is empty)")
        
        print("-" * width)
        
        print(f"    {active_player.name:<25} Life: {active_player.life:<5} Deck: {len(active_player.deck):<5} Hand: {len(active_player.hand):<5} {active_player.resources}")
        print()

        hand_cards = active_player.hand.get_cards()
        if hand_cards:
            hand_card_strings = []
            for card in hand_cards:
                cost, name = card.get_property('cost'), card.name
                if card.get_property('type') == 'Follower':
                    atk, defs = card.get_property('atk'), card.get_property('def')
                    hand_card_strings.append(f"[{cost}PP {name} ({atk}/{defs})]")
                else:
                    hand_card_strings.append(f"[{cost}PP {name}]")
            
            hand_str = "    " + "   ".join(hand_card_strings)
            print(hand_str)
        
        print()

    def display_turn_summary(self, game_state: GameState):
        """
        Prints a consolidated summary at the start of a turn for the 'simple' log.
        """
        active_player = game_state.active_player
        opponent = next(p for p in game_state.players if p is not active_player)

        print(f"\n--- Turn {game_state.turn_number}: {active_player.name} ---")
        
        print(f"    {opponent.name}: Life: {opponent.life}, Deck: {len(opponent.deck)}, Hand: {len(opponent.hand)}, {opponent.resources}")
        opponent_board_cards = opponent.board.get_cards()
        opponent_board_str = "    " + "   ".join([self._format_board_card(c) for c in opponent_board_cards])
        print(opponent_board_str if opponent_board_cards else "    (Board is empty)")
        print()

        player_board_cards = active_player.board.get_cards()
        player_board_str = "    " + "   ".join([self._format_board_card(c) for c in player_board_cards])
        print(player_board_str if player_board_cards else "    (Board is empty)")
        print(f"    {active_player.name}: Life: {active_player.life}, Deck: {len(active_player.deck)}, Hand: {len(active_player.hand)}, {active_player.resources}")
        
        hand_cards = active_player.hand.get_cards()
        if hand_cards:
            hand_card_strings = []
            for card in hand_cards:
                cost, name = card.get_property('cost'), card.name
                if card.get_property('type') == 'Follower':
                    atk, defs = card.get_property('atk'), card.get_property('def')
                    hand_card_strings.append(f"[{cost}PP {name} ({atk}/{defs})]")
                else:
                    hand_card_strings.append(f"[{cost}PP {name}]")
            
            hand_str = "    " + "   ".join(hand_card_strings)
            print(hand_str)