# creep game instructions

# install python and pygame

apt-get install python-pygame

# run the game...

python game.py

In Game:
left mouse button adds creeps at pointer
mouse button four and five (wheel scroll up/down) changes type added
any key quits

In Code:
game.py is a simple launcher
Creep.py is the main game code
vec2d is useful vector arithmetic 

In Creep.py:
CreepGame class is the game, the game loop is in CreepGame.runGame
Event handlers are hooked up to events in CreepGame.handleInputEvents

Creep class is the creep itself, 
CreepType class is for creating types of creeps

Creep.update is the method called by the game loop to allow the creep to do its stuff, it just moves around.
	
Creep.collide is the method called from the game loop to handle interactions for every combination of two creeps in the creeps collection.
	This is where all the proximity and collision behavour is handled
	
