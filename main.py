import pygame, my, input, ui, map, building
from pygame.locals import *

pygame.init()
pygame.display.set_caption('Real time strategy')

loadingScreen = pygame.image.load('assets/loadingScreen.png').convert_alpha()
my.screen.blit(loadingScreen, (0, 0))
pygame.display.update()

def main():
	runGame()


def runGame():
	my.map = map.Map()
	my.input = input.Input()
	my.camera = map.Camera()
	my.camera.update()
	my.hud = ui.Hud()

	my.resources = {'wood': 5, 'iron': 2, 'cheese': 250}

	testBuilding = building.Building('hut', 'hut.png', 2, 2)
	testButton = ui.Button('Click me', 0, (5, my.WINDOWHEIGHT - 60), 1, 0, 0, 'This is a tooltip that spans multiple lines.')

	while True:
		my.input.get()
		testBuilding.blit()
		my.camera.update()
		my.hud.update()
		testButton.simulate(my.input)
		pygame.display.update()
		my.FPSCLOCK.tick(my.FPS)
		my.input.checkForQuit()


if __name__ == '__main__':
	main()