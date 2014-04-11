import my, pygame, map, ui, os, random, math, item, shadow
from pygame.locals import *
from random import randint

my.allMobs = pygame.sprite.Group()
my.allHumans = pygame.sprite.Group()
my.animals = pygame.sprite.Group()
my.corpses = pygame.sprite.Group()

my.serfs = pygame.sprite.Group()
my.builders = pygame.sprite.Group()
my.woodcutters = pygame.sprite.Group()
my.miners = pygame.sprite.Group()
my.fishermen = pygame.sprite.Group()
OCCUPATIONS = ['None', 'builder', 'woodcutter', 'miner', 'fisherman']
OCCUPATIONGROUPS = {'None': my.serfs, 'builder': my.builders, 'woodcutter': my.woodcutters,
					'miner': my.miners, 'fisherman': my.fishermen}

def updateMobs():
	for mob in my.allMobs.sprites():
		mob.handleShadow()
	for corpse in my.corpses.sprites():
		corpse.update()
	for mob in my.animals.sprites():
		mob.update()
	for mob in my.allHumans.sprites():
		mob.update()
	for mob in my.allMobs.sprites():
		mob.handleTooltip()
	for corpse in my.corpses.sprites():
		corpse.handleTooltip()
	if len(my.designatedTrees) > my.MAXTREESDESIGNATED:
		list(iter(my.designatedTrees))[0].remove()


def loadAnimationFiles(directory):
	"""Load images from directory into a list of surfaces"""
	animation = []
	for frame in os.listdir(directory):
		name, extension = os.path.splitext(frame)
		if extension == ".png":
			path = os.path.join(directory, frame)
			img = pygame.image.load(path).convert_alpha()
			animation.append(img)
	return animation


def blitClothes(baseAnim, moveAnim, clothes, swimmingMask=None):
	"""Returns a list of Surfaces, or a tuple if both clothes and swimmingMask are given as arguments"""
	if clothes: clothesImg = pygame.image.load('assets/mobs/%s.png' %(clothes))
	clothedIdleAnim, clothedMoveAnim, swimAnim = [], [], []
	for i in range(len(baseAnim)):
		if clothes:
			frame = baseAnim[i].copy()
			frame.blit(clothesImg, (0, 0))
			clothedIdleAnim.append(frame)
	for i in range(len(moveAnim)):
		if clothes:
			frame = moveAnim[i].copy()
			frame.blit(clothesImg, (0, 0))
			clothedMoveAnim.append(frame)
	if swimmingMask:
		for i in range(len(baseAnim)):
			if clothes:
				frame = clothedMoveAnim[i].copy()
			else:
				frame = baseAnim[i].copy()
			frame.blit(swimmingMask, (0, 0))
			swimAnim.append(frame)
	if clothes and swimmingMask:
		return (clothedIdleAnim, clothedMoveAnim, swimAnim)
	elif swimmingMask:
		return swimAnim
	else:
		return (clothedIdleAnim, clothedMoveAnim)




