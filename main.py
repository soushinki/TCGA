import argparse
import sys
import questionary

from framework.core.card import Card
from framework.simulation.simulator import GameSimulator
from agents.simple_ai_agent import SimpleAiAgent
from agents.human_agent import HumanAgent
from games.ruleset_one.engine import RuleSetOneEngine
from games.sv.engine import SvEngine
from games.sv.database.db_loader import CardDatabase
from games.sv.utils.deck_builder import DeckLoader, DeckValidator

def run_simulation(game_name: str, agent1_type: str, agent2_type: str, sv_mode: str = 'SV', **kwargs):
    """
    This is the core game launcher function. It sets up and runs a simulation
    based on the provided parameters.
    """
    print("\n" + "="*30)
    print(f"Setting up a new game: {game_name}")
    print("="*30)

    # 1. Create Agents
    agents = []
    agent_map = {'simple_ai': SimpleAiAgent, 'human': HumanAgent}
    agents.append(agent_map.get(agent1_type, SimpleAiAgent)(f"Player 1 ({agent1_type.upper()})"))
    agents.append(agent_map.get(agent2_type, SimpleAiAgent)(f"Player 2 ({agent2_type.upper()})"))

    # 2. Create Game Engine and Decks based on the chosen game
    # --- THIS 'IF' BLOCK IS NOW CORRECTLY FILLED ---
    if game_name == 'ruleset_one':
        game_engine = RuleSetOneEngine()
        attack_bot = Card(card_id="ATTACK_BOT", name="Attack Bot", properties={'cost': 1})
        draw_bot = Card(card_id="DRAW_BOT", name="Draw Bot", properties={'cost': 1})
        deck1 = [Card(c.card_id, c.name, c.properties) for c in [attack_bot]*10 + [draw_bot]*10]
        deck2 = [Card(c.card_id, c.name, c.properties) for c in [attack_bot]*10 + [draw_bot]*10]
    
    elif game_name == 'sv':
        game_engine = SvEngine(game_mode=sv_mode)
        deck1 = kwargs.get('deck1', [])
        deck2 = kwargs.get('deck2', [])

    else:
        print(f"Error: Unknown game '{game_name}'")
        return

    # 3. Create and run the simulator
    try:
        simulator = GameSimulator(game_engine=game_engine, agents=agents)
        simulator.game_state.players[0].setup_deck(deck1)
        simulator.game_state.players[1].setup_deck(deck2)
        simulator.run()
    except KeyboardInterrupt:
        print("\nSimulation interrupted by user. Exiting game.")


def show_sv_settings_menu():
    """Shows a wizard-style menu to configure a Shadowverse game."""
    print("\n--- Shadowverse Game Setup ---")
    
    try:
        db = CardDatabase('games/sv/database/cards.json')
        validator = DeckValidator(db)
        deck_loader = DeckLoader('games/sv/decks', validator)
        
        if not deck_loader.valid_decks:
            print("No valid decks found in 'games/sv/decks/'. Cannot start a game.")
            questionary.press_any_key_to_continue("Press any key to return to the main menu...").ask()
            return
            
        deck_choices = list(deck_loader.valid_decks.keys())
    except Exception as e:
        print(f"Error loading decks: {e}")
        return

    try:
        agent1 = questionary.select("Select Player 1's agent:", choices=["simple_ai", "human"]).ask()
        if agent1 is None: return

        deck1_name = questionary.select("Select Player 1's deck:", choices=deck_choices).ask()
        if deck1_name is None: return

        agent2 = questionary.select("Select Player 2's agent:", choices=["simple_ai", "human"]).ask()
        if agent2 is None: return
        
        deck2_name = questionary.select("Select Player 2's deck:", choices=deck_choices).ask()
        if deck2_name is None: return

        mode = questionary.select("Select Game Mode:", choices=["SV", "SVWB"]).ask()
        if mode is None: return

        confirm_message = (f"Start Simulation?\n"
                         f"  - P1: {agent1} ({deck1_name})\n"
                         f"  - P2: {agent2} ({deck2_name})\n"
                         f"  - Mode: {mode}")
        confirm = questionary.confirm(confirm_message).ask()
        if confirm is None: return
        
        if confirm:
            deck1_ids = deck_loader.valid_decks[deck1_name]
            deck2_ids = deck_loader.valid_decks[deck2_name]

            deck1 = [Card(card_id, db.get_card_data(card_id)['name'], db.get_card_data(card_id)) for card_id in deck1_ids]
            deck2 = [Card(card_id, db.get_card_data(card_id)['name'], db.get_card_data(card_id)) for card_id in deck2_ids]
            
            run_simulation('sv', agent1, agent2, mode, deck1=deck1, deck2=deck2)

    except KeyboardInterrupt:
        print("\nSetup cancelled.")


def show_main_menu():
    """Shows the main interactive menu to the user."""
    print("\nWelcome to the TCG Simulator!")
    
    while True:
        try:
            choice = questionary.select(
                "What would you like to do?",
                choices=[
                    "1. Run RuleSetOne (AI vs AI)",
                    "2. Configure a Shadowverse Game",
                    "Quit"
                ]
            ).ask()

            if choice is None or choice == "Quit":
                break

            elif choice == "1. Run RuleSetOne (AI vs AI)":
                # --- THIS LINE IS NOW CORRECTED ---
                run_simulation(game_name='ruleset_one', agent1_type='simple_ai', agent2_type='simple_ai')

            elif choice == "2. Configure a Shadowverse Game":
                show_sv_settings_menu()
                
        except KeyboardInterrupt:
            break
    
    print("\nThank you for using the TCG Simulator!")


def setup_arg_parser():
    # ... (this function is unchanged)
    parser = argparse.ArgumentParser(description="A flexible TCG Simulator.")
    parser.add_argument('--game', type=str, choices=['ruleset_one', 'sv'], 
                        help='The name of the game to run in headless mode.')
    parser.add_argument('--agent1', type=str, choices=['human', 'simple_ai'], default='simple_ai',
                        help='The agent type for Player 1.')
    parser.add_argument('--agent2', type=str, choices=['human', 'simple_ai'], default='simple_ai',
                        help='The agent type for Player 2.')
    parser.add_argument('--mode', type=str, choices=['SV', 'SVWB'], default='SV',
                        help='The game mode for Shadowverse (SV or SVWB).')
    return parser


if __name__ == "__main__":
    parser = setup_arg_parser()
    args = parser.parse_args()

    if args.game:
        # In headless mode, we need to manually load decks for SV
        kwargs = {}
        if args.game == 'sv':
            db = CardDatabase('games/sv/database/cards.json')
            validator = DeckValidator(db)
            deck_loader = DeckLoader('games/sv/decks', validator)
            
            if not deck_loader.valid_decks:
                print("Error: No valid decks found for SV headless mode.")
                sys.exit(1)
            
            # Just grab the first valid deck for both players
            deck_name = list(deck_loader.valid_decks.keys())[0]
            deck_ids = deck_loader.valid_decks[deck_name]
            deck = [Card(card_id, db.get_card_data(card_id)['name'], db.get_card_data(card_id)) for card_id in deck_ids]
            kwargs['deck1'] = deck
            kwargs['deck2'] = deck

        run_simulation(args.game, args.agent1, args.agent2, args.mode, **kwargs)
    else:
        show_main_menu()