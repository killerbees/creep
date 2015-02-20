import sys, pygame
from pygame.sprite import Sprite
from random import randint, choice, uniform
from vec2d import vec2d
import subprocess
import re

class CreepGame():
	
	#some default numbers and initialisations
	def __init__(self):
		#we need pygame
		pygame.init()
		#we need a screen
		self.screen = self.createScreen()
		(w,h)=self.screen.get_size()
		
		#spawnbox is the rectangle that we can create new sprites in
		self.spawnBox = pygame.Rect(0,0,w,h) #our spawn box is the whole screen
		self.clock = pygame.time.Clock() # clock is for "ticking" the game loop and regulating the fps
		
		self.createCreepTypes() #define the "species"
		
		# set up some default behaviour config for our game
		self.bg_color = 0,0,0
		self.nCreeps = 30 #min (and starting) number of creeps 
		self.fps=90 #max FPS
		self.creepSeq=0 #sequence number for creep.id's
		self.nextType=self.pinkType #initial creep type for the mouse click & wheel actions
		
		# all of our sprites will belong to a pygame group 
		self.creeps = pygame.sprite.Group()
		
		
		
		
		
	# create a pygame screen for a window or fullscreen
	def createScreen(self):
		print 'available resolutions', pygame.display.list_modes(0)
		
		#@todo make this a command line switch
		#the next two lines set up full screen options, to run in a window see below
		screen_width, screen_height = pygame.display.list_modes(0)[0] # we use the 1st resolution which is the largest, and ought to give us the full multi-monitor
		options = pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF		
		
		#the next two lines set up windowed options - swap these with above to run full screen instead
		#screen_width, screen_height = (0,0)
		#options=0
		
		#create the screen with the options
		screen = pygame.display.set_mode(
		    (screen_width, screen_height), options)
		print "screen created, size is:", screen.get_size()
		return screen

	#the Game Loop
	# @see http://gameprogrammingpatterns.com/game-loop.html
	def runGame(self):
		while True:
		    time_passed = self.clock.tick(self.fps) #the game clock
		    self.handleInputEvents()
		    self.updateCreeps(time_passed)
		    self.drawEverything()
		return	
		
	#when we update the creeps we need to know how much time has passed so that we can plot their new position from their speed and direction
	#simples eh? :)
	def updateCreeps(self,time_passed):
		for creep in self.creeps:
			#the next line calls "Collide" for each creep with all the other creeps
			# this is the entry to the interaction between creeps
			pygame.sprite.spritecollide(creep
					, self.creeps
					, False
					, Creep.collide)
			#then we update the creep,
			#yes we do this before we've done all the other collides
			#yes this will lead to some anomlaous behavour,  where order in the list conveys an advantage in conflict
			#no, we don't really care!
			creep.update(time_passed)
		#if  they're dying off below the threshold spawn a new one of random type
		#@todo make the starting number and the mimium threshold different
		if len(self.creeps)<self.nCreeps:
			type = choice([self.pinkType, self.blueType, self.greyType])
			self.creepAdd(type)		

	def createCreepTypes(self):
		print "creating creeps"
		self.pinkType = CreepType()
		self.pinkType.type='pink'
		self.pinkType.filename='pinkcreep.png'
		#self.pinkType.filename='petecreep.png'
		self.pinkType.maxhealth=50
		self.pinkType.spawnBox=self.spawnBox
		
		self.blueType = CreepType()
		self.blueType.type='blue'
		self.blueType.filename='bluecreep.png'
		self.blueType.maxhealth=50
		self.blueType.spawnBox=self.spawnBox
		
		self.greyType = CreepType()
		self.greyType.type='grey'
		self.greyType.filename='graycreep.png'
		self.greyType.maxhealth=50
		self.greyType.spawnBox=self.spawnBox

		
	def creepAdd(self,type, pos =None):
		self.creepSeq += 1
		#give each one a unique name for debugging
		id = type.type+"(%s)" % (self.creepSeq)
		creep = Creep(type,id,pos)
		#add her to the group
		self.creeps.add(creep)
		
	#order of creep types to cycle through on the mouse wheel
	#@todo there must be a more elegant way to do this.
	def cycleNext(self, by):
		if by <0:
			if self.nextType==self.pinkType:
				self.nextType=self.blueType
			elif self.nextType==self.blueType:
				self.nextType=self.greyType
			elif self.nextType==self.greyType:
				self.nextType=self.pinkType
		if by >0:
			if self.nextType==self.pinkType:
				self.nextType=self.greyType
			elif self.nextType==self.blueType:
				self.nextType=self.pinkType
			elif self.nextType==self.greyType:
				self.nextType=self.blueType
	
	#this is where we register our event listeners
	#yes, we're just calling methods
	#@todo create proper event listeners
	def handleInputEvents(self):
		for event in pygame.event.get():
			if(event.type == pygame.MOUSEBUTTONDOWN):
				if(event.button==4): #wheel rotate
					self.cycleNext(-1)
				if(event.button==5): #wheel other rotate
					self.cycleNext(+1)
				if(event.button==1): #left click
					self.creepAdd(self.nextType,event.pos)
			if(event.type == pygame.KEYDOWN):
				sys.exit(0) #quit on any key
			if (event.type == pygame.QUIT):  #pygame issues a quit event, for e.g. by closing the window
				print "quitting"
				sys.exit(0)
	
	def drawEverything(self):
		#we "blank" the whole display and redraw everything for each cycle of the game loop
		#yes, this is possibly not the most efficient way to do it!
		self.screen.fill(self.bg_color) 
		#this is where pygame helps us, it will draw all the sprites in the collection on our screen for us
		self.creeps.draw(self.screen)
		#blit the pygame screen to the display
		pygame.display.flip()
	