class Mob(pygame.sprite.Sprite):
	"""Base class for all mobs"""
	def __init__(self, baseMoveSpeed, img, coords, size):
		pygame.sprite.Sprite.__init__(self)
		self.isDead = False
		self.causeOfDeath = None
		self.add(my.allMobs)
		self.animFrame = 0
		if type(img) == list:
			self.animation = img
			self.lastAnimation = self.animation
			self.handleImage()
		else:
			self.image = img
			self.animation = None
		self.direction = 'right'
		self.rect = pygame.Rect(my.map.cellsToPixels(coords), size)
		self.destination = None
		self.baseMoveSpeed = baseMoveSpeed
		self.coords =  coords
		self.tick = randint(1, 19)
		self.initTooltip()
		self.shadow = shadow.Shadow(self, self.animation[0])


	def baseUpdate(self):
		if not self.isDead:
			self.coords =  my.map.pixelsToCell(self.rect.center)
			self.updateMove()
			self.handleImage()
			self.blit()


	def updateMove(self):
		"""Move towards self.destination coords"""
		if self.destination:
			x, y = self.rect.topleft
			destx, desty = my.map.cellsToPixels(self.destination)
			destx += my.CELLSIZE / 4 # so mobs are less obviously gridlike
			destx = int(destx)
			xDistanceToDest = math.fabs(x - destx)
			yDistanceToDest = math.fabs(y - desty)
			# IS AT DESTINATION?
			if x == destx and y == desty:
				self.destination = None
				if self.animation == self.moveAnim:
					self.animation = self.idleAnim
					self.animCount = 0
				return
			# IF NOT, SET UP MOVE DISTANCE
			xMoveDist, yMoveDist = self.moveSpeed, self.moveSpeed
			if xDistanceToDest < self.moveSpeed:
				xMoveDist = xDistanceToDest
			if yDistanceToDest < self.moveSpeed:
				yMoveDist = yDistanceToDest
			# If moving diagonally, only move half as far in x and half as far in y
			movex, movey = True, True
			if x == destx: movex = False
			if y == desty: movey = False
			if (movex and movey) and xMoveDist == self.moveSpeed and yMoveDist == self.moveSpeed:
				xMoveDist = math.ceil(self.moveSpeed / 2)
				yMoveDist = math.ceil(self.moveSpeed / 2)
			# AND MOVE
			if x < destx:   movex = xMoveDist
			elif x > destx: movex = -xMoveDist
			if y < desty:   movey = yMoveDist
			elif y > desty: movey = -yMoveDist
			self.rect.move_ip(movex, movey)
			if self.animation == self.idleAnim:
				self.animation = self.moveAnim
				if self.animFrame > len(self.idleAnim) - 1:
					self.animFrame = 0
			if movex > 0:
				self.direction = 'right'
			elif movex < 0:
				self.direction = 'left'
		if randint(0, 100) == 0:
			self.moveSpeed = randint(self.baseMoveSpeed - 1, self.baseMoveSpeed + 1)
		if self.moveSpeed == 0:
			self.moveSpeed = 1


	def die(self):
		"""Pretty self explanatory really. Kick the bucket."""
		if self.occupation == None: self.stopCarryingJob()
		elif self.occupation == 'builder': self.removeSiteReservation()
		elif self.occupation == 'woodcutter': self.stopWoodcutterJob()
		self.kill()
		self.isDead = True
		Corpse((self.rect.centerx, self.rect.bottom + 5), pygame.image.load('assets/mobs/dude.png'),
				 self.name, self.causeOfDeath)


	def blit(self):
		"""Blit to surf, which is overlayed onto my.map.map"""
		if self.rect.colliderect(my.camera.viewArea):
			my.surf.blit(self.image, self.rect)


	def handleImage(self):
		"""If has animation, update self.image"""
		if self.animation:
			if self.animation != self.lastAnimation:
				if self.animFrame > len(self.animation) - 1:
					self.animFrame = 0
			self.image = self.animation[self.animFrame]
			if my.ticks % 6 == 0:
				self.animFrame += 1
			if self.animFrame > len(self.animation) - 1:
				self.animFrame = 0
			self.lastAnimation = self.animation


	def initTooltip(self):
		"""Initialises a tooltip that appears when the mob is hovered"""
		tooltipPos = (self.rect.right + ui.GAP, self.rect.top)
		self.tooltip = ui.Tooltip('BLANK TOOLTIP', tooltipPos)


	def handleTooltip(self):
		"""Updates a tooltip that appears when the mob is hovered"""
		self.tooltip.rect.topleft = (self.rect.right + ui.GAP, self.rect.top)
		self.tooltip.simulate(self.rect.collidepoint(my.input.hoveredPixel), True)


	def handleShadow(self):
		"""A nice shadow cast by the sun (which moves along the top of the map)"""
		self.shadow.draw(my.surf, my.sunPos)



class Human(Mob):
	"""Base class for humans, with methods for the different occupations."""
	idleAnimation = loadAnimationFiles('assets/mobs/idle')
	moveAnimation = loadAnimationFiles('assets/mobs/move')
	swimmingMask = pygame.image.load('assets/mobs/swimmingMask.png').convert_alpha()
	swimAnim = blitClothes(idleAnimation, moveAnimation, None, swimmingMask)
	builderIdleAnim, builderMoveAnim, builderSwimAnim = blitClothes(idleAnimation, moveAnimation, 'builder', swimmingMask)
	buildAnim = loadAnimationFiles('assets/mobs/build')
	woodcutterIdleAnim, woodcutterMoveAnim, woodcutterSwimAnim = blitClothes(idleAnimation, moveAnimation, 'woodcutter', swimmingMask)
	chopAnim = loadAnimationFiles('assets/mobs/chop')
	fishermanIdleAnim, fishermanMoveAnim, fishermanSwimAnim = blitClothes(idleAnimation, moveAnimation, 'fisherman', swimmingMask)
	fishAnim = loadAnimationFiles('assets/mobs/fish')
	minerIdleAnim, minerMoveAnim, minerSwimAnim = blitClothes(idleAnimation, moveAnimation, 'miner', swimmingMask)
	mineAnim = loadAnimationFiles('assets/mobs/mine')
