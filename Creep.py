import sys, pygame
from pygame.sprite import Sprite
from random import randint, choice, uniform
from vec2d import vec2d
import subprocess
import re

class CreepGame():
	
	def __init__(self):
		pygame.init()
		self.screen = self.createScreen()
		(w,h)=self.screen.get_size()
		self.spawnBox = pygame.Rect(0,0,w,h)
		self.clock = pygame.time.Clock()
		self.bg_color = 0,0,0
		self.nCreeps = 30 #min (and starting) number of creeps 
		self.fps=90 #max FPS
		self.creepSeq=0
		self.creeps = pygame.sprite.Group()
		self.createCreepTypes()
		self.nextType=self.pinkType
		

	def createScreen(self):
		print 'available resolutions', pygame.display.list_modes(0)
		
		''' the next two lines set up full screen'''
		screen_width, screen_height = pygame.display.list_modes(0)[0]
		options = pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF		
		
		''' the next two lines set up windowed swap with above for windowed'''
		#screen_width, screen_height = (0,0)
		#options=0
		screen = pygame.display.set_mode(
		    (screen_width, screen_height), options)
		print "screen created, size is:", screen.get_size()
		return screen

	def runGame(self):
		while True:
		    time_passed = self.clock.tick(self.fps)
		    self.handleInputEvents()
		    self.updateCreeps(time_passed)
		    self.drawEverything()
		return	
		
	def updateCreeps(self,time_passed):
		for creep in self.creeps:
			pygame.sprite.spritecollide(creep
					, self.creeps
					, False
					, Creep.collide)
			creep.update(time_passed)
		if len(self.creeps)<self.nCreeps:
			type = choice([self.pinkType, self.blueType, self.greyType])
			self.creepAdd(type)		

	def createCreepTypes(self):
		print "creating creeps"
		self.pinkType = CreepType()
		self.pinkType.type='pink'
		self.pinkType.filename='pinkcreep.png'
		#self.pinkType.filename='petecreep.png'
		self.pinkType.maxhealth=100
		self.pinkType.spawnBox=self.spawnBox
		
		self.blueType = CreepType()
		self.blueType.type='blue'
		self.blueType.filename='bluecreep.png'
		self.blueType.maxhealth=70
		self.blueType.spawnBox=self.spawnBox
		
		self.greyType = CreepType()
		self.greyType.type='grey'
		self.greyType.filename='graycreep.png'
		self.greyType.maxhealth=50
		self.greyType.spawnBox=self.spawnBox

		
	def creepAdd(self,type, pos =None):
		self.creepSeq += 1
		id = type.type+"(%s)" % (self.creepSeq)
		creep = Creep(type,id,pos)
		self.creeps.add(creep)
		
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
		
	def handleInputEvents(self):
		for event in pygame.event.get():
			if(event.type == pygame.MOUSEBUTTONDOWN):
				if(event.button==4):
					self.cycleNext(-1)
				if(event.button==5):
					self.cycleNext(+1)
				if(event.button==1):
					self.creepAdd(self.nextType,event.pos)
			if(event.type == pygame.KEYDOWN):
				print event
				sys.exit(0)
			if (event.type == pygame.QUIT):
				print "quitting"
				sys.exit(0)
	
	def drawEverything(self):
		self.screen.fill(self.bg_color)
		self.creeps.draw(self.screen)
		pygame.display.flip()
	

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
		self.maxhealth=self.type.maxhealth
		self.health=self.type.maxhealth
		self.base_image = pygame.image.load(self.type.filename).convert_alpha()
		self.image = self.base_image
		self.rect = self.image.get_rect()
		#initial direction is towards the bottom right, it randmomises as soon as they spawn though
		self.direction = vec2d(1,1)
		# @TODO different max/min speed per type
		# speeds are in pixels per millisecond (are they? check..)
		self.speedmax = 0.18
		self.speedmin = 0.11
		self.elapsed_time=0
		self.curspeed = uniform(0.08,0.2)
		self.direction.length = self.curspeed
		if (pos):
			#if we specify a starting position it should be the centre
			self.rect.center = pos
		else:
			#otherwise just set the rect x & y and don't bother doing any arithmetic to find the centre
			self.rect.x = randint(type.spawnBox.x, type.spawnBox.w)
			self.rect.y = randint(type.spawnBox.y, type.spawnBox.h)
		self.mask = pygame.mask.from_surface(self.image)
		#this randomises the initial direction
		self.rotate(0,360)
	
	def __str__(self):
		return self.type.type+" creep:"+ self.id+" - health:"+str(self.health)+" - rect:"+str(self.rect)+" - direction:"+str(self.direction)
	
	def update(self,time):
		
		self.elapsed_time += time
				
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
		    
		if(self.elapsed_time>randint(250,1000)):
			self.curspeed = self.curspeed * uniform(0.8,1.05)
			if self.curspeed < self.speedmin:
				self.curspeed = self.speedmin			
			self.rotate(-45,45)
			self.elapsed_time=0
			if self.health <= self.type.maxhealth:
				self.health += 0.1
		self.direction.length = time * self.curspeed 
		self.rect.move_ip(self.direction)

	
	def collide(creep1, creep2):
		if creep1.id != creep2.id:
			if  pygame.sprite.collide_mask(creep1, creep2):
				if(creep1.type != creep2.type and creep1.health<=creep2.health):
					creep1.rotate(-30,30)
					creep1.health -=1
					creep2.health -=0.5
					if creep1.health <= 0:
						True
						creep1.kill()
			elif creep1.elapsed_time > randint(200, 500):
				if (pygame.sprite.collide_circle_ratio(15)(creep1,creep2) ):
					if creep1.type != creep2.type:
						if creep1.health>creep2.health:
							creep2.curspeed = uniform(creep2.curspeed *1.2 , creep2.curspeed*1.3)
							creep1.curspeed = uniform(creep1.curspeed *1.1 , creep1.curspeed*1.2)
							if creep1.curspeed > creep1.speedmax:
								creep1.curspeed = creep1.speedmax
							if creep2.curspeed > creep2.speedmax:
								creep2.curspeed = creep2.speedmax
						vec= vec2d(creep2.rect.x - creep1.rect.x,creep2.rect.y - creep1.rect.y)
						if creep1.health>creep2.health:
							creep1.rotate(creep1.direction.get_angle_between(vec)+randint(-10,10))
						else:
							creep1.rotate(creep1.direction.get_angle_between(vec)-180+randint(-10,10))
					
			
				if (pygame.sprite.collide_circle_ratio(10)(creep1,creep2) and creep1.health>=creep2.health and (creep1.type == creep2.type and creep1.elapsed_time >= 300)):
					vec= vec2d(creep2.rect.x - creep1.rect.x,creep2.rect.y - creep1.rect.y)
					creep1.rotate(creep1.direction.get_angle_between(vec)+randint(-6,6))
					creep1.curspeed = uniform(creep1.curspeed *0.8 , creep1.curspeed*0.7)

				
					
				
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

		