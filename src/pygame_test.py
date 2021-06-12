import pygame as pg
from pygame.locals import *
import os
import sys

main_dir = sys.argv[1] # run like: python3 pygame_test.py $(pwd)

recticle =(
    "           X            ",
    "           X            ",
    "        XXXXXXXX        ",
    "     XXX   X    XXX     ",
    "    X      X       X    ",
    "   X       X        X   ",
    "   X       X        X   ",
    "  X        X         X  ",
    "  X        X         X  ",
    "  X        X         X  ",
    "XXXXXXXXXXXxXXXXXXXXXXXX",
    "  X        X         X  ",
    "  X        X         X  ",
    "  X        X         X  ",
    "  X        X         X  ",
    "   X       X         X  ",
    "   X       X         X  ",
    "    X      X        X   ",
    "     X     X        X   ",
    "     X     X      XX    ",
    "      XX   X    XX      ",
    "        XXXXXXXX        ",
    "           X            ",
    "           X            ",
)

def TestCursor(arrow):
    hotspot = None
    for y, line in enumerate(arrow):
        for x, char in enumerate(line):
            if char in ["x", ",", "O"]:
                hotspot = x, y
                break
        if hotspot is not None:
            break
    if hotspot is None:
        raise Exception("No hotspot specified for cursor '%s'!" % arrow)
    s2 = []
    for line in arrow:
        s2.append(line.replace("x", "X").replace(",", ".").replace("O", "o"))
    cursor, mask = pg.cursors.compile(s2, "X", ".", "o")
    size = len(arrow[0]), len(arrow)
    pg.mouse.set_cursor(size, hotspot, cursor, mask)
    
def load_image(file):
    """ loads an image, prepares it for play
    """
    file = os.path.join(main_dir, "images", file)
    try:
        surface = pg.image.load(file)
    except pg.error:
        raise SystemExit('Could not load image "%s" %s' % (file, pg.get_error()))
    return surface.convert()

CANVASDIM = 640*2, 480
CANVASRECT = pg.Rect(0, 0, CANVASDIM[0], CANVASDIM[1])

SCREENDIM = 640, 480
SCREENRECT = pg.Rect(0, 0, SCREENDIM[0], SCREENDIM[1])

CARTDIM = 40, 30

orig_cx = 0
orig_cy = 350
def cart_coord_on_background(t):
    cx = orig_cx + t
    cy = orig_cy
    return cx, cy

cw = CARTDIM[0]
ch = CARTDIM[1]
vw = SCREENDIM[0]
vh = SCREENDIM[1]
vcx = (vw-cw)/2
vcy = (vh-ch)/2
def background_coord_on_viewport(t):
    bcx, bcy = cart_coord_on_background(t)
    vbx = vcx - bcx
    vby = vcy - bcy
    return vbx, vby

def viewport_coord_on_background(t, mx, my):
    vbx, vby = background_coord_on_viewport(t)
    bmx = mx - vbx
    bmy = my - vby
    return bmx, bmy

class Entity:
    def __init__(self, entities, p):
        self.entities = entities
        self.p = p

    def update(self):
        return
        
    def draw(self, background):
        return
        
class Bullet(Entity):
    bullets_max = 10
    bullets = []
    def __init__(self, entities, p):
        super().__init__(entities, p)
        self.lifespan = 10
        self.entities = entities
        self.entities += [self]
        Bullet.bullets += [self]
        if len(Bullet.bullets) == Bullet.bullets_max:
            old_bullet = Bullet.bullets[0]
            Bullet.bullets.remove(old_bullet)
            if old_bullet in self.entities:
                self.entities.remove(old_bullet)

    def update(self):
        self.lifespan -= 1
        if self.lifespan == 0:
            self.entities.remove(self)
                
    def draw(self, background):
        pg.draw.circle(background, (0,0,0), self.p, 3, 3)

def main():
    pg.init()
    screen = pg.display.set_mode(SCREENDIM, 0, 24)
    clock = pg.time.Clock()

    font = pg.font.Font(None, 32)

    images = {}
    for image_filename in os.listdir('images'):
        image_name = image_filename.split('.')[0]
        images[image_name] = load_image(image_filename)

    TestCursor(recticle)
        
    grass = images['grass']
    dirt = images['dirt']

    background = pg.Surface(CANVASRECT.size)
    viewport = pg.Surface(SCREENRECT.size)

    cart = pg.transform.scale(images['minecart'], CARTDIM)

    entities = []
    
    t = 0
    mousedown = False
    while True:
        t += 1
        bcp = cart_coord_on_background(t)
        vbp = background_coord_on_viewport(t)

        background.fill((255, 255, 255))
        background.blit(cart, bcp)
        background.blit(grass, (               (SCREENDIM[0]-grass.get_width())/2, SCREENDIM[1]-grass.get_height()))
        background.blit(grass, (SCREENDIM[0] + (SCREENDIM[0]-grass.get_width())/2, SCREENDIM[1]-grass.get_height()))

        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                return
            if event.type == pg.MOUSEBUTTONDOWN:
                mousedown = True
            if event.type == pg.MOUSEBUTTONUP:
                mousedown = False
            if mousedown:
                mx, my = pg.mouse.get_pos()
                bmx, bmy = viewport_coord_on_background(t, mx, my)
                bmp = (bmx, bmy)
                Bullet(entities, bmp)

        for e in entities:
            e.update()
                
        for e in entities:
            e.draw(background)
                
        viewport.blit(background, vbp)
        screen.blit(viewport, (0, 0))
        pg.display.update()
        clock.tick(40)

if __name__ == '__main__':
    main()