#   BASE CLASS
	def __init__(self, coords, occupation=None):
		pygame.sprite.Sprite.__init__(self)
		self.idleAnim, self.moveAnim = Human.idleAnimation, Human.moveAnimation
		if occupation is None:
			self.animation = self.idleAnim
		self.size = (10, 20)
		self.baseMoveSpeed = my.HUMANMOVESPEED
		self.moveSpeed = my.HUMANMOVESPEED
		self.changeOccupation(occupation)
		Mob.__init__(self, self.baseMoveSpeed, self.animation, coords, self.size)
		self.name = random.choice(my.FIRSTNAMES) + ' ' + random.choice(my.LASTNAMES)
		self.tooltip.text = self.name
		self.initEmotions()
		self.carrying = None
		self.lastDestItem = None
		self.destinationItem = None
		self.destinationSite = None
		self.add(my.allHumans)


	def update(self):
		if not self.isDead:
			self.baseUpdate()
			self.updateEmotions()
			if self.occupation is None:
				self.updateSerf()
			if self.occupation == 'builder':
				self.updateBuilder()
			if self.occupation == 'woodcutter':
				self.updateWoodcutter()
			if self.occupation == 'fisherman':
				self.updateFisherman()
			if self.occupation == 'miner':
				self.updateMiner()
			if self.rect.collidepoint(my.input.hoveredPixel) and my.input.mousePressed == 2:
				self.occupation = 'miner'
				self.initMiner()
			if my.map.cellType(self.coords) == 'water' and self.animation == self.moveAnim:
				self.animation = self.swimAnim
			elif my.map.cellType(self.coords) != 'water' and self.animation == self.swimAnim:
				self.animation = self.idleAnim


	def initEmotions(self):
		"""Initialise the human's wants and needs"""
		self.happiness = my.STARTINGHAPPINESS
		self.hunger = my.STARTINGHUNGER + randint(-100, 100)
		self.lastHunger = self.hunger
		bubblePos = (self.rect.centerx, self.rect.top - my.BUBBLEMARGIN)
		self.intention = None
		self.thought = None
		self.thoughtIsUrgent = False
		self.bubble = ThoughtBubble(self.thought, bubblePos, self.thoughtIsUrgent)


	def updateEmotions(self):
		"""Update the human's wants and needs, and kills it if need be!"""
		# HUNGER
		self.hunger -= 1
		if self.hunger < my.HUNGERWARNING:
			self.thought = 'hungry'
			if not self.intention == 'find food': # ^ is hungry or eating?
				self.goGetFood()
				self.thoughtIsUrgent = False
			if self.hunger < my.HUNGERURGENT:
				self.thoughtIsUrgent = True
		elif self.thought == 'eating' and self.hunger > my.FULLMARGIN:
			self.intention = None
		if self.hunger < 1: # starved to death?
			self.causeOfDeath = 'starved to death'
			self.die()
		self.lastHunger = self.hunger

		# THOUGHTBUBBLE
		bubblePos = (self.rect.left + ui.GAP, self.rect.top - my.BUBBLEMARGIN)
		self.bubble.update(self.thought, bubblePos, self.thoughtIsUrgent)
		if self.intention == 'working':
			self.thought = 'working'
		if self.thought is None:
			thoughtText = 'chillaxing'
		else:
			thoughtText = self.thought
		if self.thoughtIsUrgent:
			urgency = 'very '
		else: urgency = ''
		self.tooltip.text = self.name + ' is ' + urgency + thoughtText


	def goGetFood(self, specificSite=None):
		"""Find the nearest food place wiht slots and go and eat there. If specificSite, go there instead"""
		site = None
		if not specificSite:
			sites = my.map.findNearestBuildings(self.coords, my.foodBuildingsWithSpace)
			if sites:
				site = sites[0]
		elif specificSite:
			site = specificSite
		if site:
			self.destination = random.choice(site.AOEcoords)
			self.intention = 'find food'
			self.thought = 'hungry'
			self.stopJob()


	def changeOccupation(self, newOccupation):
		"""Change occupation and stop any previous jobs"""
		try:
			if self.occupation:
				self.stopJob()
				self.remove(OCCUPATIONGROUPS[str(self.occupation)])
		except AttributeError:
			pass
		self.add(OCCUPATIONGROUPS[str(newOccupation)])
		self.occupation = newOccupation
		if self.occupation == 'builder':
			self.initBuilder()
		elif self.occupation == 'woodcutter':
			self.initWoodcutter()
		elif self.occupation == 'fisherman':
			self.initFisherman()
		elif self.occupation == 'miner':
			self.initMiner()


	def stopJob(self):
		"""Stop the current job, for any occupation"""
		if self.intention == 'working':
			self.intention, self.thought, self.destination = None, None, None
		if self.occupation is None:
			self.stopCarryingJob()
		if self.occupation == 'builder':
			self.removeSiteReservation()
			self.building, self.destinationSite = None, None
		elif self.occupation == 'woodcutter':
			self.stopWoodcutterJob()
		elif self.occupation == 'fisherman':
			self.stopFishingJob()
		elif self.occupation == 'miner':
			self.stopMiningJob()


