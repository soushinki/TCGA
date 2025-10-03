import questionary
from questionary import Choice
import copy

from framework.core.card import Card
from framework.simulation.simulator import GameSimulator
from agents.simple_ai_agent import SimpleAiAgent
from agents.human_agent import HumanAgent
from games.sv.engine import SvEngine
from games.sv.database.db_loader import CardDatabase
from games.sv.utils.deck_builder import DeckLoader

def launch():
    """
    Shows a wizard-style menu to configure and launch a Shadowverse: Worlds Beyond game.
    """
    print("\n--- Shadowverse: Worlds Beyond Game Setup ---")
    
    # This launcher is hard-coded to the 'SVWB' game mode.
    game_mode = 'SVWB'

    # 1. Load the database and all valid decks
    try:
        db = CardDatabase('games/sv/database/cards.json')
        deck_loader = DeckLoader('games/sv/decks', db)
        
        if not deck_loader.valid_decks:
            print("No valid decks found in 'games/sv/decks/'.")
            questionary.press_any_key_to_continue("Press any key to return...").ask()
            return

        deck_choices = [
            Choice(
                title=f"{data['deckName']} ({data['class']})", 
                value=filename
            ) for filename, data in deck_loader.valid_decks.items()
        ]
            
    except Exception as e:
        print(f"Error loading game data: {e}")
        return

    # 2. Ask user for configuration
    try:
        agent1_type = questionary.select("Select Player 1's agent:", choices=["simple_ai", "human"]).ask()
        if agent1_type is None: return

        deck1_filename = questionary.select("Select Player 1's deck:", choices=deck_choices).ask()
        if deck1_filename is None: return

        agent2_type = questionary.select("Select Player 2's agent:", choices=["simple_ai", "human"]).ask()
        if agent2_type is None: return
        
        deck2_filename = questionary.select("Select Player 2's deck:", choices=deck_choices).ask()
        if deck2_filename is None: return

        # 3. Confirmation
        deck1_data = deck_loader.valid_decks[deck1_filename]
        deck2_data = deck_loader.valid_decks[deck2_filename]
        confirm_message = (f"Start Simulation?\n"
                         f"  - P1: {agent1_type} ({deck1_data['deckName']})\n"
                         f"  - P2: {agent2_type} ({deck2_data['deckName']})\n"
                         f"  - Mode: {game_mode}") # Display the mode
        confirm = questionary.confirm(confirm_message).ask()
        if confirm is None: return
        
        if confirm:
            # 4. Build the final decks of Card objects and run simulation
            deck1_ids = deck1_data['cardIds']
            deck2_ids = deck2_data['cardIds']
            deck1 = [Card(card_id, db.get_card_data(card_id)['name'], copy.deepcopy(db.get_card_data(card_id))) for card_id in deck1_ids]
            deck2 = [Card(card_id, db.get_card_data(card_id)['name'], copy.deepcopy(db.get_card_data(card_id))) for card_id in deck2_ids]
        
            agent_map = {'simple_ai': SimpleAiAgent, 'human': HumanAgent}
            agents = [
                agent_map[agent1_type](f"Player 1 ({agent1_type.upper()})"),
                agent_map[agent2_type](f"Player 2 ({agent2_type.upper()})")
            ]
            game_engine = SvEngine(game_mode=game_mode)
            simulator = GameSimulator(game_engine=game_engine, agents=agents)
            simulator.game_state.players[0].setup_deck(deck1)
            simulator.game_state.players[1].setup_deck(deck2)
            simulator.run()

    except KeyboardInterrupt:
        print("\nSetup cancelled.")