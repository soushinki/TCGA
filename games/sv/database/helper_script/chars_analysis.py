# filename: analyze_skill_chars_local.py
import json
import os
import sys
from collections import defaultdict
import string

def analyze_skill_chars_local():
    """
    Analyzes the 'skill' property in the local card database file
    to find unique non-alphanumeric characters (excluding space) and lists
    card IDs for specific characters.
    """
    db_path = "games/sv/database"
    slim_filename = "all_sv_cards_slim.json"
    filepath = os.path.join(db_path, slim_filename)

    print(f"--- Analyzing Special Characters in 'skill' Property of '{filepath}' ---")

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            all_cards_data = json.load(f)
        print(f"Successfully loaded {len(all_cards_data)} cards from local file.")

    except FileNotFoundError:
        print(f"FATAL ERROR: File not found at '{filepath}'. Make sure the script is run from the 'tcg_simulator' root directory.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"FATAL ERROR: Could not parse JSON file. It may be corrupted. Details: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"FATAL ERROR: An unexpected error occurred. Details: {e}")
        sys.exit(1)

    if not isinstance(all_cards_data, list):
        print("FATAL ERROR: Expected JSON file to contain a list of cards.")
        sys.exit(1)

    # Define allowed characters: letters, digits, and space
    allowed_chars = set(string.ascii_letters + string.digits + ' ')

    # --- Setup for tracking ---
    special_char_counts = defaultdict(int) # Counts for ALL special chars
    # Dictionary to store card IDs for SPECIFIC special chars: {char: [id1, id2...]}
    cards_with_target_chars = defaultdict(list)
    # Define the specific characters to track card IDs for
    target_special_chars = set(['+', '-', '.', '=', '@', '{', '}'])
    cards_processed = 0

    # --- Iterate and analyze ---
    for card in all_cards_data:
        skill_value = card.get('skill')
        card_id = str(card.get('card_id', 'UnknownID')) # Get card ID as string

        if isinstance(skill_value, str):
            cards_processed += 1
            found_target_char_in_card = False # Track if this card had a target char
            unique_target_chars_in_skill = set() # Track unique target chars in this skill string

            for char in skill_value:
                if char not in allowed_chars:
                    special_char_counts[char] += 1
                    # Check if it's one of the specific chars we want IDs for
                    if char in target_special_chars:
                         unique_target_chars_in_skill.add(char)
                         found_target_char_in_card = True # Not strictly needed with the set, but clearer

            # If any target char was found in this skill, add card ID to respective lists
            for char in unique_target_chars_in_skill:
                 cards_with_target_chars[char].append(card_id)

        elif skill_value is not None:
             pass # Silently ignore non-string skill values

    # --- Print the results ---
    print(f"\nProcessed 'skill' property for {cards_processed} cards.")

    # Section 1: Counts of ALL unique special characters
    print("\n--- Unique Non-Alphanumeric Characters Found in 'skill' (Counts) ---")
    if not special_char_counts:
        print("No special characters (excluding space) found in the 'skill' property.")
    else:
        for char, count in sorted(special_char_counts.items()):
            display_char = repr(char).strip("'")
            print(f"  Character: '{display_char}' | Count: {count}")

    # Section 2: Card IDs for TARGET special characters
    print("\n--- Card IDs Containing Specific Special Characters ---")
    found_any_target = False
    for char in sorted(list(target_special_chars)): # Iterate through target chars for consistent order
        if char in cards_with_target_chars:
            found_any_target = True
            display_char = repr(char).strip("'")
            card_ids = sorted(cards_with_target_chars[char]) # Sort IDs for readability
            print(f"\nCharacter: '{display_char}' (Found in {len(card_ids)} cards)")
            # Limit printed IDs if the list is very long
            id_limit = 20
            if len(card_ids) > id_limit:
                 print(f"  Card IDs: {', '.join(card_ids[:id_limit])} ... (and {len(card_ids) - id_limit} more)")
            else:
                 print(f"  Card IDs: {', '.join(card_ids)}")
        # Optionally print if a target character was NOT found
        # else:
        #    print(f"\nCharacter: '{repr(char).strip(\"'\")}' (Found in 0 cards)")

    if not found_any_target:
        print("None of the target special characters were found.")

    print(f"\nAnalysis complete.")

# --- Execution ---
if __name__ == "__main__":
    try:
        analyze_skill_chars_local()
    except Exception as e:
        print(f"An error occurred during execution: {e}")