#   SERF
	def updateSerf(self):
		"""A human without an occupation who carries items around"""
		if not self.carrying and my.tick[self.tick]:
			self.findItem()
		if self.carrying:
			self.tooltip.text += ' and carrying %s %s' %(self.carrying.quantity, self.carrying.name)
			self.carry()
			if self.carrying:
				x, y = self.rect.center
				my.surf.blit(self.carrying.carryImage, (x - 3, y))
		if self.lastDestItem and self.lastDestItem != self.destinationItem:
			self.lastDestItem.reserved = False
		self.lastDestItem = self.destinationItem


	def findItem(self):
		"""Find the nearest unreserved item"""
		if self.intention in [None, 'working']:
			if self.destinationItem and self.destinationItem.reserved not in [self, None]:
				if self.destination == self.destinationItem.coords:
					self.destination = None
				self.destinationItem = None
			# find item
			done = False
			items = my.map.findNearestBuildings(self.coords, my.itemsOnTheFloor)
			if items:
				for item in items:
					if item.name == 'fish' and (not item.reserved or item.reserved == self):
						if self.isStorageSpace(my.fishMongers, item.quantity):
							self.destination = item.coords
							self.destinationItem = item
							item.reserved = self
							self.intention = 'working'
							done = True
						else:
							my.statusMessage = "No storage space for %s" %(item.name)
						if done: break
					if not item.reserved or item.reserved == self:
						if self.isStorageSpace(my.storageBuildingsWithSpace, item.quantity):
							self.destination = item.coords
							self.destinationItem = item
							item.reserved = self
							self.intention = 'working'
							done = True
						else:
							my.statusMessage = "No storage space for %s" %(item.name)
					if done: break
		if self.destinationItem and self.rect.colliderect(self.destinationItem.rect) \
				and self.destinationItem.reserved == self: # pick up item
			self.carrying = self.destinationItem
			self.destinationItem = None
			self.carrying.beingCarried = True


	def carry(self):
		"""Carry the item to the nearest storage building with space"""
		if self.intention in [None, 'working'] and not self.destinationSite:
			if self.carrying.name == 'fish': # if fish, only send to fishmongers
				fishMongers = my.map.findNearestBuildings(self.coords, my.fishMongers)
				if fishMongers:
					site = fishMongers[0]
					self.intention = 'working'
					self.destinationSite = site
					self.destination = self.destinationSite.coords
					return
				else:
					my.statusMessage = 'Build a fishmongers!'
				return
			# item is not fish....
			sites = my.map.findNearestBuildings(self.coords, my.storageBuildingsWithSpace)
			done = False
			for site in sites:
				if site.totalStored + self.carrying.quantity < site.storageCapacity:
					self.intention = 'working'
					self.destinationSite = site
					self.destination = self.destinationSite.coords
				if done: break
			if not self.destinationSite:
				my.statusMessage = "No storage space for %s" %(self.carrying.name)
				self.intention = None
				self.stopCarryingJob()
				return
		self.carrying.reserved = self
		# STORE ITEM
		if self.destinationSite and self.coords == self.destinationSite.coords:
			self.destinationSite.storeResource(self.carrying.name, self.carrying.quantity)
			self.carrying.kill()
			self.stopCarryingJob()


	def stopCarryingJob(self):
		if self.destinationItem:
			self.destinationItem.reserved = None
			self.destinationItem = None
		self.destinationSite = None
		if self.carrying:
			self.carrying.reserved = None
			self.carrying.coords = self.coords
			self.carrying.beingCarried = False
			self.carrying = None


	def isStorageSpace(self, buildingGroup, quantity):
		"""Checks if there will be enough storage space in any building in buildingGroup"""
		if not len(buildingGroup):
			return False
		for building in buildingGroup.sprites():
			if building.totalStored + quantity <= building.storageCapacity:
				return True
		return False


