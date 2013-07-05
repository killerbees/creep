# Creep pyGame

This project is a fun introduction to pyGame and game development. It's currently a WIP, pull requests welcome!

## Installation

##### 1. Install Python and pyGame
```bash
apt-get install python-pygame
```
##### 2. Run the game!
```bash
python game.py
```

## Controls

 - Left mouse button adds creeps at pointer.
 - Mouse button four and five (wheel scroll up/down) changes type added.
 - any key quits

## Documentation
>### game.py
>This is just a simple launcher.
>
>
>### Creep.py
> `Creep.py` is the main game code.
>
> `CreepGame` class is the game, the main game loop is in `CreepGame.runGame`. 
```python
def runGame(self):
	while True:
	    time_passed = self.clock.tick(self.fps)
	    self.handleInputEvents()
	    self.updateCreeps(time_passed)
	    self.drawEverything()
	return	
```
>
> Event handlers are hooked up to events in `CreepGame.handleInputEvents`.
>
> `Creep` class is the creep itself, `CreepType` class is for creating types of creeps.
>
>>#### `Creep.update`
>>This is the method called by the game loop to allow the creep to do its stuff, it just moves around.
>    
>>#### `Creep.collide`
>>this is the method called from the game loop to handle interactions for every combination of two creeps in the creeps collection. This is where all the proximity and collision behaviour is handled.
>
>### vect2d
> vec2d is useful for vector arithmetic.

## Roadmap
 - [x] @killerbees initial commit
 - [ ] ...
