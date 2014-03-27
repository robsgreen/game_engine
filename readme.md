game_engine
===========
Python Pyramid version, based on the original: [Jacobkg/game_engine](https://github.com/Jacobkg/game_engine)
###Installation
  
  1. Install requirements
  
  `pip install -r game_engine.req`
  
  2. Initialize the sqlite database:
  
  `python initializedb.py development.ini`

###Run the server
`python game_engine/wsgiapp.py -c development.ini`


###Game Rules
- Board is a 20 x 20 grid. Position (0,0) is in the upper left. Position (0,19) is the bottom left.
- There are two players, X and Y. X starts at (0,0). Y starts at (19,19).
- Player X moves first
- There are 4 legal moves. Left, Right, Up, and Down. Each move a player one space.
- There are 21 "stars" randomly generated on the board.
- Players collect stars by moving onto the square where the star is located. Once a star has been collected it is removed from the board.
- The first player to collect 11 stars is the winner
- A stalemate occurs if 100 moves pass without any stars being collected. A stalemate counts as a win for Y.

## Game Protocol

When it is a player's move, that player's url will be sent a GET request containing the board state. It will be of the form:

```
http://localhost:3000?board={"stars":[[12,2],[12,3],[14,7],[19,9],[15,16],[6,14],[9,17],[7,10],[6,5],[7,11],[13,10],[1,15],[7,5],[19,3],[4,7],[6,17],[14,19],[3,10],[19,7],[12,10],[9,15]],"x_position":[0,0],"y_position":[19,19],"x_score":0,"y_score":0,"player_to_move":"X"}
```

The board is represented in JSON with the following parameters
- stars: The position of all the stars on the board
- x_position: The position of the X player
- y_position: The position of the Y player
- x_score: The number of stars collected so far by the X player
- y_score: The number of stars collected so far by the Y player
- player_to_move: The player represented by the AI server (your player).

Your AI should respond with JSON encoding of the desired move. For example

```
{ "move" : "left" }
```