#	BUILDER
	def initBuilder(self):
		"""Finds the nearest construction site and constructs it."""
		self.idleAnim = Human.builderIdleAnim
		self.moveAnim = Human.builderMoveAnim
		self.swimAnim = Human.builderSwimAnim
		self.animation = self.idleAnim
		self.destination = None
		self.building = None
		self.destinationSite = None
		self.lastDestination = None


	def updateBuilder(self):
		if not self.isDead:
			if self.building is None and my.tick[self.tick]:
				self.findConstructionSite()
			self.build()
			if self.destinationSite and my.builtBuildings.has(self.destinationSite):
				self.removeSiteReservation()
				self.destination = None
				self.intention = None
			if (self.destinationSite and self.destination) or self.building:
				self.thought = 'working'
				self.intention = 'working'
			elif self.thought == 'working': # just finished work
				self.thought = None
				self.thoughtIsUrgent = False
			if self.intention == 'working' and (not self.destination or not self.building):
				self.intention is None
			self.lastDestination = self.destination


	def findConstructionSite(self):
		"""Find nearest free cell in a site and set as destination"""
		done = False
		sites = my.map.findNearestBuildings(self.coords, my.buildingsUnderConstruction)
		if sites and (self.intention is None or self.intention == 'working'):
			for site in sites:
				for x in range(len(site.buildersPositions)):
					for y in range(len(site.buildersPositions[0])):
						if done: break
						if site.buildersPositions[x][y] is None:
							# go to, and reserve a place at, the site
							self.destination = site.buildersPositionsCoords[x][y]
							site.buildersPositions[x][y] = self
							if (self.destination != self.lastDestination) or (self.intention not in 'working'):
								self.removeSiteReservation()
							self.destinationSite = site
							self.buildPosx, self.buildPosy = x, y
							done = True
						if done: break
					if done: break
				if done: break


	def removeSiteReservation(self):
		"""Removes the reserved spot at the lost construction site"""
		if self.destinationSite:
			self.destinationSite.buildersPositions[self.buildPosx][self.buildPosy] = None
			self.building = None


	def build(self):
		"""If at site, construct it. If site is done, look for a new one."""
		done = False
		for site in my.buildingsUnderConstruction:
			for x in range(len(site.buildersPositions)):
				for y in range(len(site.buildersPositions[0])):
					if done: break
					if site.buildersPositionsCoords[x][y] == self.coords:
						self.building = site
						self.destinationSite = None
						self.building.buildProgress += my.CONSTRUCTIONSPEED
						self.intention = 'working'
						done = True
					if done: break
				if done: break
		if not done:
			if self.animation not in [self.idleAnim, self.moveAnim]:
				self.animation = self.idleAnim
				self.animFrame = 0
			self.building = None
		else:
			if self.animation != Human.buildAnim:
				self.animation = Human.buildAnim
				self.animFrame = 0
		if my.builtBuildings.has(self.building):
			self.building = None
			self.intention = None


