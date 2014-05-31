import pygame, my, input, ui, map, building, mob, item, random, mission, event


def updateCheats():
	if my.CHEATS['noHunger']:
		my.STARTINGHUNGER = 10000000000000000000000000000000000000000000000000000000000000
	if my.CHEATS['fastActions']:
		my.TREECHOPSPEED = 100
		my.CONSTRUCTIONSPEED = 100
	if my.CHEATS['fastMoving']:
		my.HUMANMOVESPEED = 50

class Handler:
	"""Keep the main.runGame() function nice and tidy"""
	def __init__(self):
		my.ticks = 0
		my.tick = []
		for i in range(20):
			my.tick.append(False)

		my.paused = False
		my.statusMessage = 'None'
		my.map = map.Map()
		my.map.completeGen()
		my.input = input.Input()
		my.camera = map.Camera()
		my.hud = ui.Hud()
		my.eventHandler = event.EventHandler()

		my.mode = 'look' 
		my.resources = {}
		for resourceName in my.STARTRESOURCES.keys():
			my.resources[resourceName] = my.STARTRESOURCES[resourceName]
		my.RESOURCENAMEORDER = ['wood', 'coal', 'iron', 'gold', 'ingot'] # displayed on the screen at all times
		my.updateSurf = True
		my.gameRunning = True
		self.sunx = 0
		my.sunPos = (self.sunx, my.MAPHEIGHT + 10)

		# HUMANS FOR TESTING
		for i in range(5):
			human = mob.Human((int(my.MAPXCELLS / 2), int(my.MAPYCELLS / 2)), None)
			human.destination = (random.randint(int(my.MAPXCELLS / 2) - 5, int(my.MAPXCELLS / 2) + 5),
					   random.randint(int(my.MAPYCELLS / 2) - 5, int(my.MAPYCELLS / 2) + 5))

		for i in range(20):
			mob.Rabbit()
			mob.Deer()

		#for i in range(1):
		#	mob.DeathWolf((random.randint(int(my.MAPXCELLS / 2) - 5, int(my.MAPXCELLS / 2) + 5),
		#						random.randint(int(my.MAPYCELLS / 2) - 5, int(my.MAPYCELLS / 2) + 5)))

		mission.initMissions()


	def update(self):
		my.UIhover = False
		my.input.get()
		updateCheats()

		pauseText = ''
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
			#TEMP
			if pygame.locals.K_0 in my.input.unpressedKeys:
				my.FPS = random.choice([5, 20, 120])
				ui.StatusText('FPS cap: %s' %(my.FPS), None, True)

			self.pauseAlpha = 0
			my.surf.blit(my.map.surf, (0, 0))

			my.ticks += 1
			for i in range(1, 20):
				if my.ticks % i == 0:
					my.tick[i] = True
				else:
					my.tick[i] = False
			millisecondsSinceLastFrame = my.FPSCLOCK.tick(my.FPS)
			deltaTime = millisecondsSinceLastFrame / 1000.0

			self.sunx += my.SUNMOVESPEED
			if self.sunx > my.MAPWIDTH: self.sunx = -30
			my.sunPos = (self.sunx, my.MAPHEIGHT + 50)

			try:
				my.mission = my.MISSIONS[my.currentMissionNum]
			except IndexError:
				if my.mission is not None:
					ui.StatusText('Congratulations, you completed all missions!')
				my.mission = None

			my.map.update()
			my.eventHandler.update()
			building.updateBuildings(deltaTime)
			item.update()
			mob.updateMobs(deltaTime)
			ui.handleTooltips()
			my.hud.updateWorldUI()
			my.camera.update(deltaTime)
			my.hud.updateHUD()

		else:
			if self.pauseAlpha < 150: self.pauseAlpha += 5
			self.pauseSurf.fill(my.DARKGREY)
			self.pauseSurf.set_alpha(self.pauseAlpha)
			self.pauseSurf.blit(self.pauseTextSurf, self.pauseTextRect)
			my.screen.blit(self.screenCache, (0, 0))
			my.screen.blit(self.pauseSurf, (0, 0))
			pauseText = '   **PAUSED**'

		pygame.display.update()
		pygame.display.set_caption('Aedificus: Fathers of Rome' + ' ' * 10 + 'FPS: ' + str(int(my.FPSCLOCK.get_fps())) + pauseText)

		for key in my.resources.keys(): # DON'T FIX THE BUGS, HIDE 'EM!
			if my.resources[key] < 0:
				my.resources[key] = 0
