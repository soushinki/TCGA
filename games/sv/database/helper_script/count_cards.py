import json
import os
import sys
from collections import defaultdict

def count_card_sets():
    """
    Loads the master card database, counts the number of cards per card_set_id,
    and verifies the total sum.
    """
    db_path = "games/sv/database"
    master_filename = "all_sv_cards.json"
    filepath = os.path.join(db_path, master_filename)

    print(f"--- Counting Cards by Set ID in '{master_filename}' ---")

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            all_cards_data = json.load(f)
    except FileNotFoundError:
        print(f"FATAL ERROR: Master file '{master_filename}' not found at '{filepath}'.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"FATAL ERROR: Could not parse JSON file. It may be corrupted. Details: {e}")
        sys.exit(1)
    
    if not isinstance(all_cards_data, list):
        print("FATAL ERROR: Expected JSON file to contain a list of cards.")
        sys.exit(1)

    set_counts = defaultdict(int)
    
    for card in all_cards_data:
        set_id = card.get('is_eight_one_zero_start_id')
        
        # --- FIX APPLIED HERE ---
        # We explicitly check for 'None' to ensure the number 0 is counted.
        if set_id is not None:
            set_counts[set_id] += 1
        else:
            print(f"Warning: Found a card with no 'card_set_id': {card.get('card_name', 'Unknown')}")

    total_sum_of_counts = sum(set_counts.values())

    print("\n--- Card Counts by Set ID ---")
    for set_id, count in sorted(set_counts.items()):
        print(f"  Set ID: {set_id:<15} | Card Count: {count}")
    
    print(f"\nTotal unique set IDs found: {len(set_counts)}")
    
    print("\n--- Verification ---")
    print(f"Sum of all card counts: {total_sum_of_counts}")
    print(f"Total length of cards array: {len(all_cards_data)}")
    
    if total_sum_of_counts == len(all_cards_data):
        print("✅ SUCCESS: The sum of counts matches the total array length.")
    else:
        print("❌ FAILURE: The sum of counts does NOT match the total array length.")

if __name__ == "__main__":
    count_card_sets()