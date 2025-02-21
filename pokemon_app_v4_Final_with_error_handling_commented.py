"""
Dash application for Pokémon scouting:
- Fetches a list of Pokémon names from PokeAPI
- Allows the user to select up to 5 Pokémon
- Displays details in a DataTable
- Enables CSV download of the results
- Includes an email report link for errors
"""

import json
import requests
import pandas as pd
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State #Imports dependencies / callbacks input = clicks, outpit = updates the table, state = constant, see line 207

# Constants for PokeAPI endpoints
POKEAPI_URL = "https://pokeapi.co/api/v2/pokemon/"
ENCOUNTERS_URL = "https://pokeapi.co/api/v2/pokemon/{}/encounters"

def load_pokemon_names():
    """
    Fetch a list of Pokémon names from the PokeAPI and sort them alphabetically.

    Returns:
        list of str: Alphabetically sorted list of Pokémon names.
    """
    try:
        response = requests.get("https://pokeapi.co/api/v2/pokemon?limit=2000") #initial load of 1000 names we could add more if needed
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            # Return sorted list of Pokémon names
            return sorted([p["name"] for p in results]) #Sort alphabetically
        print(f"Error retrieving Pokémon list from API: {response.text}") #Error handling, prints non 200 reponse
        return []
    except Exception as exc:
        print(f"Exception encountered while loading Pokémon names: {exc}")
        return []
#Exception as exc handles the unexpected errors when making api requests, does not crash app or terminal if 500 error or other errors
def fetch_pokemon_location(pokemon_id):
    """
    Retrieve location information for a Pokémon using its ID.

    Args:
        pokemon_id (int): The ID of the Pokémon whose location to fetch.

    Returns:
        str: A comma-separated string of location areas or an error message.
    """
    try:
        response = requests.get(ENCOUNTERS_URL.format(pokemon_id)) #calls encounters (location) URL and appends pokemon ID, no other required params, location join, self joins locations
        if response.status_code == 200:
            locations = response.json()
            if locations:
                return ", ".join(
                    loc["location_area"]["name"] for loc in locations
                )
            return "Unknown"
        return (
            f"Error retrieving location (status code {response.status_code})"
        )
    except Exception as exc:
        return f"Exception occurred fetching location: {exc}"

def fetch_pokemon_data(pokemon_name):
    """
    Retrieve Pokémon data from PokeAPI for a single Pokémon.

    Args:
        pokemon_name (str): Name of the Pokémon to fetch.

    Returns:
        dict: A dictionary containing the Pokémon's details or an error message.
    """
    try:
        response = requests.get(f"{POKEAPI_URL}{pokemon_name.lower()}")
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
                "location": location,
            }
        return {
            "name": pokemon_name,
            "error": f"Data not found (status code {response.status_code})"
        }
    except Exception as exc:
        return {"name": pokemon_name, "error": str(exc)}

def generate_error_report_link(error_list):
    """
    Generate an error message and a 'Send Error Report' hyperlink for emailing the dev team.

    Args:
        error_list (list of str): The Pokémon names (or errors) encountered.

    Returns:
        dash.html.Div: A Div containing an error message and an email link.
    """
    dev_team_email = "wcollier1390@gmail.com"   # Change to your dev team's address  - Personal email for now,
    subject = "Pokémon Scouting Error"
    body = (
        "Hello Dev Team,%0D%0A%0D%0A"
        "We encountered the following Pokémon errors or issues:%0D%0A"
        f"{', '.join(error_list)}%0D%0A%0D%0A"
        "Please advise on potential fixes.%0D%0A%0D%0A"
        "Thank you,"
    )
    mailto_link = (
        f"mailto:{dev_team_email}?subject={subject}&body={body}"
    )

    return html.Div(
        [
            html.P(
                f"Error: The following Pokémon were not found or had an error: "
                f"{', '.join(error_list)}",
                style={"color": "red"},
            ),
            html.A(
                "Send Error Report",
                href=mailto_link,
                style={"marginLeft": "10px"},
            ),
        ]
    )

# Load all Pokémon names once at startup
all_pokemon_names = load_pokemon_names()

# Create a Dash application instance
app = dash.Dash(__name__)

