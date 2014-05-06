import pygame, random, my

SOUND = {}
for filename in ['chop1', 'chop2', 'hammering1', 'hammering2', 'hammering3', 'hammering4', 'hammering5',
				 'hammering6', 'treeFalling', 'thud', 'splash', 'groan', 'mining1', 'mining2', 'mining3',
				 'mining4', 'click', 'tick', 'error', 'pop', 'eating1', 'eating2', 'eating3', 'clunk',
				 'achievement', 'growl1', 'growl2', 'growl3', 'wolfHowl', 'explosion']: # .wav files only
	SOUND[filename] = pygame.mixer.Sound('assets/sounds/%s.wav' %(filename))

def play(sound, volume=0.8, varyVolume=True ,loops=0):
	"""Plays the given sound"""
	if not my.muted:
		if varyVolume:
			volume -= random.uniform(0.0, 0.4)
			if volume < 0.0: volume == 0.1
			SOUND[sound].set_volume(volume)
		SOUND[sound].play(loops)