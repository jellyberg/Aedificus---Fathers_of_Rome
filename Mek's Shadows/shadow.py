import pygame as pg


class Shadow(object):
    """
    A class for adding dynamic shadows to 2d-sprites.
    """
    def __init__(self, sprite, image=None):
        self.sprite = sprite
        image = image if image else sprite.image
        self.shadow_strips = self.make_shadow_elements(image)

    def make_shadow_elements(self, image):
        """Split the image into horizontal strips."""
        colorkey = image.get_colorkey()
        transparent = colorkey if colorkey else (0,0,0,0)
        shadow_strips = []
        for j in range(self.sprite.rect.height):
            strip = pg.Surface((self.sprite.rect.width,1)).convert_alpha()
            strip.fill((0,0,0,0))
            for i in range(self.sprite.rect.width):
                pixel = image.get_at((i,j))
                if pixel != transparent:
                    alpha = min(j*5, 255)
                    strip.set_at((i,0), (10,0,10,alpha))
            shadow_strips.append(strip)
        return shadow_strips[::-1]

    def draw(self, surface, sun):
        """Draw each strip of the shadow offsetting the x-axis accordingly."""
        slope = self.get_inverse_slope(sun)
        sign = 1 if sun[1] < self.sprite.rect.centery else -1
        for i,strip in enumerate(self.shadow_strips):
            pos = (self.sprite.rect.x+i*slope*sign,
                   self.sprite.rect.bottom-1+i*sign)
            surface.blit(strip, pos)

    def get_inverse_slope(self, sun):
        """Calculate the inverse slope between the sun and the actor."""
        rise = self.sprite.rect.centery-sun[1]
        run = self.sprite.rect.centerx-sun[0]
        try:
            return run/float(rise)
        except ZeroDivisionError:
            return 0
