import os
import json
from collections import Counter
from typing import List, Dict, Tuple

from ..database.db_loader import CardDatabase

class DeckValidator:
    """
    Validates a decklist against a given set of game rules.
    """
    def __init__(self, db: CardDatabase):
        self.db = db

    def validate(self, deck_card_ids: List[str]) -> Tuple[bool, str]:
        """
        Checks a list of card IDs against SV rules.

        Returns:
            A tuple containing (isValid, reasonStr).
        """
        # Rule 1: Deck Size
        if len(deck_card_ids) != 40:
            return False, f"Deck must contain exactly 40 cards, but it has {len(deck_card_ids)}."

        # Rule 2: Card Copies
        counts = Counter(deck_card_ids)
        for card_id, count in counts.items():
            if count > 3:
                card_name = self.db.get_card_data(card_id).get('name', card_id)
                return False, f"Deck contains {count} copies of '{card_name}'. Maximum is 3."

        # Rule 3: All card IDs must be valid
        for card_id in counts.keys():
            try:
                self.db.get_card_data(card_id)
            except KeyError:
                return False, f"Deck contains an invalid Card ID: '{card_id}'."

        return True, "Deck is valid."


class DeckLoader:
    """
    Loads and validates all deck files from a specified directory.
    """
    def __init__(self, deck_folder_path: str, validator: DeckValidator):
        self.deck_folder_path = deck_folder_path
        self.validator = validator
        self.valid_decks: Dict[str, List[str]] = self._load_decks()

    def _load_decks(self) -> Dict[str, List[str]]:
        """Scans the directory, validates, and loads all legal decks."""
        print("\n--- Loading Decks ---")
        loaded_decks = {}
        if not os.path.isdir(self.deck_folder_path):
            print(f"Warning: Deck directory not found at '{self.deck_folder_path}'")
            return loaded_decks
            
        for filename in os.listdir(self.deck_folder_path):
            if filename.endswith('.json'):
                deck_name = os.path.splitext(filename)[0]
                filepath = os.path.join(self.deck_folder_path, filename)
                with open(filepath, 'r') as f:
                    card_ids = json.load(f)
                
                is_valid, reason = self.validator.validate(card_ids)
                if is_valid:
                    print(f"  > '{deck_name}' loaded successfully.")
                    loaded_decks[deck_name] = card_ids
                else:
                    print(f"  > Skipped '{deck_name}': {reason}")
        
        print("--- Deck Loading Complete ---\n")
        return loaded_decks