#	WOODCUTTER
	def initWoodcutter(self):
		"""Chops down the nearest tree in my.designatedTrees"""
		self.occupation = 'woodcutter'
		self.idleAnim = Human.woodcutterIdleAnim
		self.moveAnim = Human.woodcutterMoveAnim
		self.swimAnim = Human.woodcutterSwimAnim
		self.animation = self.idleAnim
		self.chopping = False
		self.destinationSite = None
		self.lastSite = self.destinationSite


	def updateWoodcutter(self):
		if self.intention in [None, 'working'] and not self.chopping and my.tick[self.tick]:
			self.intention = 'working'
			self.findTree()
		if self.destinationSite and self.coords == self.destinationSite.coords:
			self.chopping = True
			self.destinationSite.chop()
			if self.destinationSite.isDead:
				self.destinationSite = None
				self.intention, self.thought = None, None
				self.chopping = False
		else:
			self.chopping = False
			if self.animation not in [self.idleAnim, self.moveAnim]:
				self.animation = self.idleAnim
				self.animFrame = 0
		if self.chopping:
			self.animation = Human.chopAnim
		self.lastSite = self.destinationSite


	def findTree(self):
		"""Find nearest unreserved tree and go there"""
		if my.designatedTrees:
			sites = my.map.findNearestBuildings(self.coords, my.designatedTrees)
			if sites:
				done = False
				for site in sites:
					if not site.reserved or site.reserved == self:
						self.destinationSite = site
						self.destination = self.destinationSite.coords
						self.destinationSite.reserved = self
						self.intention = 'working'
						if self.lastSite and self.lastSite != self.destinationSite:
							self.lastSite.reserved = False
						done = True
					if done: return
		self.thought = None
		self.intention = None


	def stopWoodcutterJob(self):
		if self.destinationSite:
			self.destinationSite.reserved = False
			self.destinationSite = None
		self.chopping = False


#   FISHERMAN
	def initFisherman(self):
		"""Goes to the nearest free fishing boat seat and occasionally spawns a Fish() item"""
		self.occupation = 'fisherman'
		self.idleAnim = Human.fishermanIdleAnim
		self.moveAnim = Human.fishermanMoveAnim
		self.swimAnim = Human.fishermanSwimAnim
		self.animation = self.idleAnim
		self.destinationSite = None
		self.fishing = None
		self.lastSite = None
		self.seatCoords = None


	def updateFisherman(self):
		if not self.destinationSite and len(my.fishOnTheFloor) < my.MAXFISHONFLOOR\
										and self.intention in ['working', None] and my.tick[self.tick]:
			self.findFishingSpot()
		elif self.destinationSite and len(my.fishOnTheFloor) < my.MAXFISHONFLOOR:
			self.fish()
		if len(my.fishOnTheFloor) >= my.MAXFISHONFLOOR:
			self.stopFishingJob()
		self.lastSite = self.destinationSite


	def findFishingSpot(self):
		"""Find nearest unreserved fishing boat seat and go there"""
		sites = my.map.findNearestBuildings(self.coords, my.fishingBoats)
		if sites:
			done = False
			for site in sites:
				for seatCoords in site.seats.keys():
					if not site.seats[seatCoords] or site.seats[seatCoords] == self:
						self.destinationSite = site
						self.destination = seatCoords
						self.seatCoords = seatCoords
						site.seats[seatCoords] = self
						self.intention = 'working'
						if self.lastSite and self.lastSite != self.destinationSite:
							self.lastSite.reserved = False
						done = True
					if done: return
		self.thought = None
		self.intention = None
		

	def fish(self):
		"""If on seat, fish (occasionally spawn a Fish() item)"""
		if self.intention == 'working' and self.coords == self.seatCoords:
			if not self.animation == Human.fishAnim:
				self.animation = Human.fishAnim
				self.animCount = 0
			if randint(0, my.FISHFREQUENCY) == 0:
				x, y = self.coords
				item.Fish(randint(my.FISHPERFISH - 20, my.FISHPERFISH + 20),
						  (randint(x - 1, x + 1), randint(y - 1, y + 1)))
		elif self.animation == Human.fishAnim:
			self.animation = self.idleAnim
			self.animCount = 0


	def stopFishingJob(self):
		if self.destinationSite:
			self.destinationSite.seats[self.seatCoords] = None
			self.destinationSite = None
		self.seatCoords = None
		if self.animation == Human.fishAnim:
			self.animation = self.idleAnim
			self.animCount = 0


