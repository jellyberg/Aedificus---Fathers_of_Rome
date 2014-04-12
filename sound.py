import pygame

SOUND = {}
for filename in []:
	SOUND[filename] = pygame.mixer.sound('%s.wav %(filename)')