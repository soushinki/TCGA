import requests
import json  # 1. Import the json library

# The API endpoint URL
url = "https://shadowverse-portal.com/api/v1/cards?clan=8&format=json&lang=en"
output_filename = "portal.json"  # The name of the file we'll save

print(f"Fetching data from: {url}")

try:
    response = requests.get(url, timeout=10)

    if response.status_code == 200:
        data = response.json()
        card_list = data.get('data', {}).get('cards', [])
        card_count = len(card_list)
        print(f"Success! Found {card_count} cards.")

        # --- NEW: Save the card_list to disk ---
        print(f"Saving data to '{output_filename}'...")

        # 2. Open the file in write mode ('w')
        with open(output_filename, 'w', encoding='utf-8') as f:
            # 3. Use json.dump() to write the data
            # indent=2 makes the JSON file nicely formatted and easy to read.
            json.dump(card_list, f, indent=2, ensure_ascii=False)
        
        print("File saved successfully.")
        
    else:
        print(f"Error: Failed to fetch data. Status code: {response.status_code}")

except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")