#   MINER
	def initMiner(self):
		"""Mines designated stone and ore, dropping Stone() and Ore() items"""
		self.occupation = 'miner'
		self.idleAnim = Human.minerIdleAnim
		self.moveAnim = Human.minerMoveAnim
		self.swimAnim = Human.minerSwimAnim
		self.animation = self.idleAnim
		self.destinationSeam = None
		self.mining = False
		self.lastSeam = None


	def updateMiner(self):
		if (not self.destinationSeam or (my.tick[self.tick] and not self.mining)) and self.intention in [None, 'working']\
					and len(my.oreOnTheFloor) < my.MAXOREONFLOOR:
			self.findMiningSpot()
		elif len(my.oreOnTheFloor) < my.MAXOREONFLOOR: # for performance
			self.mine()
		self.lastSeam = self.destinationSeam


	def findMiningSpot(self):
		if not my.designatedOres:
			if self.intention == 'working':
				self.intention = None
			if self.animation not in [self.idleAnim, self.moveAnim]:
				self.animation = self.idleAnim
				self.animCount = 0
			return
		sites = my.map.findNearestBuildings(self.coords, my.designatedOres)
		if sites:
			done = False
			for site in sites:
				if not site.reserved or site.reserved == self:
					self.destination = site.coords
					self.destinationSeam = site
					site.reserved = self
					self.intention = 'working'
					if self.lastSeam and self.lastSeam != self.destinationSeam:
						self.lastSeam.reserved = False
					done = True
				if done: return
		self.thought = None
		self.intention = None
		if self.animation not in [self.idleAnim, self.moveAnim]:
			self.animation = self.idleAnim
			self.animCount = 0


	def mine(self):
		"""If at seam, mine, occasionally spawning Ore() items"""
		if self.intention == 'working' and self.coords == self.destinationSeam.coords:
			if self.animation != Human.mineAnim:
				self.animation = Human.mineAnim
				self.animCount = 0
			self.destinationSeam.durability -= my.OREMINESPEED
			if self.destinationSeam.durability < 1:
				self.destinationSeam = None
				self.mining = False
				self.intention = None
			elif randint(0, 1000) < map.OREABUNDANCE[self.destinationSeam.mineral]:
				x, y = self.coords
				item.Ore(1, (x + randint(-1, 1), y + randint(-1, 1)), self.destinationSeam.mineral)
		elif self.animation == Human.mineAnim:
			self.animation = self.idleAnim
			self.animCount = 0


	def stopMiningJob(self):
		if self.animation == Human.mineAnim:
			self.animation = self.idleAnim
			self.animCount = 0
		self.mining = False
		if self.destinationSeam:
			self.destinationSeam.reserved = False
			self.destinationSeam = None



class ThoughtBubble:
	"""A visual display of a mob's thoughts, a cloud with an icon in it."""
	bubble = pygame.image.load('assets/mobs/thoughtBubble/bubble.png').convert()
	urgentBubble = pygame.image.load('assets/mobs/thoughtBubble/urgentBubble.png').convert_alpha()
	icons = {}
	for icon in ['None', 'happy', 'sad', 'hungry', 'working']:
		icons[icon] = pygame.image.load('assets/mobs/thoughtBubble/' + icon + '.png')
	animIcons = {}
	for icon in ['eating']:
		animIcons[icon] = loadAnimationFiles('assets/mobs/thoughtBubble/' + icon)

	def __init__(self, thought, pos, isUrgent=False):
		self.alpha = 200
		self.rect = pygame.Rect((0,0), (20, 20))
		self.image = None
		self.animCount = 0
		self.thought = str(thought)
		self.isUrgent = isUrgent
		self.updateSurf()
		self.update(self.thought, pos, self.isUrgent) # blit


	def updateSurf(self):
		"""Called whenever a new thought or urgency is needed"""
		if self.thought in ThoughtBubble.icons.keys():
			self.animated = False
			self.icon = ThoughtBubble.icons[self.thought]
		elif self.thought in ThoughtBubble.animIcons.keys():
			self.animated = True
			if my.ticks % 5 ==0:
				self.animCount += 1
			if self.animCount == len(ThoughtBubble.animIcons[self.thought]):
				self.animCount = 0
			self.icon = ThoughtBubble.animIcons[self.thought][self.animCount]
		if self.isUrgent:
			self.image = ThoughtBubble.urgentBubble.copy()
		else:
			self.image = ThoughtBubble.bubble.copy()
		self.image.blit(self.icon, (0,0))
		self.image.convert_alpha()


	def update(self, thought, pos, isUrgent=False):
		if self.alpha > 0:
			self.alpha -= 5
		if str(thought) != self.thought or isUrgent != self.isUrgent or self.animated:
			self.isUrgent = isUrgent
			self.thought = str(thought)
			self.alpha = 200
			self.updateSurf()
		self.image.set_alpha(self.alpha)
		self.rect.midbottom = pos
		my.surf.blit(self.image, self.rect)



