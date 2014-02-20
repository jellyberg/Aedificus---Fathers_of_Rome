import pygame, my, map, input
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

	while True:
		my.input.get()
		my.camera.update()
		pygame.display.update()
		my.FPSCLOCK.tick(my.FPS)
		my.input.checkForQuit()


if __name__ == '__main__':
	main()