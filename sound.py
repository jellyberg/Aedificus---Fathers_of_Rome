import pygame, random

SOUND = {}
for filename in ['chop1', 'chop2', 'hammering1', 'hammering2', 'hammering3', 'hammering4', 'hammering5',
				 'hammering6', 'treeFalling', 'thud', 'splash', 'groan', 'mining1', 'mining2', 'mining3',
				 'mining4', 'click', 'error', 'pop']: # .wav files only
	SOUND[filename] = pygame.mixer.Sound('assets/sounds/%s.wav' %(filename))

def play(sound, volume=0.8, loops=0):
	"""Plays the given sound"""
	volume -= random.uniform(0.0, 0.5)
	SOUND[sound].set_volume(volume)
	SOUND[sound].play(loops)