class Corpse(pygame.sprite.Sprite):
	"""Eyecandy spawned when a human dies"""
	image = pygame.image.load('assets/mobs/corpse.png').convert_alpha()
	def __init__(self, pos, livingImage, name, causeOfDeath=None):
		pygame.sprite.Sprite.__init__(self)
		self.add(my.corpses)
		self.pos, self.name, self.causeOfDeath = pos, name, causeOfDeath
		self.animCount = 0 # count down to -90 to animate falling over
		self.livingImage = livingImage
		self.initTooltip()

	def update(self):
		if self.animCount > -90: # fall over
			self.img = pygame.transform.rotate(self.livingImage, self.animCount)
			self.animCount -= 5
		else: self.img = Corpse.image
		my.surf.blit(self.img, self.pos)
		self.handleTooltip()


	def initTooltip(self):
		"""Initialises a tooltip that appears when the mob is hovered"""
		x, y = self.pos
		tooltipPos = (x + ui.GAP * 4, y)
		self.tooltip = ui.Tooltip(self.name + ' ' + self.causeOfDeath, tooltipPos)


	def handleTooltip(self):
		"""Updates a tooltip that appears when the mob is hovered"""
		if my.input.hoveredCell == my.map.pixelsToCell(self.pos):
			isHovered = True
		else:
			isHovered = False
		self.tooltip.simulate(isHovered, True)




class PassiveAnimal(Mob):
	"""Base class for animals that do not interact with humans"""
	def __init__(self, baseMoveSpeed, img, coords, size):
		if coords == 'randomGrass':
			while True:
				x, y = (randint(0, my.MAPXCELLS - 1), randint(0, my.MAPYCELLS - 1))
				if my.map.map[x][y] == 'grass':
					coords = (x, y)
					break
		Mob.__init__(self, baseMoveSpeed, img, coords, size)
		self.add(my.animals)


	def animalUpdate(self):
		if self.rect.colliderect(my.camera.viewArea):
			if randint(0, 50) == 0:
				x, y = self.coords
				for i in range(5): # prefer walking onto grass tiles
					newx, newy =  x + randint(-2, 2), y + randint(-2, 2)
					if my.map.inBounds((newx, newy)) and my.map.map[newx][newy] == 'grass' or i == 5:
						self.destination = (newx, newy)
						break
			self.baseUpdate()


class Rabbit(PassiveAnimal):
	"""Hop, hop, hop"""
	def __init__(self):
		self.animLeft = loadAnimationFiles('assets/mobs/rabbit')
		self.animRight = []
		for frame in self.animLeft:
			self.animRight.append(pygame.transform.flip(frame, 1, 0))
		self.idleAnim = self.animLeft
		self.moveAnim = self.idleAnim
		self.moveSpeed = 1
		PassiveAnimal.__init__(self, 1, self.idleAnim, 'randomGrass', (10, 10))


	def update(self):
		self.animalUpdate()
		if self.direction == 'left':
			self.idleAnim, self.moveAnim = self.animLeft, self.animLeft
		else:
			self.idleAnim, self.moveAnim = self.animRight, self.animRight


class Deer(PassiveAnimal):
	"""Silent but deadly. But not deadly."""
	def __init__(self):
		self.animLeft = loadAnimationFiles('assets/mobs/deer')
		self.animRight = []
		for frame in self.animLeft:
			img = pygame.transform.flip(frame, 1, 0)
			self.animRight.append(img)
		self.idleAnim = self.animLeft
		self.moveAnim = self.idleAnim
		self.moveSpeed = 1
		PassiveAnimal.__init__(self, 1, self.idleAnim, 'randomGrass', (15, 15))

	def update(self):
		self.animalUpdate()
		if self.direction == 'left':
			self.idleAnim, self.moveAnim = self.animLeft, self.animLeft
		else:
			self.idleAnim, self.moveAnim = self.animRight, self.animRight
