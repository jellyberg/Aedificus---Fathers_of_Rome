# AEDIFICUS: FATHERS OF ROME
# by Adam Binks   www.github.com/jellyberg/Aedificus---Fathers_of_Rome
# Read the devblog on Tumblr: bit.ly/Aedificus

import pygame, random, my

SOUND = {}
for filename in ['chop1', 'chop2', 'hammering1', 'hammering2', 'hammering3', 'hammering4', 'hammering5',
				 'hammering6', 'treeFalling', 'thud', 'splash', 'groan', 'mining1', 'mining2', 'mining3',
				 'mining4', 'click', 'tick', 'error', 'pop', 'eating1', 'eating2', 'eating3', 'clunk',
				 'achievement', 'growl1', 'growl2', 'growl3', 'wolfHowl', 'explosion', 'swish', 'sword1',
				 'sword2', 'sword3', 'sword4']: # .wav files only
	SOUND[filename] = pygame.mixer.Sound('assets/sounds/%s.wav' %(filename))

def play(sound, volume=0.8, varyVolume=True ,loops=0):
	"""Plays the given sound"""
	if not my.muted:
		if varyVolume:
			volume -= random.uniform(0.0, 0.2)
			if volume < 0.1: volume == 0.1
			SOUND[sound].set_volume(volume)
		SOUND[sound].play(loops)