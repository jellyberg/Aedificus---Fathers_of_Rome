# AEDIFICUS: FATHERS OF ROME
# by Adam Binks   www.github.com/jellyberg/Aedificus---Fathers_of_Rome
# Read the devblog on Tumblr: bit.ly/Aedificus

import pygame, my, logic, input, ui, os, math

os.environ['SDL_VIDEO_CENTERED'] = '1'
pygame.mixer.pre_init(44100,-16,2, 1024)
pygame.init()
pygame.display.set_icon(pygame.image.load('assets/ui/icon.png'))
pygame.display.set_caption('Aedificus: Fathers of Rome')

my.screen.blit(my.loadingScreen, (0, 0))
pygame.display.update()

my.gameRunning = False

def run():
	my.input = input.Input()
	menu = EmbarkMenu()
	my.transition = -1 # fade between menus/game states

	while True:
		deltaTime = my.FPSCLOCK.tick(my.FPS)
		if my.gameRunning:
			try:
				handler.update(deltaTime / 1000.0)
			except:
				handler = logic.Handler()
	
		else:
			menu.update()

		if my.transition == 'begin':
			my.transition = 255
		if my.transition > 0:
			my.transition -= 3 * deltaTime / 17
			my.lastSurf.set_alpha(my.transition)
			my.screen.blit(my.lastSurf, (0, 0))

		pygame.display.update()
		pygame.display.set_caption('Aedificus: Fathers of Rome' + ' ' * 10 + 'FPS: ' + str(int(my.FPSCLOCK.get_fps())))



class EmbarkMenu:
	def __init__(self):
		self.sliders = []
		self.sliderData = [{'label': 'Number of mountains', 'valRange': (5 , 20), 'default': 10},
							{'label': 'Number of rivers', 'valRange': (5 , 40), 'default': 20},
							{'label': 'Tree density', 'valRange': (50 , 150), 'default': 125}]
		i = 0
		for data in self.sliderData:
			self.sliders.append(ui.Slider((int(my.WINDOWWIDTH/2 - ui.Slider.size[0]/2), 200 + i*ui.Slider.size[1] + i*ui.GAP),
								 data['valRange'], data['label'], data['default']))
			i += 1

		self.backButton = ui.Button('Back', 0, (my.HALFWINDOWWIDTH - 100, my.WINDOWHEIGHT), 1, 1)
		self.embarkButton = ui.Button('Embark', 0, (my.HALFWINDOWWIDTH + 20, my.WINDOWHEIGHT), 1, 1)

		self.logoImg = pygame.image.load('assets/aedificus title smaller.png').convert_alpha()
		self.logoRect = self.logoImg.get_rect()
		self.logoRect.midtop = (my.HALFWINDOWWIDTH, -155)

		self.animateOut = False


	def update(self):
		my.input.get()
		my.screen.fill(my.PASTELBLUE)

		for slider in self.sliders:
			value = slider.update()
			if slider.label == 'Number of mountains':
				my.NUMMOUNTAINS = value
			elif slider.label == 'Number of rivers':
				my.NUMRIVERS = value
			elif slider.label == 'Tree density':
				my.TREEFREQUENCY = 200 - value

		self.embarkButton.simulate(my.input)
		if self.embarkButton.isClicked:
			self.animateOut = True

		self.backButton.simulate(my.input)
		if self.backButton.isClicked: my.input.terminate()

		my.screen.blit(self.logoImg, self.logoRect)


		# ANIMATE
		if self.animateOut: # animate out
			animateDone = True
			if self.backButton.rect.y < my.WINDOWHEIGHT - 1:
				animateDone = False
				self.backButton.rect.y += (my.WINDOWHEIGHT + 50 - self.backButton.rect.y) * 0.1
				self.embarkButton.rect.y = self.backButton.rect.y
			if self.logoRect.y > -160:
				animateDone = False
				self.logoRect.y -= math.fabs(-180 - self.logoRect.y) * 0.1

		else: # animate in
			if self.backButton.rect.y > my.HALFWINDOWWIDTH - 100:
				self.backButton.rect.y -= math.fabs(my.WINDOWHEIGHT * 0.75 - self.backButton.rect.y) * 0.1
				self.embarkButton.rect.y = self.backButton.rect.y

			if self.logoRect.y != 30:
				self.logoRect.y += math.fabs(30 - self.logoRect.y) * 0.1

		if self.animateOut and animateDone:
			my.gameRunning = True
			loadingSurf, loadingRect = ui.genText('GENERATING WORLD', (0,0), my.WHITE, ui.MEGAFONT)
			loadingRect.center = (my.HALFWINDOWWIDTH, my.HALFWINDOWHEIGHT)
			my.screen.fill(my.DARKBLUE, pygame.Rect(loadingRect.x - 20, loadingRect.y - 20, 
													loadingRect.width + 40, loadingRect.height + 40))
			my.screen.blit(loadingSurf, loadingRect)

			my.transition = 'begin'
			my.lastSurf = my.screen.copy().convert()



if __name__ == '__main__':
	run()