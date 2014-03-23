"""
Drag the Sun with the mouse to see the shadow change.
"""

import os
import sys
import pygame as pg

import shadow


CELL_SIZE = (50, 50)
SUN_SIZE = (75, 75)
BACKGROUND_COLOR = (240, 240, 255)


class Sun(object):
    def __init__(self, pos):
        self.image = self.make_image()
        self.rect = self.image.get_rect(center=pos)
        self.click = False

    def make_image(self):
        image = pg.Surface(SUN_SIZE).convert_alpha()
        rect = image.get_rect()
        image.fill((0,0,0,0))
        pg.draw.ellipse(image, pg.Color("black"), rect)
        pg.draw.ellipse(image, pg.Color("orange"), rect.inflate(-10,-10))
        return image

    def update(self, screen_rect):
        if self.click:
            self.rect.move_ip(pg.mouse.get_rel())
            self.rect.clamp_ip(screen_rect)

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class Player(pg.sprite.Sprite):
    def __init__(self, pos):
        pg.sprite.Sprite.__init__(self)
        self.image = self.make_image()
        self.rect = self.image.get_rect(center=pos)
        self.shadow = shadow.Shadow(self)

    def make_image(self):
        image = pg.Surface(CELL_SIZE).convert_alpha()
        image.fill(pg.Color("Red"))
        image.fill((0,0,0,0), image.get_rect().inflate(-30,-30))
        pg.draw.circle(image, (0,0,0,0), (15,15), 10)
        return image

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class Control(object):
    def __init__(self, screen_size):
        pg.init()
        os.environ["SDL_VIDEO_CENTERED"] = "TRUE"
        pg.display.set_caption("Drag sun to move shadow")
        self.screen = pg.display.set_mode(screen_size)
        self.screen_rect = self.screen.get_rect()
        self.clock = pg.time.Clock()
        self.fps = 60.0
        self.done = False
        self.player = Player(self.screen_rect.center)
        self.sun = Sun((50,50))

    def event_loop(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.done = True
            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                if self.sun.rect.collidepoint(event.pos):
                    self.sun.click = True
                    pg.mouse.get_rel()
            elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
                self.sun.click = False

    def update(self):
        self.sun.update(self.screen_rect)

    def draw(self):
        self.screen.fill(BACKGROUND_COLOR)
        self.sun.draw(self.screen)
        self.player.shadow.draw(self.screen, self.sun.rect.center)
        self.player.draw(self.screen)

    def main_loop(self):
        while not self.done:
            self.event_loop()
            self.update()
            self.draw()
            pg.display.update()
            self.clock.tick(self.fps)


if __name__ == "__main__":
    app = Control((500,500))
    app.main_loop()
    pg.quit()
    sys.exit()
