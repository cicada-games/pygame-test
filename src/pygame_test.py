import pygame as pg
from pygame.locals import *
import os
import sys

#main_dir = os.path.split(os.path.abspath(__file__))[0]
main_dir = sys.argv[1]

def load_image(file):
    """ loads an image, prepares it for play
    """
    file = os.path.join(main_dir, "images", file)
    print(file)
    try:
        surface = pg.image.load(file)
    except pg.error:
        raise SystemExit('Could not load image "%s" %s' % (file, pg.get_error()))
    return surface.convert()

def main():
    SCREENDIM = 640, 480
    
    SCREENRECT = pg.Rect(0, 0, SCREENDIM[0], SCREENDIM[1])
    
    pg.init()
    screen = pg.display.set_mode(SCREENDIM, 0, 24)
    clock = pg.time.Clock()
    
    font = pg.font.Font(None, 32)
    
    images = {}
    for image_filename in os.listdir('images'):
        image_name = image_filename.split('.')[0]
        images[image_name] = load_image(image_filename)
    
    bgdtile = images['grass']
    
    background = pg.Surface(SCREENRECT.size)
    
    background.blit(bgdtile, (0, 0))
        
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                return
        screen.blit(background, (0, 0))
        pg.display.update()
    
if __name__ == '__main__':
    main()
