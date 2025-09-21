import os
import json
from collections import Counter
from typing import List, Dict, Tuple, Any

from ..database.db_loader import CardDatabase

class DeckValidator:
    """
    Validates a decklist against a given set of game rules.
    """
    def __init__(self, db: CardDatabase):
        self.db = db

    def validate(self, deck_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Checks a deck data object against SV rules.
        """
        # --- LOGIC UPDATED TO USE THE DECK_DATA OBJECT ---
        deck_class = deck_data.get('class')
        card_ids = deck_data.get('cardIds', [])

        if not deck_class or not card_ids:
            return False, "Deck file is missing 'class' or 'cardIds' key."

        # Rule 1: Deck Size
        if len(card_ids) != 40:
            return False, f"Deck must contain 40 cards, but it has {len(card_ids)}."

        # Rule 2: Card Copies
        counts = Counter(card_ids)
        for card_id, count in counts.items():
            if count > 3:
                card_name = self.db.get_card_data(card_id).get('name', card_id)
                return False, f"Deck contains {count} copies of '{card_name}'. Max is 3."

        # Rule 3 & 4: Card Existence and Class Allegiance
        for card_id in counts.keys():
            try:
                card_data = self.db.get_card_data(card_id)
                card_class = card_data.get('class')
                if card_class not in [deck_class, 'Neutral']:
                    card_name = card_data.get('name', card_id)
                    return False, f"'{deck_class}' deck contains a '{card_class}' card: '{card_name}'."
            except KeyError:
                return False, f"Deck contains an invalid Card ID: '{card_id}'."

        return True, "Deck is valid."


class DeckLoader:
    """
    Loads and validates all deck files from a specified directory.
    """
    def __init__(self, deck_folder_path: str, db: CardDatabase):
        self.deck_folder_path = deck_folder_path
        self.validator = DeckValidator(db)
        self.valid_decks: Dict[str, Dict[str, Any]] = self._load_decks()

    def _load_decks(self) -> Dict[str, Dict[str, Any]]:
        """Scans the directory, validates, and loads all legal decks."""
        print("\n--- Loading Decks ---")
        loaded_decks = {}
        if not os.path.isdir(self.deck_folder_path):
            print(f"Warning: Deck directory not found at '{self.deck_folder_path}'")
            return loaded_decks
            
        for filename in os.listdir(self.deck_folder_path):
            if filename.endswith('.json'):
                filepath = os.path.join(self.deck_folder_path, filename)
                with open(filepath, 'r') as f:
                    deck_data = json.load(f)
                
                is_valid, reason = self.validator.validate(deck_data)
                deck_name = deck_data.get("deckName", filename)
                if is_valid:
                    print(f"  > '{deck_name}' ({deck_data.get('class')}) loaded successfully.")
                    # Use filename as the key, and store the whole data object
                    loaded_decks[filename] = deck_data
                else:
                    print(f"  > Skipped '{deck_name}': {reason}")
        
        print("--- Deck Loading Complete ---\n")
        return loaded_decks