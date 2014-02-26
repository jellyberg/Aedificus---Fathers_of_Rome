import pygame, my, input, ui, map, building, mob, random
pygame.init()

class Handler:
	"""Keep the main.runGame() function nice and tidy"""
	def __init__(self):
		my.ticks = 0
		my.tick = []
		for i in range(20):
			my.tick.append(False)
		my.map = map.Map()
		my.input = input.Input()
		my.camera = map.Camera()
		my.hud = ui.Hud()
		my.mode = 'look' 
		my.resources = {'wood': my.STARTRESOURCES['wood'], 
						'iron': my.STARTRESOURCES['iron'], 'cheese': my.STARTRESOURCES['cheese']}
		my.maxResources = {'wood': my.STARTMAXRESOURCES['wood'], 
						'iron': my.STARTMAXRESOURCES['iron'], 'cheese': my.STARTMAXRESOURCES['cheese']}
		my.updateSurf = True
		my.gameRunning = True

		self.testBuilders = []
		for i in range(10):
			self.testBuilders.append(mob.Builder((random.randint(0, 20), random.randint(0, 20))))

	def update(self):
		my.input.get()
		building.updateBuildings()
		for builder in self.testBuilders:
			builder.update()
		my.camera.update()
		my.hud.update()
		my.ticks += 1
		for i in range(0, 19):
			if my.ticks % (my.FPS + i):
				my.tick[i] = True
			else:
				my.tick[i] = False

		pygame.display.update()
		my.FPSCLOCK.tick(my.FPS)
		pygame.display.set_caption('Real time strategy' + ' ' * 10 + 'FPS: ' + str(int(my.FPSCLOCK.get_fps())))
		my.input.checkForQuit()

		for key in my.resources.keys():
			if my.resources[key] > my.maxResources[key]:
				my.resources[key] = my.maxResources[key]
			if my.resources[key] < 0:
				my.resources[key] = 0