import pygame, my, input, ui, map, building, mob, item, random, sound


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
		my.mode = 'look' 
		my.resources = {'wood': my.STARTRESOURCES['wood'], 'iron': my.STARTRESOURCES['iron'], 
						'coal': my.STARTRESOURCES['coal']}
		my.updateSurf = True
		my.gameRunning = True
		self.sunx = int(my.MAPWIDTH / 2)
		my.sunPos = (self.sunx, my.MAPHEIGHT + 10)
# HUMANS FOR TESTING
		for i in range(3):
			mob.Human((random.randint(int(my.MAPXCELLS / 2) - 5, int(my.MAPXCELLS / 2) + 5),
					   random.randint(int(my.MAPYCELLS / 2) - 5, int(my.MAPYCELLS / 2) + 5)), None)
		for i in range(0):
			mob.Human((random.randint(int(my.MAPXCELLS / 2) - 5, int(my.MAPXCELLS / 2) + 5),
					   random.randint(int(my.MAPYCELLS / 2) - 5, int(my.MAPYCELLS / 2) + 5)), 'woodcutter')
		for i in range(0):
			mob.Human((random.randint(int(my.MAPXCELLS / 2) - 5, int(my.MAPXCELLS / 2) + 5),
					   random.randint(int(my.MAPYCELLS / 2) - 5, int(my.MAPYCELLS / 2) + 5)), 'builder')
		for i in range(0):
			mob.Human((random.randint(int(my.MAPXCELLS / 2) - 5, int(my.MAPXCELLS / 2) + 5),
					   random.randint(int(my.MAPYCELLS / 2) - 5, int(my.MAPYCELLS / 2) + 5)), 'miner')
		for i in range(0):
			mob.Human((random.randint(int(my.MAPXCELLS / 2) - 5, int(my.MAPXCELLS / 2) + 5),
					   random.randint(int(my.MAPYCELLS / 2) - 5, int(my.MAPYCELLS / 2) + 5)), 'fisherman')

		for i in range(20):
			mob.Rabbit()
			mob.Deer()


	def update(self):
		my.input.get()
		pauseText = ''
		if pygame.locals.K_SPACE in my.input.unpressedKeys:
			my.paused = not my.paused
			self.screenCache = my.screen.copy()
			self.pauseSurf = pygame.Surface((my.WINDOWWIDTH, my.WINDOWHEIGHT))
			self.pauseTextSurf, self.pauseTextRect = ui.genText('PAUSED (press space to unpause)', (10, 10), my.WHITE, ui.MEGAFONT)
			self.pauseTextRect.center = (int(my.WINDOWWIDTH / 2), int(my.WINDOWHEIGHT / 2))

		if not my.paused:
			self.pauseAlpha = 0
			my.surf.blit(my.map.surf, (0, 0))

			my.ticks += 1
			for i in range(1, 20):
				if my.ticks % i == 0:
					my.tick[i] = True
				else:
					my.tick[i] = False

			self.sunx += my.SUNMOVESPEED
			if self.sunx > my.MAPWIDTH: self.sunx = -30
			my.sunPos = (self.sunx, my.MAPHEIGHT + 10)

			my.map.update()
			building.updateBuildings()
			item.update()
			mob.updateMobs()
			my.hud.updateWorldUI()
			my.camera.update()
			my.hud.updateHUD()

			# TEMP
			if pygame.locals.K_q in my.input.unpressedKeys:
				ui.StatusText('this is a test')

		else:
			if self.pauseAlpha < 150: self.pauseAlpha += 5
			self.pauseSurf.fill(my.DARKGREY)
			self.pauseSurf.set_alpha(self.pauseAlpha)
			self.pauseSurf.blit(self.pauseTextSurf, self.pauseTextRect)
			my.screen.blit(self.screenCache, (0, 0))
			my.screen.blit(self.pauseSurf, (0, 0))
			pauseText = '   **PAUSED**'

		pygame.display.update()
		my.FPSCLOCK.tick(my.FPS)
		pygame.display.set_caption('Real time strategy' + ' ' * 10 + 'FPS: ' + str(int(my.FPSCLOCK.get_fps())) + pauseText)

		for key in my.resources.keys(): # DON'T FIX THE BUGS, HIDE 'EM!
			if my.resources[key] < 0:
				my.resources[key] = 0
