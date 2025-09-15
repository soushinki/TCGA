from framework.core.card import Card
from framework.simulation.simulator import GameSimulator
from agents.simple_ai_agent import SimpleAiAgent
from agents.human_agent import HumanAgent
from games.ruleset_one.engine import RuleSetOneEngine

def main():
    """
    Main function to configure and run the TCG simulation.
    """
    print("Initializing TCG Simulator...")

    # 1. Define the cards that will be used in the game
    attack_bot_card = Card(card_id="ATTACK_BOT", name="Attack Bot")
    draw_bot_card = Card(card_id="DRAW_BOT", name="Draw Bot")

    # 2. Build the decks for the players
    # --- DECK SIZE INCREASED HERE ---
    # We create larger decks to prevent players from running out of cards.
    deck1 = [Card(c.card_id, c.name) for c in [attack_bot_card]*10 + [draw_bot_card]*10]
    deck2 = [Card(c.card_id, c.name) for c in [attack_bot_card]*10 + [draw_bot_card]*10]

    # ... (The rest of the file is exactly the same)
    # 3. Create the agents that will play the game
    agent1 = SimpleAiAgent("AI Player Alice")
    agent2 = SimpleAiAgent("AI Player Bob")
    # agent1 = HumanAgent("Human Player") 
    
    agents = [agent1, agent2]

    # 4. Create the game engine with our custom rules
    game_engine = RuleSetOneEngine()

    # 5. Create the simulator with the engine and agents
    simulator = GameSimulator(game_engine=game_engine, agents=agents)
    
    # 6. Assign decks to the players in the game state
    simulator.game_state.players[0].setup_deck(deck1)
    simulator.game_state.players[1].setup_deck(deck2)

    # 7. Run the simulation!
    simulator.run()


if __name__ == "__main__":
    main()