import os
import shutil

from ..core.game_state import GameState

def clear_screen():
    """Clears the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

class Display:
    """
    Handles the visual presentation of the game state to the console.
    """
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

        # Opponent Info
        print(f"    {opponent.name:<25} Life: {opponent.life:<5} Deck: {len(opponent.deck):<5} Hand: {len(opponent.hand):<5} {opponent.resources}")
        print("-" * width)
        
        def format_board_card(card):
            """Helper to format a card on the board."""
            if card.get_property('type') == 'Follower':
                return f"[{card.name} ({card.get_property('atk')}/{card.get_property('def')})]"
            else: # Amulets
                return f"[{card.name}]"

        # Opponent's Board
        opponent_board_cards = opponent.board.get_cards()
        opponent_board_str = "    " + "   ".join([format_board_card(c) for c in opponent_board_cards])
        print(opponent_board_str if opponent_board_cards else "    (Board is empty)")
        print()

        # Player's Board
        player_board_cards = active_player.board.get_cards()
        player_board_str = "    " + "   ".join([format_board_card(c) for c in player_board_cards])
        print(player_board_str if player_board_cards else "    (Board is empty)")
        
        print("-" * width)
        
        # Player Info
        print(f"    {active_player.name:<25} Life: {active_player.life:<5} Deck: {len(active_player.deck):<5} Hand: {len(active_player.hand):<5} {active_player.resources}")
        print()

        # Display Player's Hand with Stats for Followers
        hand_cards = active_player.hand.get_cards()
        if hand_cards:
            hand_card_strings = []
            for card in hand_cards:
                cost = card.get_property('cost')
                name = card.name
                if card.get_property('type') == 'Follower':
                    atk = card.get_property('atk')
                    defs = card.get_property('def')
                    hand_card_strings.append(f"[{cost}PP {name} ({atk}/{defs})]")
                else: # Spells and Amulets
                    hand_card_strings.append(f"[{cost}PP {name}]")
            
            hand_str = "    " + "   ".join(hand_card_strings)
            print(hand_str)
        
        print() # Extra newline for spacing before the next prompt