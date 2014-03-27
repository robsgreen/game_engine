Install requirements

pip install -r game_engine.req

To run the game_engine server:

1. Initialize the sqlite database
python initializedb.py development.ini

2. Run the server
python game_engine/wsgiapp.py -c development.ini