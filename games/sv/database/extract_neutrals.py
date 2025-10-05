import json
import os
import sys

def extract_neutral_cards():
    """
    Extracts neutral cards by finding the difference between a master
    card list and all class-specific card lists.
    """
    db_path = "games/sv/database"
    
    class_filenames = [
        "blood.json", "dragon.json", "forest.json", "haven.json",
        "portal.json", "rune.json", "shadow.json", "sword.json"
    ]
    
    master_filename = "all_sv_cards.json"
    output_filename = "neutral.json"

    print("--- Starting Neutral Card Extraction ---")

    class_card_ids = set()
    
    # 1. Collect all card IDs from class-specific files
    for filename in class_filenames:
        filepath = os.path.join(db_path, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for card in data:
                    if 'card_id' in card:
                        class_card_ids.add(str(card['card_id']))
        except FileNotFoundError:
            print(f"Warning: Class file not found, skipping: {filename}")
            continue
    
    print(f"Found {len(class_card_ids)} unique class-specific card IDs.")

    # 2. Read the master file and filter out class cards
    master_filepath = os.path.join(db_path, master_filename)
    neutral_cards = []
    
    try:
        with open(master_filepath, 'r', encoding='utf-8') as f:
            master_data = json.load(f)
        
        for card in master_data:
            if str(card.get('card_id')) not in class_card_ids:
                neutral_cards.append(card)
                
    except FileNotFoundError:
        print(f"FATAL ERROR: Master file '{master_filename}' not found.")
        sys.exit(1)
    
    print(f"Found {len(neutral_cards)} neutral cards to extract.")

    # 3. Save the filtered list to a new file
    output_filepath = os.path.join(db_path, output_filename)
    try:
        with open(output_filepath, 'w', encoding='utf-8') as f:
            json.dump(neutral_cards, f, indent=2, ensure_ascii=False)
        print(f"\n✅ SUCCESS: Saved {len(neutral_cards)} neutral cards to '{output_filepath}'.")
    except Exception as e:
        print(f"\n❌ ERROR: Could not write output file. Details: {e}")


if __name__ == "__main__":
    extract_neutral_cards()