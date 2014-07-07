# AEDIFICUS: FATHERS OF ROME
# by Adam Binks   www.github.com/jellyberg/Aedificus---Fathers_of_Rome
# Read the devblog on Tumblr: bit.ly/Aedificus

import pygame, my, ui, map, building, mob, item, random, mission, event


def updateCheats():
	if my.CHEATS['noHunger']:
		my.STARTINGHUNGER = 10000000000000000000000000000000000000000000000000000000000000
	if my.CHEATS['fastActions']:
		my.TREECHOPSPEED = 1000
		my.CONSTRUCTIONSPEED = 1000
	if my.CHEATS['fastMoving']:
		my.HUMANMOVESPEED = 50

class Handler:
	"""Keep the libengine.run() function nice and tidy"""
	def __init__(self):
		my.ticks = 0
		my.tick = []
		for i in range(20):
			my.tick.append(False)

		my.paused = False
		self.pauseAlpha = 0
		my.statusMessage = 'None'

		self.newGame()

		my.hud = ui.Hud()
		my.mode = 'look'
		self.sunx = 0
		my.sunPos = (self.sunx, my.MAPHEIGHT + 10)

		for i in range(20):
			mob.Rabbit()
			mob.Deer()


	def update(self, deltaTime):
		my.UIhover = False
		my.input.get()
		updateCheats()

		if pygame.locals.K_SPACE in my.input.unpressedKeys:
			my.paused = not my.paused
			self.screenCache = my.screen.copy()
			self.pauseSurf = pygame.Surface((my.WINDOWWIDTH, my.WINDOWHEIGHT))
			self.pauseTextSurf, self.pauseTextRect = ui.genText('PAUSED (press space to unpause)', (10, 10), my.WHITE, ui.MEGAFONT)
			self.pauseTextRect.center = (int(my.WINDOWWIDTH / 2), int(my.WINDOWHEIGHT / 2))

		if pygame.locals.K_m in my.input.unpressedKeys:
			my.muted = not my.muted
			if my.muted:
				ui.StatusText('All sounds muted (M to unmute)', None, True)
			if not my.muted:
				ui.StatusText('All earmeltingly beautiful sounds activated', None, True)

		if not my.paused:
			self.pauseAlpha = 0
			my.surf.blit(my.map.surf, (0, 0))

			my.ticks += 1
			for i in range(1, 20):
				if my.ticks % i == 0:
					my.tick[i] = True
				else:
					my.tick[i] = False
			my.dt = deltaTime

			self.sunx += my.SUNMOVESPEED
			if self.sunx > my.MAPWIDTH: self.sunx = -30
			my.sunPos = (self.sunx, my.MAPHEIGHT + 50)

			try:
				my.mission = my.MISSIONS[my.currentMissionNum]
			except IndexError:
				if not my.DEBUGMODE and my.mission is not None:
					ui.StatusText('Congratulations, you completed all missions!')
				my.mission = None

			my.map.update()
			my.eventHandler.update(deltaTime)
			building.updateBuildings(deltaTime)
			item.update()
			mob.updateMobs(deltaTime)
			ui.handleTooltips()
			my.hud.updateWorldUI()
			my.camera.update(deltaTime)
			my.hud.updateHUD(deltaTime)

		else:
			if self.pauseAlpha < 150: self.pauseAlpha += 600 * deltaTime
			self.pauseSurf.fill(my.DARKGREY)
			self.pauseSurf.set_alpha(self.pauseAlpha)
			self.pauseSurf.blit(self.pauseTextSurf, self.pauseTextRect)
			my.screen.blit(self.screenCache, (0, 0))
			my.screen.blit(self.pauseSurf, (0, 0))

		for key in my.resources.keys(): # DON'T FIX THE BUGS, HIDE 'EM!
			if my.resources[key] < 0:
				my.resources[key] = 0


	def newGame(self):
		"""Sets up a brand new game"""
		my.map = map.Map()
		my.map.completeGen()
		my.camera = map.Camera()
		my.eventHandler = event.EventHandler()

		my.resources = {}
		for resourceName in my.STARTRESOURCES.keys():
			my.resources[resourceName] = my.STARTRESOURCES[resourceName]
			my.RESOURCENAMEORDER = ['wood', 'coal', 'iron', 'gold', 'ingot'] # displayed on the screen at all times

		# HUMANS FOR TESTING
		for i in range(1):
			human = mob.Human((int(my.MAPXCELLS / 2), int(my.MAPYCELLS / 2)), 'swordsman')
			human.destination = (random.randint(int(my.MAPXCELLS / 2) - 5, int(my.MAPXCELLS / 2) + 5),
					   random.randint(int(my.MAPYCELLS / 2) - 5, int(my.MAPYCELLS / 2) + 5))
		# for i in range(1):
		# 	mob.DeathWolf((random.randint(int(my.MAPXCELLS / 2) - 5, int(my.MAPXCELLS / 2) + 5),
		# 						random.randint(int(my.MAPYCELLS / 2) - 5, int(my.MAPYCELLS / 2) + 5)))
		for i in range(1):
			mob.Enemy((int(my.MAPXCELLS / 2 + 30), int(my.MAPYCELLS / 2 + 15)))
		for i in range(5):
			item.Sword(1, (random.randint(int(my.MAPXCELLS / 2) - 5, int(my.MAPXCELLS / 2) + 5),
					   random.randint(int(my.MAPYCELLS / 2) - 5, int(my.MAPYCELLS / 2) + 5)))

		mission.initMissions(100) # FOR TESTING