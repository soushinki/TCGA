# filename: analyze_skill_keywords.py
import json
import os
import sys
from collections import Counter
import re

def analyze_skill_keywords():
    """
    Analyzes the 'skill' property in the slim card database to find
    and count unique keywords, assuming '//' and ',' as separators.
    """
    db_path = "games/sv/database"
    slim_filename = "all_sv_cards_slim.json"
    filepath = os.path.join(db_path, slim_filename)

    print(f"--- Analyzing Skill Keywords in '{filepath}' ---")

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            all_cards_data = json.load(f)
        print(f"Successfully loaded {len(all_cards_data)} cards.")

    except FileNotFoundError:
        print(f"FATAL ERROR: File not found at '{filepath}'.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"FATAL ERROR: Could not parse JSON. Details: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"FATAL ERROR: An unexpected error occurred. Details: {e}")
        sys.exit(1)

    if not isinstance(all_cards_data, list):
        print("FATAL ERROR: Expected JSON file to contain a list of cards.")
        sys.exit(1)

    keyword_counts = Counter()
    cards_with_skill = 0

    # Iterate through each card
    for card in all_cards_data:
        skill_value = card.get('skill')

        if isinstance(skill_value, str) and skill_value.strip() and skill_value != 'none':
            cards_with_skill += 1
            # Split by '//' first (handles unevo/evo separation)
            parts = skill_value.split('//')
            for part in parts:
                # Split each part by ',' to get individual keywords
                keywords = part.split(',')
                for keyword in keywords:
                    # Clean up the keyword (remove extra spaces)
                    cleaned_keyword = keyword.strip()
                    if cleaned_keyword: # Ensure it's not empty after stripping
                        keyword_counts[cleaned_keyword] += 1
        elif skill_value is not None and skill_value != 'none':
             print(f"Warning: Card ID {card.get('card_id')} has non-string/non-none skill value: {skill_value}")

    # Print the results
    print(f"\nProcessed 'skill' property for {cards_with_skill} cards with skills.")
    print("\n--- Unique Skill Keywords Found (Sorted by Frequency) ---")

    if not keyword_counts:
        print("No valid keywords found.")
    else:
        # Sort the keywords by count, descending
        for keyword, count in keyword_counts.most_common():
            print(f"  Keyword: '{keyword}' | Count: {count}")

    print(f"\nAnalysis complete. Found {len(keyword_counts)} unique keywords.")

# --- Execution ---
if __name__ == "__main__":
    try:
        analyze_skill_keywords()
    except Exception as e:
        print(f"An error occurred during execution: {e}")