# Prepare dropdown options for Pokémon names
pokemon_options = [
    {"label": name.capitalize(), "value": name} for name in all_pokemon_names
]

# Define the application layout
app.layout = html.Div(
    [
        html.H1("Pokémon Scouting"),
        html.P("Select up to 5 Pokémon:"),
        # Container for up to 5 dropdown inputs
        html.Div(
            [
                dcc.Dropdown(
                    id="pokemon1",
                    options=pokemon_options,
                    placeholder="Pokemon 1",
                    clearable=True,
                ),
                dcc.Dropdown(
                    id="pokemon2",
                    options=pokemon_options,
                    placeholder="Pokemon 2",
                    clearable=True,
                ),
                dcc.Dropdown(
                    id="pokemon3",
                    options=pokemon_options,
                    placeholder="Pokemon 3",
                    clearable=True,
                ),
                dcc.Dropdown(
                    id="pokemon4",
                    options=pokemon_options,
                    placeholder="Pokemon 4",
                    clearable=True,
                ),
                dcc.Dropdown(
                    id="pokemon5",
                    options=pokemon_options,
                    placeholder="Pokemon 5",
                    clearable=True,
                )
            ],
            style={
                "display": "grid",
                "gridTemplateColumns": "1fr",
                "gap": "10px",
                "width": "300px",
            },
        ),
        html.Br(),
        html.Button("Fetch Data", id="fetch-button"),
        html.Button(
            "Download CSV", id="download-button", style={"marginLeft": "10px"}
        ),
        # Hidden storage for Pokémon data
        dcc.Store(id="pokemon-data-store"),
        # Download component
        dcc.Download(id="download-csv"),
        # Placeholder for table results
        html.Div(id="results", style={"marginTop": "20px"}),
    ]
)

@app.callback(
    # FIRST CALLBACK: The 'Fetch Data' button
    [Output("pokemon-data-store", "data"),
     Output("results", "children")],
    Input("fetch-button", "n_clicks"),
    [
        State("pokemon1", "value"),
        State("pokemon2", "value"),
        State("pokemon3", "value"),
        State("pokemon4", "value"),
        State("pokemon5", "value")
    ]
)
def update_results(n_clicks, p1, p2, p3, p4, p5):
    """
    Callback for the 'Fetch Data' button.
    Fetches and displays Pokémon data in a table, stores data for CSV download.
    """
    if not n_clicks:
        return None, ""

    # Gather selected Pokémon
    pokemon_names = [p for p in (p1, p2, p3, p4, p5) if p]

    if not pokemon_names:
        return None, "Please select at least one Pokémon."

    # Retrieve data for each Pokémon
    pokemon_data = [fetch_pokemon_data(name) for name in pokemon_names]

    # Check for errors
    error_messages = [p["name"] for p in pokemon_data if "error" in p]
    if error_messages:
        # Return a link to email the dev team with the error details
        return None, generate_error_report_link(error_messages)

    # Construct a Dash DataTable
    columns = [
        {"name": "Name", "id": "name"},
        {"name": "ID", "id": "id"},
        {"name": "Height", "id": "height"},
        {"name": "Weight", "id": "weight"},
        {"name": "Base Experience", "id": "base_experience"},
        {"name": "Types", "id": "types"},
        {"name": "Location", "id": "location"},
    ]

    data_table = dash_table.DataTable(
        id="pokemon-table",
        columns=columns,
        data=pokemon_data,
        style_cell={"textAlign": "left"},
        style_header={"fontWeight": "bold"},
        page_size=10,
    )

    # Return the data for CSV saving, and the table as the UI
    return pokemon_data, data_table

@app.callback(
    # SECOND CALLBACK: The 'Download CSV' button
    Output("download-csv", "data"),
    Input("download-button", "n_clicks"),
    State("pokemon-data-store", "data"),
    prevent_initial_call=True
)
def download_csv(n_clicks, data):
    """
    Callback for the 'Download CSV' button.
    Converts the stored Pokémon data into a DataFrame and downloads as CSV.
    """
    if data:
        df = pd.DataFrame(data)
        return dcc.send_data_frame(df.to_csv, "pokemon_data.csv")
    return None

if __name__ == "__main__":
    app.run_server(debug=True, port=8050)
