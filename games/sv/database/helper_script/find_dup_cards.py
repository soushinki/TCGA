import json
import os
import sys
from collections import defaultdict

def verify_base_card_ids():
    """
    Analyzes the slim database to find cards sharing a base_card_id and
    verifies their card_name for consistency.
    """
    db_path = "games/sv/database"
    slim_filename = "all_sv_cards_slim.json"
    filepath = os.path.join(db_path, slim_filename)

    print(f"--- Verifying Base Card IDs in '{slim_filename}' ---")

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            all_cards_data = json.load(f)
    except FileNotFoundError:
        print(f"FATAL ERROR: Slim database '{slim_filename}' not found at '{filepath}'.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"FATAL ERROR: Could not parse JSON file. Details: {e}")
        sys.exit(1)

    # Group cards by their base_card_id
    base_id_groups = defaultdict(list)
    for card in all_cards_data:
        base_id = card.get('base_card_id')
        if base_id:
            base_id_groups[str(base_id)].append(card)

    print(f"Found {len(base_id_groups)} unique base_card_ids.")
    print("\n--- Analysis Report ---")

    shared_base_id_count = 0
    name_mismatches = 0

    # Analyze the groups
    for base_id, cards in base_id_groups.items():
        if len(cards) > 1:
            shared_base_id_count += 1
            
            # Check for name consistency within the group
            first_card_name = cards[0].get('card_name')
            all_names_match = all(c.get('card_name') == first_card_name for c in cards)
            
            card_ids = [str(c.get('card_id')) for c in cards]

            if all_names_match:
                print(f"\n✅ Base ID {base_id} is shared by {len(cards)} cards. All have the name '{first_card_name}'.")
                print(f"   - Card IDs: {', '.join(card_ids)}")
            else:
                name_mismatches += 1
                print(f"\n❌ Base ID {base_id} is shared by {len(cards)} cards, but their names DO NOT match.")
                for c in cards:
                    print(f"   - Card ID: {c.get('card_id')}, Name: '{c.get('card_name')}'")

    print("\n--- Summary ---")
    if shared_base_id_count == 0:
        print("No cards were found that share a base_card_id.")
    else:
        print(f"Found {shared_base_id_count} base_card_ids that are shared by multiple cards.")
        if name_mismatches == 0:
            print("✅ All shared groups have consistent card names.")
        else:
            print(f"❌ Found {name_mismatches} groups with inconsistent card names.")

if __name__ == "__main__":
    verify_base_card_ids()