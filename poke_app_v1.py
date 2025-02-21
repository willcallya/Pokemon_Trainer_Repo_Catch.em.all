import requests
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import json

# API endpoints
POKEAPI_URL = "https://pokeapi.co/api/v2/pokemon/"
ENCOUNTERS_URL = "https://pokeapi.co/api/v2/pokemon/{}/encounters"

def fetch_pokemon_location(pokemon_id):
    """
    Retrieve location information for a Pokémon using its ID.
    """
    try:
        response = requests.get(ENCOUNTERS_URL.format(pokemon_id))
        if response.status_code == 200:
            locations = response.json()
            if locations:
                return ", ".join(loc["location_area"]["name"] for loc in locations)
            return "Unknown"
        return f"Error retrieving location (status code {response.status_code})"
    except Exception as e:
        return f"Exception occurred fetching location: {e}"

def fetch_pokemon_data(pokemon_name):
    """
    Retrieve Pokémon data from PokeAPI for a single Pokémon.
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
                "types": ", ".join(t["type"]["name"] for t in data["types"]),
                "location": location,
            }
        else:
            return {
                "name": pokemon_name,
                "error": f"Data not found (status code {response.status_code})"
            }
    except Exception as e:
        return {"name": pokemon_name, "error": str(e)}

# Initialize Dash app
app = dash.Dash(__name__)

# Define layout with five text inputs for Pokémon names
app.layout = html.Div([
    html.H1("Pokémon Scouting"),
    html.P("Type in up to 5 Pokémon names:"),

    html.Div([
        dcc.Input(id="pokemon1", type="text", placeholder="Pokemon 1"),
        dcc.Input(id="pokemon2", type="text", placeholder="Pokemon 2"),
        dcc.Input(id="pokemon3", type="text", placeholder="Pokemon 3"),
        dcc.Input(id="pokemon4", type="text", placeholder="Pokemon 4"),
        dcc.Input(id="pokemon5", type="text", placeholder="Pokemon 5")
    ], style={"display": "grid", "gridTemplateColumns": "1fr", "gap": "10px", "width": "300px"}),

    html.Br(),
    html.Button("Fetch Data", id="fetch-button"),

    # Area to show results (errors or data)
    html.Div(id="results", style={"marginTop": "20px"})
])

@app.callback(
    Output("results", "children"),
    [Input("fetch-button", "n_clicks")],
    [
        Input("pokemon1", "value"),
        Input("pokemon2", "value"),
        Input("pokemon3", "value"),
        Input("pokemon4", "value"),
        Input("pokemon5", "value")
    ]
)
def update_results(n_clicks, p1, p2, p3, p4, p5):
    """
    When the user clicks 'Fetch Data', gather the Pokémon names entered
    and fetch their data. Display errors or JSON-formatted data.
    """
    if not n_clicks:
        return ""

    pokemon_names = [p for p in [p1, p2, p3, p4, p5] if p]
    if not pokemon_names:
        return "Please enter at least one Pokémon name."

    # Retrieve data for each Pokémon
    pokemon_data = [fetch_pokemon_data(p) for p in pokemon_names]

    # Check for errors
    error_messages = [pd["name"] for pd in pokemon_data if "error" in pd]
    if error_messages:
        return html.Div([
            html.P(
                f"Error: The following Pokémon were not found or had an error: "
                f"{', '.join(error_messages)}",
                style={"color": "red"}
            )
        ])

    # Otherwise, display JSON data
    return html.Pre(json.dumps(pokemon_data, indent=2))

if __name__ == "__main__":
    app.run_server(debug=True, port=8050)
