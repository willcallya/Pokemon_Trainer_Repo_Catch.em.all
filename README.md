Pokémon Scouting Application
This application provides a user-friendly interface for scouting Pokémon data from the PokeAPI using Dash.
Features
•	Dropdowns for up to 5 Pokémon
•	Cleaner data table for Pokémon stats
•	CSV export of results
•	Error handling for invalid or missing Pokémon
Setup Instructions
1.	Install Dependencies
pip install dash requests pandas
If you don’t have pip, install it according to your operating system guidelines.
2.	Run the Application
1.	Save the application code (above) into a file (e.g., pokemon_app.py).
2.	Run the file in your terminal:
python pokemon_app.py
3.	Open your browser to http://localhost:8050 to access the application.
3.	Using the Application
o	Select up to 5 Pokémon using the dropdowns.
o	Click Fetch Data to retrieve and display Pokémon information.
o	Click Download CSV to save the results locally.
Configuring for Other Pokémon
By default, the application loads up to 2,000 Pokémon names from the PokeAPI. If you need to change this:
1.	Adjust the limit in the load_pokemon_names() function:
response = requests.get("https://pokeapi.co/api/v2/pokemon?limit=2000")
Increase or decrease limit based on your needs.
2.	Adjust logic for retrieving data:
o	Modify fetch_pokemon_data() or fetch_pokemon_location() if you want different Pokémon fields.
Notes
•	The PokeAPI rate limits may apply if you fetch data for many Pokémon simultaneously.
•	You can disable or update the debug mode by editing the app.run_server() call.
•	If you need a different port, set the port parameter accordingly:
app.run_server(debug=True, port=1234)
Troubleshooting
•	If the app won’t start, ensure all dependencies are installed.
•	Check if your port 8050 is free or set a different port.
•	If you see errors fetching specific Pokémon, it may mean the Pokémon name is invalid or PokeAPI is down.

