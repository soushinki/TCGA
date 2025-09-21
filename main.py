import argparse
import sys
import questionary

# Import the launcher functions
from launchers import ruleset_one_launcher
from launchers import sv_launcher
# --- NEW IMPORT ---
from launchers import svwb_launcher

def show_main_menu():
    """Shows the main interactive menu to the user."""
    print("\nWelcome to the TCG Simulator!")
    
    while True:
        try:
            choice = questionary.select(
                "What would you like to do?",
                choices=[
                    "1. Run RuleSetOne (AI vs AI)",
                    "2. Configure a Shadowverse Game (Classic)",
                    # --- NEW MENU OPTION ---
                    "3. Configure a Shadowverse: Worlds Beyond Game",
                    "Quit"
                ]
            ).ask()

            if choice is None or choice == "Quit":
                break

            elif choice == "1. Run RuleSetOne (AI vs AI)":
                ruleset_one_launcher.launch()

            elif choice == "2. Configure a Shadowverse Game (Classic)":
                sv_launcher.launch()
            
            # --- NEW MENU LOGIC ---
            elif choice == "3. Configure a Shadowverse: Worlds Beyond Game":
                svwb_launcher.launch()
                
        except KeyboardInterrupt:
            break
    
    print("\nThank you for using the TG Simulator!")


def setup_arg_parser():
    """Sets up the command-line argument parser for headless mode."""
    # ... (this function is unchanged)
    parser = argparse.ArgumentParser(description="A flexible TCG Simulator.")
    parser.add_argument('--game', type=str, choices=['ruleset_one'], 
                        help='The name of the game to run in headless mode.')
    return parser


if __name__ == "__main__":
    # ... (this function is unchanged)
    parser = setup_arg_parser()
    args = parser.parse_args()

    if args.game:
        if args.game == 'ruleset_one':
            ruleset_one_launcher.launch()
    else:
        show_main_menu()