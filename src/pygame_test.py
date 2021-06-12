import pygame as pg
from pygame.locals import *
from random import random
import os
import sys
import math

main_dir = sys.argv[1] # run like: python3 pygame_test.py $(pwd)

images = {}
for image_filename in os.listdir('images'):
    image_name = image_filename.split('.')[0]
    images[image_name] = load_image(image_filename)

class Vec2_f: # TODO Convert all positions to Vec2_f
    x = 0.0
    y = 0.0

    def __init__( self, x, y ):
        self.x = x 
        self.y = y

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

def load_level(entities, filename):
    chunk_tilemap = []
    for _ in range(30):
        chunk_tilemap.append([" "] * 40 )

    cart = None
        
    point1 = Vec2_f( 10, SCREENDIM[ 1 ]/2) # beginning 
    point2 = Vec2_f( SCREENDIM[ 0 ]/2, SCREENDIM[ 1 ]/2) # middle
    point3 = Vec2_f( SCREENDIM[ 0 ] - 10, SCREENDIM[ 1 ]/2 ) # end
    points = [ point1, point2, point3 ]
    
    chunk_file = open(filename, "r")
    row = 0
    col = 0
    MAX_COLS = 40
    MAX_ROWS = 30 
    lines = chunk_file.readlines()
    for line in lines:
        for c in line:
            if c == '\n' :
                break
            if col >= MAX_COLS - 1:
                break
            chunk_tilemap[ row ][ col ] = c
            col+=1
        col = 0
        row += 1
        if row >= MAX_ROWS - 1:
            break
        for row_num, row_arr in enumerate(chunk_tilemap):
            for col_num, val in enumerate( row_arr ):
                if( val == '#'):
                    BlockFlat(entities, (col_num * TILE_SIZE, row_num * TILE_SIZE))
                if( val == '@'):
                    cart = Cart(entities, (col_num * TILE_SIZE, row_num * TILE_SIZE), points)
    return cart

class Entity:
    def __init__(self, entities, p):
        self.entities = entities
        self.entities += [self]
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

TILE_SIZE = 20
class BlockFlat(Entity):
    def __init__(self, entities, p):
        super().__init__(entities, p)
        self.sprite = images['tile']
        self.solid = True
        self.width = TILE_SIZE
        self.height = TILE_SIZE
        self.sprite = pg.transform.scale(images['stone'], (self.width, self.height))
        
    def draw(self, background):
        background.blit(self.sprite, self.p)

class Cart(Entity):
    def __init__(self, entities, p, points):
        super().__init__()
        self.v = (0, 0)
        self.points = points
        self.target_point = 0
        self.width = 40
        self.height = 30
        self.sprite = pg.transform.scale(images['minecart'], (self.width, self.height))

    def update(self):
        if self.p[0] >= self.points[ self.target_point ].x and self.target_point < len(self.points) - 1:
            self.target_point+=1 
            # find next velocity
            # subtract
            dist = Vec2_f(0,0)
            dist.x = self.points[ self.target_point ].x - self.p[0] 
            dist.y = self.points[ self.target_point ].y - self.p[1] 
            # unit vector
            direction = Vec2_f(0,0)
            direction.x = dist.x / math.sqrt( dist.x*dist.x + dist.y*dist.y )
            direction.y = dist.y / math.sqrt( dist.x*dist.x + dist.y*dist.y )
            # set velocity
            self.v.x = direction.x * entity_speed
            self.v.y = direction.y * entity_speed

        self.p[0] += self.v.x
        self.p[0] += self.v.y

    def draw(self, background):
        background.blit(self.sprite, self.p)

CANVASDIM = 640*2, 480
CANVASRECT = pg.Rect(0, 0, CANVASDIM[0], CANVASDIM[1])

SCREENDIM = 640, 480
SCREENRECT = pg.Rect(0, 0, SCREENDIM[0], SCREENDIM[1])

cw = cart.width
ch = cart.height
vw = SCREENDIM[0]
vh = SCREENDIM[1]
vcx = (vw-cw)/2
vcy = (vh-ch)/2
def background_coord_on_viewport(cart):
    bcx, bcy = cart.p
    vbx = vcx - bcx
    vby = vcy - bcy
    return vbx, vby

def viewport_coord_on_background(cart, mx, my):
    vbx, vby = background_coord_on_viewport(cart)
    bmx = mx - vbx
    bmy = my - vby
    return bmx, bmy
        
def main():
    pg.init()
    screen = pg.display.set_mode(SCREENDIM, 0, 24)
    clock = pg.time.Clock()

    TestCursor(recticle)
        
    background = pg.Surface(CANVASRECT.size)
    viewport = pg.Surface(SCREENRECT.size)

    entities = []
    cart = load_level(entities, 'chunks/chunk1')
    
    grass = images['grass']
    
    mousedown = False
    while True:
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
                bmx, bmy = viewport_coord_on_background(cart, vmx, vmy)
                bmp = (bmx, bmy)
                bbx, bby = cart.p
                bbx += cart.width/2 # Position bullets to come from middle of cart
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
                
        background.fill((255, 255, 255))
        for e in entities:
            e.draw(background)
        background.blit(grass, (               (SCREENDIM[0]-grass.get_width())/2, SCREENDIM[1]-grass.get_height()))
        background.blit(grass, (SCREENDIM[0] + (SCREENDIM[0]-grass.get_width())/2, SCREENDIM[1]-grass.get_height()))
                
        vbp = background_coord_on_viewport(cart)
        viewport.blit(background, vbp)
        screen.blit(viewport, (0, 0))

        pg.display.update()
        clock.tick(40)

if __name__ == '__main__':
    main()
