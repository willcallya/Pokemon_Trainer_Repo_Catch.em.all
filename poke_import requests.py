import requests
import csv
import pandas as pd
import os

# List of Pokémon to source
target_pokemon = ["pikachu", "dhelmise", "charizard", "parasect", "terodactyl", "kingler"]

#URLs / Endpoints for PokeAPI
POKEAPI_URL = "https://pokeapi.co/api/v2/pokemon/"
ENCOUNTERS_URL = "https://pokeapi.co/api/v2/pokemon/{}/encounters"

# Function to retrieve Pokémon data
def fetch_pokemon_data(pokemon_name):
    response = requests.get(POKEAPI_URL + pokemon_name.lower())
    if response.status_code == 200:
        data = response.json()
        pokemon_id = data["id"]
        location = fetch_pokemon_location(pokemon_id)
        return {
            "name": data["name"],
            "id": pokemon_id,
            "height": data["height"],
            "weight": data["weight"],
            "base_experience": data["base_experience"],
            "types": ", ".join([t["type"]["name"] for t in data["types"]]),
            "location": location
        }
    else:
        return {"name": pokemon_name, "error": "Data not found"}

# Function to retrieve Pokémon location
def fetch_pokemon_location(pokemon_id):
    response = requests.get(ENCOUNTERS_URL.format(pokemon_id))
    if response.status_code == 200:
        locations = response.json()
        if locations:
            return ", ".join([loc["location_area"]["name"] for loc in locations])
        else:
            return "Unknown"
    return "Error retrieving location"

# Function to run the Pokémon scouting task
def run_scouting_task():
    # Retrieve data for each Pokémon
    pokemon_data = [fetch_pokemon_data(pokemon) for pokemon in target_pokemon]
    
    # Convert to DataFrame
    df = pd.DataFrame(pokemon_data)
    
    # Define the downloads directory
    downloads_dir = os.path.expanduser("~/Downloads")
    csv_filename = os.path.join(downloads_dir, "pokemon_scouting_report.csv")
    
    # Save data to CSV
    df.to_csv(csv_filename, index=False)
    
    # Print DataFrame and CSV location
    print(df)
    print(f"Pokémon scouting report saved at: {csv_filename}")

# Run the task immediately
run_scouting_task()
