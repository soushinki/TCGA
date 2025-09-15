import argparse
import sys

# Third-party library for interactive menus
import questionary

# Import all our necessary game components
from framework.core.card import Card
from framework.simulation.simulator import GameSimulator
from agents.simple_ai_agent import SimpleAiAgent
from agents.human_agent import HumanAgent
from games.ruleset_one.engine import RuleSetOneEngine
from games.sv.engine import SvEngine

def run_simulation(game_name: str, agent1_type: str, agent2_type: str, sv_mode: str = 'SV'):
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
    if game_name == 'ruleset_one':
        game_engine = RuleSetOneEngine()
        attack_bot = Card(card_id="ATTACK_BOT", name="Attack Bot", properties={'cost': 1})
        draw_bot = Card(card_id="DRAW_BOT", name="Draw Bot", properties={'cost': 1})
        deck1 = [Card(c.card_id, c.name, c.properties) for c in [attack_bot]*10 + [draw_bot]*10]
        deck2 = [Card(c.card_id, c.name, c.properties) for c in [attack_bot]*10 + [draw_bot]*10]
    
    elif game_name == 'sv':
        game_engine = SvEngine(game_mode=sv_mode)
        # TODO: Create a real card database and deck building logic for Shadowverse
        print("!!! WARNING: Using placeholder decks for Shadowverse !!!")
        placeholder_card = Card(card_id="placeholder", name="Placeholder", properties={'cost': 1})
        deck1 = [Card(c.card_id, c.name, c.properties) for c in [placeholder_card]*40]
        deck2 = [Card(c.card_id, c.name, c.properties) for c in [placeholder_card]*40]

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
        agent1 = questionary.select(
            "Select Player 1's agent:",
            choices=["simple_ai", "human"]
        ).ask()
        if agent1 is None: return # User pressed Ctrl+C

        agent2 = questionary.select(
            "Select Player 2's agent:",
            choices=["simple_ai", "human"]
        ).ask()
        if agent2 is None: return

        mode = questionary.select(
            "Select Game Mode:",
            choices=["SV", "SVWB"]
        ).ask()
        if mode is None: return

        confirm = questionary.confirm(
            f"Start Simulation? (P1: {agent1}, P2: {agent2}, Mode: {mode})"
        ).ask()
        if confirm is None: return
        
        if confirm:
            run_simulation('sv', agent1, agent2, mode)

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
                break # Exit loop if user presses Ctrl+C or selects Quit

            elif choice == "1. Run RuleSetOne (AI vs AI)":
                run_simulation('ruleset_one', 'simple_ai', 'simple_ai')

            elif choice == "2. Configure a Shadowverse Game":
                show_sv_settings_menu()
                
        except KeyboardInterrupt:
            break # Exit loop if user presses Ctrl+C
    
    print("\nThank you for using the TCG Simulator!")


def setup_arg_parser():
    """Sets up the command-line argument parser."""
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

    # If the --game argument is provided, run in headless mode.
    # Otherwise, run in interactive mode.
    if args.game:
        run_simulation(args.game, args.agent1, args.agent2, args.mode)
    else:
        show_main_menu()