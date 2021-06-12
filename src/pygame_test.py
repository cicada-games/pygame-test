import pygame as pg
from pygame.locals import *
from random import random
from random import randint
import time
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
    
def lerp (start, end, amt):
    return (1-amt)*start+amt*end

def load_image(file):
    """ loads an image, prepares it for play
    """
    file = os.path.join(main_dir, "images", file)
    try:
        surface = pg.image.load(file)
    except pg.error:
        raise SystemExit('Could not load image "%s" %s' % (file, pg.get_error()))
    return surface.convert_alpha() # use png's alpha channel

CANVASDIM = 640*2, 480
CANVASRECT = pg.Rect(0, 0, CANVASDIM[0], CANVASDIM[1])

SCREENDIM = 640, 480
SCREENRECT = pg.Rect(0, 0, SCREENDIM[0], SCREENDIM[1])

CARDHEIGHT = 40
CARTDIM = int(CARDHEIGHT * 1.01923077), CARDHEIGHT # width = CARDHEIGHT * (original width / height ratio)

orig_cx = 0
orig_cy = 350
cpos_x = 0
cpos_y = 0
def cart_coord_on_background(t):
    global cpos_x, cpos_y
    cx = orig_cx + t
    cy = orig_cy
    
    cpos_x = lerp(cpos_x, cx, 0.05)
    cpos_y = lerp(cpos_y, cy, 0.05)

    return cpos_x, cpos_y

cw = CARTDIM[0]
ch = CARTDIM[1]
vw = SCREENDIM[0]
vh = SCREENDIM[1]
vcx = (vw-cw)/2
vcy = (vh-ch)/2
images = {}

def get_ticks():
    return round(time.time() * 1000)

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

def load_assets():
    # load images
    for image_filename in os.listdir('images'):
        image_name = image_filename.split('.')[0]
        images[image_name] = load_image(image_filename)

class Entity:
    def __init__(self, entities, p):
        self.entities = entities
        self.p = p

    def update(self):
        return
        
    def draw(self, background):
        return
        
class Bullet(Entity):
    bullets_max = 100
    bullets = []
    def __init__(self, entities, p, v, l):
        super().__init__(entities, p)
        self.v = v
        self.lifespan = l
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
        if self.lifespan < 0:
            self.entities.remove(self)

        px, py = self.p
        vx, vy = self.v
        px += vx
        py += vy
        self.p = px, py
                
    def draw(self, background):
        pg.draw.circle(background, (0,0,0), self.p, 3, 3)

class Cicada(Entity):
    sprite = None
    size = None
    angle = 0
    nangle = 0
    twitch_timeout = 350
    last_twitch = 0
    
    def __init__(self, entities, p):
        super().__init__(entities, p)
        self.entities = entities
        self.entities += [self]
        self.angle = randint(-45, 45)
        cicada_height = 65
        self.size = (int(cicada_height * 0.568421053), cicada_height)
        self.sprite = pg.transform.smoothscale(images['cicada'], self.size) 
        self.last_twitch = get_ticks()


    def update(self):
        if(get_ticks()-self.last_twitch > self.twitch_timeout):
            self.angle = randint(-45, 45)
            self.last_twitch = get_ticks()

        self.nangle = lerp(self.nangle, self.angle, 0.05)
                
    def draw(self, background):
        result = pg.transform.rotate(self.sprite, self.nangle) # apply some on the fly transformations
        rect = result.get_rect(center = self.sprite.get_rect(topleft = self.p).center) # render from the center
        background.blit(result, rect)   

def main():
    pg.init()
    screen = pg.display.set_mode(SCREENDIM, 0, 24)
    clock = pg.time.Clock()

    font = pg.font.Font(None, 32)
    load_assets()

    TestCursor(recticle)
        
    grass = images['grass']
    dirt = images['dirt']

    background = pg.Surface(CANVASRECT.size)
    viewport = pg.Surface(SCREENRECT.size)

    cart = pg.transform.smoothscale(images['minecart'], CARTDIM)

    entities = []
    
    t = 0
    mousedown = False

    for i in range(1, 20):
        Cicada(entities, (0 + i * 75, 250))

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
                vmx, vmy = pg.mouse.get_pos()
                bmx, bmy = viewport_coord_on_background(t, vmx, vmy)
                bmp = (bmx, bmy)
                bbx, bby = cart_coord_on_background(t)
                bbx += CARTDIM[0]/2
                bbp = (bbx, bby)
                bbvx = bmx - bbx
                bbvy = bmy - bby
                bbvh = (bbvx ** 2 + bbvy ** 2) ** (1/2)
                bbv = 10
                bbvxn = bbvx/bbvh * bbv + (random()-0.5)
                bbvyn = bbvy/bbvh * bbv + (random()-0.5)
                bbvn = (bbvxn, bbvyn)
                bl = 30
                Bullet(entities, bbp, bbvn, bl)

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
