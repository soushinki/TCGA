import json
import argparse
import sys

def check_subset(superset_file: str, subset_file: str):
    """
    Checks if the card IDs from one JSON file are a subset of another.

    Args:
        superset_file (str): The path to the JSON file that should contain all the cards (the bigger list).
        subset_file (str): The path to the JSON file that should be a subset (the smaller list).
    """
    try:
        # Load the superset file and extract card IDs into a set for fast lookups
        with open(superset_file, 'r', encoding='utf-8') as f:
            superset_data = json.load(f)
        superset_ids = {str(item['card_id']) for item in superset_data}
        print(f"Loaded {len(superset_ids)} unique card IDs from '{superset_file}'.")

        # Load the subset file and extract card IDs
        with open(subset_file, 'r', encoding='utf-8') as f:
            subset_data = json.load(f)
        subset_ids = {str(item['card_id']) for item in subset_data}
        print(f"Loaded {len(subset_ids)} unique card IDs from '{subset_file}'.")

    except FileNotFoundError as e:
        print(f"Error: File not found. Please check your file paths. Details: {e}")
        sys.exit(1)
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        print(f"Error: Could not process JSON file. Make sure it's a valid array of objects with a 'card_id' attribute. Details: {e}")
        sys.exit(1)

    # Perform the check
    print("\n--- Comparing Sets ---")
    if subset_ids.issubset(superset_ids):
        print(f"✅ SUCCESS: '{subset_file}' is a complete subset of '{superset_file}'.")
    else:
        # Find which card IDs are missing
        missing_ids = subset_ids - superset_ids
        print(f"❌ FAILURE: '{subset_file}' is NOT a subset of '{superset_file}'.")
        print(f"Found {len(missing_ids)} missing card ID(s):")
        for card_id in sorted(missing_ids):
            print(f"  - {card_id}")

def main():
    # Set up the command-line argument parser
    parser = argparse.ArgumentParser(
        description="Compare two JSON card databases to see if one is a subset of the other based on 'card_id'."
    )
    parser.add_argument("superset_file", help="The path to the JSON file that should be the 'master' list.")
    parser.add_argument("subset_file", help="The path to the JSON file that should be the 'subset' list.")
    
    args = parser.parse_args()
    
    check_subset(args.superset_file, args.subset_file)


if __name__ == "__main__":
    main()