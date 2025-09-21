from framework.core.card import Card
from framework.simulation.simulator import GameSimulator
from agents.simple_ai_agent import SimpleAiAgent
from games.ruleset_one.engine import RuleSetOneEngine

def launch():
    """
    Sets up and runs a default simulation for RuleSetOne.
    """
    print("\n" + "="*30)
    print("Setting up a new game: RuleSetOne")
    print("="*30)

    try:
        # 1. Create Agents
        agent1 = SimpleAiAgent("AI Player Alice")
        agent2 = SimpleAiAgent("AI Player Bob")
        agents = [agent1, agent2]

        # 2. Create Game Engine and Decks
        game_engine = RuleSetOneEngine()
        attack_bot = Card(card_id="ATTACK_BOT", name="Attack Bot", properties={'cost': 1})
        draw_bot = Card(card_id="DRAW_BOT", name="Draw Bot", properties={'cost': 1})
        deck1 = [Card(c.card_id, c.name, c.properties) for c in [attack_bot]*10 + [draw_bot]*10]
        deck2 = [Card(c.card_id, c.name, c.properties) for c in [attack_bot]*10 + [draw_bot]*10]

        # 3. Create and run the simulator
        simulator = GameSimulator(game_engine=game_engine, agents=agents)
        simulator.game_state.players[0].setup_deck(deck1)
        simulator.game_state.players[1].setup_deck(deck2)
        simulator.run()

    except KeyboardInterrupt:
        print("\nSimulation interrupted by user.")
    except Exception as e:
        print(f"\nAn error occurred during simulation setup: {e}")