# template for a Creep type
class CreepType(object):
	def __init__(self):
		self.type=None
		self.filename=None
		self.maxhealth=100 #100 is a default
	def __str__(self):
		return "type:"+self.type+" - maxhealth:"+str(self.maxhealth)

class Creep(Sprite):
	def __init__(self, type, id, pos=None):
		Sprite.__init__(self)
		self.id = id
		self.type=type
		#load some init values from our chosen type
		self.maxhealth=self.type.maxhealth
		self.health=self.type.maxhealth
		self.base_image = pygame.image.load(self.type.filename).convert_alpha()
		#self.image will be changed (rotated in this case) base_image doesn't change
		self.image = self.base_image
		self.rect = self.image.get_rect()
		#initial direction is towards the bottom right, it randmomises as soon as they spawn though
		#we're using a vector library so we can do vector arithmetic with direction, rotation, speed and time.
		self.direction = vec2d(1,1)
		# @TODO different max/min speed per type
		# speeds are in pixels per millisecond (are they? check..)
		self.speedmax = 0.15
		self.speedmin = 0.05
		self.elapsed_time=0
		#initial speed is random within the limits
		#@todo replace "magic numbers" with configurable properties
		self.curspeed = uniform(0.08,0.2)
		#badly named variables, but direction is a vector property
		self.direction.length = self.curspeed
		if (pos):
			#if we specify a starting position it should be for the centre of the sprite
			self.rect.center = pos
		else:
			#otherwise just set random rect x & y somwehere in the spawn box and don't bother doing any arithmetic to find the centre
			#yes this might cause glitching of sprites created at the edge
			#no I don't care about that yet
			self.rect.x = randint(type.spawnBox.x, type.spawnBox.w)
			self.rect.y = randint(type.spawnBox.y, type.spawnBox.h)
		#the mask is  used by pygame to detect collisions
		#pygame calculates the mask for us
		# I <3 pygame :)
		# each sprite has its own mask (rather than a mask per type) 
		#because the mask changes when the sprite rotates 
		#(unless its perfectly circular or rotates by exactly its angle of rotational symmetry)
		self.mask = pygame.mask.from_surface(self.image)
		#this randomises the initial direction
		self.rotate(0,360)
	
	def __str__(self):
		#output some debugging info
		return self.type.type+" creep:"+ self.id+" - health:"+str(self.health)+" - rect:"+str(self.rect)+" - direction:"+str(self.direction)
	
	def update(self,time):
		
		self.elapsed_time += time
				
		# keep the little buggers on the screen...
		#@todo make this more elegant
		if self.rect.x < self.type.spawnBox.left:
		    self.rect.x = self.type.spawnBox.left
		    self.direction.x *= -1
		    self.rotate()
		    self.elapsed_time=0
		elif self.rect.x > self.type.spawnBox.right-self.rect.w:
		    self.rect.x = self.type.spawnBox.right-self.rect.w
		    self.direction.x *= -1
		    self.rotate()
		    self.elapsed_time=0
		elif self.rect.y < self.type.spawnBox.top:
		    self.rect.y = self.type.spawnBox.top
		    self.direction.y *= -1
		    self.rotate()
		    self.elapsed_time=0
		elif self.rect.y > self.type.spawnBox.bottom-self.rect.h:
		    self.rect.y = self.type.spawnBox.bottom-self.rect.h
		    self.direction.y *= -1
		    self.rotate()
		    self.elapsed_time=0
		    
		# how long since we changed speed or direction?
		#@todo make magic numbers into configuration items
		# if its longer than a random time between 1/4 to 1/2 of a second since we changed speed or direction
		if(self.elapsed_time>randint(250,500)):
			#ok, lets mooch about
			#reset the clock
			self.elapsed_time=0
			#change speed, slow down a bit
			# acceleration is always in response to proximity to other types (percieved threat)
			#@todo "magic number" - get rid
			self.curspeed = self.curspeed * uniform(0.5,0.7)
			# apply min speed limit, we don't want them to stop
			if self.curspeed < self.speedmin:
				self.curspeed = self.speedmin		
			#turn a bit (degrees)
			self.rotate(-45,45)
			#heal a bit
			if self.health <= self.type.maxhealth:
				self.health += 0.1
		#distance = speed x time, yeah school maths, who'd'a thunk it.
		self.direction.length = time * self.curspeed 
		# http://www.pygame.org/docs/ref/rect.html#pygame.Rect.move_ip
		# self.direction is a vector, so you change the distance (above) and it presents as coordinates.
		#cool, right?
		self.rect.move_ip(self.direction)
		

	# check for collisions and do the collision action
	# this represents all the creep interaction behaviour
	def collide(creep1, creep2):
		#it seems silly to have to check for self-self collisions, pygame could filter this out but hey, I guess its empowering
		if creep1.id != creep2.id:
			if  pygame.sprite.collide_mask(creep1, creep2): #if we actually bump
				if(creep1.type != creep2.type and creep1.health<=creep2.health):
					#because each collision will be handled twice,  with each participant as "creep1"
					#we only act when creep  1 is the weaker one
					#creep1 turns 
					creep1.rotate(-30,30)
					#creep1 gets hurt
					creep1.health -=1
					#creep2 looses health from the attack
					creep2.health -=0.5
					#if creep health is zero it is dead :-/
					if creep1.health <= 0:
						True
						creep1.kill()
					if creep2.health <= 0:
						True
						creep2.kill()
			
			elif creep1.elapsed_time > randint(200, 500):
				#at an interval, to mimic a lack of perfect awareness, 			
				#we use Collide to check whether or not creep2 is "near" creep1
				#the circle is 15* the diamater of the "size" of creep1
				if (pygame.sprite.collide_circle_ratio(15)(creep1,creep2) ):
					if creep1.type != creep2.type: #if they're not the same type
						if creep1.health>creep2.health: #if creep1 is stronger
							creep1.elapsed_time=0
							creep2.curspeed = uniform(creep2.curspeed *1.2 , creep2.curspeed*1.3) #creep2 accelerates most because its fleeing
							creep1.curspeed = uniform(creep1.curspeed *1.1 , creep1.curspeed*1.2) #creaap1 accelerates to attack
							#apply max speed limits
							if creep1.curspeed > creep1.speedmax:
								creep1.curspeed = creep1.speedmax
							if creep2.curspeed > creep2.speedmax:
								creep2.curspeed = creep2.speedmax
						#figure out the vector between the creep1 & 2		
						vec= vec2d(creep2.rect.x - creep1.rect.x,creep2.rect.y - creep1.rect.y)
						if creep1.health>creep2.health: #if creep1 is stronger
							creep1.rotate(creep1.direction.get_angle_between(vec)+randint(-10,10)) #creep1 turns towards creep2 (not perfectly) and the hunt is on!
						else:
							creep1.rotate(creep1.direction.get_angle_between(vec)-180+randint(-10,10)) #otherwise creep1 turns away!
				if (pygame.sprite.collide_circle_ratio(10)(creep1,creep2) and creep1.health>=creep2.health and (creep1.type == creep2.type and creep1.elapsed_time >= 500)):
						creep1.elapsed_time=0
						vec= vec2d(creep2.rect.x - creep1.rect.x,creep2.rect.y - creep1.rect.y)
						#when the creep types are the same, they slow down and turn towards one another
						#this is the flocking behaviour
						creep1.rotate(creep1.direction.get_angle_between(vec)+randint(-6,6))
						creep1.curspeed = uniform(creep1.curspeed *0.7, creep1.curspeed*0.8)

				
					
				
	def rotate(self, range_lo = 0, range_hi = None):
		if range_hi:
			angle = randint(range_lo, range_hi)
		else:
			angle = range_lo
		self.direction.rotate(angle)
		#self.direction.length = 1.4
		self.image = pygame.transform.rotate(
			self.base_image, -self.direction.angle)
		self.mask = pygame.mask.from_surface(self.image)

		