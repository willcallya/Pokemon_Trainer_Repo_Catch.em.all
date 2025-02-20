import requests
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import json

POKEAPI_URL = "https://pokeapi.co/api/v2/pokemon/"
ENCOUNTERS_URL = "https://pokeapi.co/api/v2/pokemon/{}/encounters"

# Fetch full list of Pokémon names (limited to a large number)
def load_pokemon_names():
    try:
        response = requests.get("https://pokeapi.co/api/v2/pokemon?limit=2000")
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            return [p["name"] for p in results]
        else:
            print(f"Error retrieving pokemon list from API: {response.text}")
            return []
    except Exception as e:
        print(f"Exception encountered while loading Pokémon names: {e}")
        return []

all_pokemon_names = load_pokemon_names()

# Function to retrieve Pokémon data with error handling
def fetch_pokemon_data(pokemon_name):
    try:
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
            return {"name": pokemon_name, "error": f"Data not found (status code {response.status_code})"}
    except Exception as e:
        return {"name": pokemon_name, "error": str(e)}

# Function to retrieve Pokémon location with error handling
def fetch_pokemon_location(pokemon_id):
    try:
        response = requests.get(ENCOUNTERS_URL.format(pokemon_id))
        if response.status_code == 200:
            locations = response.json()
            if locations:
                return ", ".join([loc["location_area"]["name"] for loc in locations])
            else:
                return "Unknown"
        else:
            return f"Error retrieving location (status code {response.status_code})"
    except Exception as e:
        return f"Exception occurred fetching location: {e}"

# Dash App for UI
app = dash.Dash(__name__)

pokemon_options = [
    {"label": name.capitalize(), "value": name}
    for name in all_pokemon_names
]

app.layout = html.Div([
    html.H1("Pokémon Scouting"),
    html.P("Select up to 5 Pokémon:"),

    html.Div([
        dcc.Dropdown(
            id="pokemon1",
            options=pokemon_options,
            placeholder="Pokemon 1",
            clearable=True
        ),
        dcc.Dropdown(
            id="pokemon2",
            options=pokemon_options,
            placeholder="Pokemon 2",
            clearable=True
        ),
        dcc.Dropdown(
            id="pokemon3",
            options=pokemon_options,
            placeholder="Pokemon 3",
            clearable=True
        ),
        dcc.Dropdown(
            id="pokemon4",
            options=pokemon_options,
            placeholder="Pokemon 4",
            clearable=True
        ),
        dcc.Dropdown(
            id="pokemon5",
            options=pokemon_options,
            placeholder="Pokemon 5",
            clearable=True
        ),
    ], style={"display": "grid", "gridTemplateColumns": "1fr", "gap": "10px", "width": "300px"}),

    html.Br(),
    html.Button("Fetch Data", id="fetch-button"),
    html.Div(id="results", style={"marginTop": "20px"})
])

@app.callback(
    Output("results", "children"),
    [Input("fetch-button", "n_clicks")],
    [Input("pokemon1", "value"),
     Input("pokemon2", "value"),
     Input("pokemon3", "value"),
     Input("pokemon4", "value"),
     Input("pokemon5", "value")] 
)
def update_results(n_clicks, p1, p2, p3, p4, p5):
    if not n_clicks:
        return ""

    # Gather selected Pokémon
    pokemon_names = [p for p in [p1, p2, p3, p4, p5] if p]

    if not pokemon_names:
        return "Please select at least one Pokémon."

    # Retrieve data for each Pokémon
    pokemon_data = [fetch_pokemon_data(pokemon) for pokemon in pokemon_names]

    # Check for errors
    error_messages = [pd["name"] for pd in pokemon_data if "error" in pd]
    if error_messages:
        return html.Div([
            html.P(
                f"Error: The following Pokémon were not found or had an error: {', '.join(error_messages)}",
                style={"color": "red"}
            )
        ])

    # Display results
    return html.Pre(json.dumps(pokemon_data, indent=2))

if __name__ == "__main__":
    app.run_server(debug=True, port=8050)
