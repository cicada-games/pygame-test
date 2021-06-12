import pygame as pg
from pygame.locals import *
import os

main_dir = os.path.split(os.path.abspath(__file__))[0]

def load_image(file):
    """ loads an image, prepares it for play
    """
    file = os.path.join(main_dir, "images", file)
    try:
        surface = pg.image.load(file)
    except pg.error:
        raise SystemExit('Could not load image "%s" %s' % (file, pg.get_error()))
    return surface.convert()

pg.init()
screen = pg.display.set_mode((640, 480), 0, 24)
clock = pg.time.Clock()

font = pg.font.Font(None, 32)

images = {}
for image_filename in os.listdir('images'):
    image_name = image_filename.split('[.]')[0]
    images[image_name] = load_image(image_name)

while True:
    pg.event.get() 
    screen.fill(0)
    pg.display.update()

    
