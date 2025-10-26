# filename: parse_skill_field_tokens_v4.py
import json
import os
import sys
import re
from collections import Counter

# --- Configuration ---
# Change this to analyze 'skill', 'skill_target', 'skill_option', 'skill_preprocess'
FIELD_TO_ANALYZE = "skill_condition"
# --- End Configuration ---

def is_numeric(token):
    """Checks if a token represents a plain integer or float."""
    return re.fullmatch(r'-?\d+(\.\d+)?', token) is not None

def tokenize_detail_string(detail_str):
    """
    Tokenizes a complex detail string using regex.
    Extracts keywords (alphanumeric + _), numbers.
    For dynamic expressions ({...}), extracts keywords *within* them.
    Ignores common separators (=, &, <, >, etc.) outside brackets.
    """
    if not detail_str or detail_str.lower() == 'none':
        # Return 'none' as a token if that's the input
        return ['none'] if detail_str and detail_str.lower() == 'none' else []

    # Regex to find:
    # 1. Dynamic expressions: {[^{}]+} (Captures content inside {})
    # 2. Keywords outside braces: \b[a-zA-Z_][a-zA-Z0-9_]*\b
    # 3. Numbers outside braces: -?\d+(?:\.\d+)?
    # We prioritize finding the {} block first.
    token_pattern = re.compile(r"({[^{}]+})|(\b[a-zA-Z_][a-zA-Z0-9_]*\b)|(-?\d+(?:\.\d+)?)")

    # Regex to extract keywords *within* the braces
    inner_keyword_pattern = re.compile(r"\b[a-zA-Z_][a-zA-Z0-9_]*\b")

    initial_tokens = token_pattern.findall(detail_str)
    final_leaf_tokens = []

    for match in initial_tokens:
        brace_content, keyword, number = match # Unpack the tuple from findall

        if brace_content: # It's a {...} block
            # Extract content inside braces
            inner_content = brace_content[1:-1]
            # Find all keywords within the inner content
            inner_keywords = inner_keyword_pattern.findall(inner_content)
            final_leaf_tokens.extend(inner_keywords)
        elif keyword: # It's a keyword outside braces
            final_leaf_tokens.append(keyword)
        elif number: # It's a number outside braces
             final_leaf_tokens.append(number)
        # Separators outside braces are implicitly ignored as they don't match

    # Filter out any potential empty strings again just in case
    return [token for token in final_leaf_tokens if token]


def parse_field_hierarchically(raw_field_string):
    """
    Parses the raw skill field string into a list of leaf tokens.
    Handles '//' for evolution split and ',' for effect split.
    Calls tokenize_detail_string for the lowest level tokenization.
    """
    if not isinstance(raw_field_string, str) or not raw_field_string.strip():
        return []

    all_leaf_tokens = []
    unevolved_part_str = raw_field_string
    evolved_part_str = None

    if '//' in raw_field_string:
        parts = raw_field_string.split('//', 1)
        unevolved_part_str = parts[0]
        evolved_part_str = parts[1] if len(parts) > 1 else None

    # Process unevolved part
    if unevolved_part_str:
        effect_strings = unevolved_part_str.split(',')
        for effect_str in effect_strings:
            all_leaf_tokens.extend(tokenize_detail_string(effect_str.strip()))

    # Process evolved part
    if evolved_part_str:
        effect_strings = evolved_part_str.split(',')
        for effect_str in effect_strings:
            all_leaf_tokens.extend(tokenize_detail_string(effect_str.strip()))

    return all_leaf_tokens


def analyze_field_tokens():
    """
    Main function to load data, parse the specified skill field for all cards,
    and report statistics on the non-numeric leaf tokens found, including
    tokens extracted from within {...} blocks.
    """
    db_path = "games/sv/database"
    slim_filename = "all_sv_cards_slim.json" # Make sure this file exists
    filepath = os.path.join(db_path, slim_filename)

    print(f"--- Analyzing Non-Numeric Leaf Tokens in '{FIELD_TO_ANALYZE}' Field of '{filepath}' ---")

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            all_cards_data = json.load(f)
        print(f"Successfully loaded {len(all_cards_data)} cards.")
    except Exception as e:
        print(f"FATAL ERROR loading/parsing JSON: {e}")
        sys.exit(1)

    all_tokens_counter = Counter() # To count all leaf tokens initially
    cards_processed = 0
    cards_failed = 0

    for card in all_cards_data:
        card_id = card.get('card_id', 'UnknownID')
        field_string = card.get(FIELD_TO_ANALYZE)

        try:
            # Process cards with valid string fields
            if isinstance(field_string, str) and field_string.strip():
                 leaf_tokens = parse_field_hierarchically(field_string)
                 all_tokens_counter.update(leaf_tokens)
                 cards_processed += 1
            else:
                 # Count cards even if the field is empty/None/not string
                 cards_processed += 1

        except Exception as e:
            print(f"  > ERROR: Failed parsing '{FIELD_TO_ANALYZE}' for card_id {card_id}. Value: '{field_string}'. Error: {e}")
            cards_failed += 1

    print(f"\n--- Parsing Summary ---")
    print(f"Successfully processed '{FIELD_TO_ANALYZE}' for {cards_processed} cards.")
    if cards_failed > 0:
        print(f"Failed during parsing for {cards_failed} cards.")

    # --- Filter out numeric tokens and create the final counter ---
    final_tokens_counter = Counter()
    numeric_token_count = 0
    total_tokens_counted = 0
    for token, count in all_tokens_counter.items():
        total_tokens_counted += count
        if not is_numeric(token):
            final_tokens_counter[token] = count
        else:
            numeric_token_count += 1

    # --- Print Filtered Token Statistics ---
    print("\n--- Unique Non-Numeric Leaf Token Statistics (Sorted by Frequency) ---")
    if not final_tokens_counter:
        print("No non-numeric leaf tokens found.")
    else:
        for token, count in final_tokens_counter.most_common():
            print(f"  Token: '{token}' | Count: {count}")

    print(f"\nFound {len(final_tokens_counter)} unique non-numeric leaf tokens.")
    if numeric_token_count > 0:
      print(f"(Excluded {numeric_token_count} purely numeric tokens from the final list. Total tokens processed: {total_tokens_counted})")

    print("\nAnalysis complete.")


# --- Execution ---
if __name__ == "__main__":
    try:
        analyze_field_tokens()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")