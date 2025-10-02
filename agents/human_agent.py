import sys
from typing import List, Dict
import questionary
from questionary import Choice, Separator

from framework.core.game_state import GameState
from framework.core.card import Card
from framework.simulation.action import Action
from .base_agent import BaseAgent

class HumanAgent(BaseAgent):
    """
    An agent that provides a multi-level, interactive menu system for a human
    player to make decisions via the command line.
    """

    def _select_from_menu(self, message: str, choices: List):
        """A helper function to run a questionary prompt and handle cancellation."""
        if not choices:
            return None
        
        # Add the global quit option to every menu
        choices.append(Separator())
        choices.append(Choice(title="Quit to Main Menu", value="quit_to_menu"))
        
        try:
            return questionary.select(message, choices=choices, use_indicator=True).ask()
        except KeyboardInterrupt:
            # Catch Ctrl+C and treat it as a hard exit
            print("\n\nExiting application...")
            sys.exit()

    def _select_card_to_play(self, actions: List[Action], game_state: GameState):
        """Shows a sub-menu to select a specific card to play."""
        choices = [
            Choice(title=action.to_repr(game_state), value=action) 
            for action in actions
        ]
        choices.append(Separator())
        choices.append(Choice(title="Back", value="back"))
        
        return self._select_from_menu("Select a card to play:", choices)

    def _select_evolve_target(self, actions: List[Action], game_state: GameState):
        """Shows a sub-menu to select a specific follower to evolve."""
        choices = [
            Choice(title=action.to_repr(game_state), value=action) 
            for action in actions
        ]
        choices.append(Separator())
        choices.append(Choice(title="Back", value="back"))

        return self._select_from_menu("Select a follower to evolve:", choices)

    def _select_attack(self, actions: List[Action], game_state: GameState):
        """Guides the user through a multi-step attack selection process."""
        # 1. Select an attacker
        attackers: Dict[str, Card] = {}
        for action in actions:
            attacker_id = action.details['attacker_id']
            if attacker_id not in attackers:
                card = next((c for c in game_state.active_player.board.get_cards() if c.instance_id == attacker_id), None)
                if card: attackers[attacker_id] = card
        
        attacker_choices = [
            Choice(title=f"{card.name} ({card.get_property('atk')}/{card.get_property('def')})", value=card)
            for card in attackers.values()
        ]
        attacker_choices.append(Separator())
        attacker_choices.append(Choice(title="Back", value="back"))

        chosen_attacker = self._select_from_menu("Select an attacker:", attacker_choices)
        if chosen_attacker is None or chosen_attacker in ["back", "quit_to_menu"]:
            return chosen_attacker

        # 2. Select a target for the chosen attacker
        target_actions = [action for action in actions if action.details['attacker_id'] == chosen_attacker.instance_id]
        target_choices = [
            Choice(title=action.to_repr(game_state), value=action)
            for action in target_actions
        ]
        target_choices.append(Separator())
        target_choices.append(Choice(title="Back", value="back"))
        
        return self._select_from_menu(f"Select a target for {chosen_attacker.name}:", target_choices)


    def choose_action(self, game_state: GameState, possible_actions: List[Action]) -> Action:
        """
        Presents a hierarchical menu system to the user to choose an action.
        """
        while True: # Main menu loop
            # 1. Categorize all possible actions
            play_actions = [a for a in possible_actions if a.action_type == "PLAY_CARD"]
            attack_actions = [a for a in possible_actions if a.action_type == "ATTACK"]
            evolve_actions = [a for a in possible_actions if a.action_type == "EVOLVE"]
            end_turn_action = next((a for a in possible_actions if a.action_type == "END_TURN"), None)

            # 2. Dynamically build the main menu choices
            main_menu_choices = []
            if end_turn_action:
                main_menu_choices.append(Choice(title="0. End Turn", value="END_TURN"))
            if play_actions:
                main_menu_choices.append(Choice(title="1. Play Card", value="PLAY"))
            if attack_actions:
                main_menu_choices.append(Choice(title="2. Attack", value="ATTACK"))
            if evolve_actions:
                main_menu_choices.append(Choice(title="3. Evolve", value="EVOLVE"))

            # 3. Show the main menu
            choice = self._select_from_menu("Choose an action:", main_menu_choices)

            if choice is None or choice == "quit_to_menu":
                return "quit_to_menu"
            
            # 4. Handle the choice and navigate to sub-menus
            action_to_return = None
            if choice == "END_TURN":
                return end_turn_action
            
            elif choice == "PLAY":
                action_to_return = self._select_card_to_play(play_actions, game_state)
            
            elif choice == "ATTACK":
                action_to_return = self._select_attack(attack_actions, game_state)
            
            elif choice == "EVOLVE":
                action_to_return = self._select_evolve_target(evolve_actions, game_state)
            
            if action_to_return == "quit_to_menu":
                return "quit_to_menu"

            if action_to_return and action_to_return != "back":
                return action_to_return
            # If the sub-menu returned "back" or None, the loop will repeat and show the main menu.