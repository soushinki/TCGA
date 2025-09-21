import json
import os
from typing import Dict, Any

class CardDatabase:
    """
    Loads and provides access to card data from the JSON database.
    """
    def __init__(self, db_path: str):
        self.cards: Dict[str, Any] = self._load_db(db_path)
        print(f"Loaded {len(self.cards)} card definitions from the database.")

    def _load_db(self, db_path: str) -> Dict[str, Any]:
        """Loads the JSON file from the given path."""
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"Card database not found at: {db_path}")
        with open(db_path, 'r') as f:
            return json.load(f)

    def get_card_data(self, card_id: str) -> Dict[str, Any]:
        """Retrieves the data for a single card by its ID."""
        if card_id not in self.cards:
            raise KeyError(f"Card ID '{card_id}' not found in the database.")
        return self.cards[card_id]