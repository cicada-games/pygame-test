import pygame as pg
from pygame.locals import *
from random import random, randint
import time
import os
import sys
import math

def get_ticks():
    return round(time.time() * 1000)

def lerp (start, end, amt):
    return (1-amt)*start+amt*end

main_dir = sys.argv[1] # run like: python3 pygame_test.py $(pwd)

def load_image(file):
    """ loads an image, prepares it for play
    """
    file = os.path.join(main_dir, "images", file)
    try:
        surface = pg.image.load(file)
    except pg.error:
        raise SystemExit('Could not load image "%s" %s' % (file, pg.get_error()))
    return surface.convert_alpha() # use png's alpha channel

images = {}

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
                    cart = Cart(entities, Vec2_f(col_num * TILE_SIZE, row_num * TILE_SIZE), points)
                if( val == 'C'):
                    cart = Cicada(entities, Vec2_f(col_num * TILE_SIZE, row_num * TILE_SIZE))
    return cart

class Vec2_f: # TODO Convert all positions to Vec2_f
    x = 0.0
    y = 0.0

    def __init__( self, x, y ):
        self.x = x 
        self.y = y
        
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
    height = 30
    width = int(30 * 1.01923077)

    def __init__(self, entities, p, points):
        super().__init__(entities, p)
        self.velocity = Vec2_f(1, 0)
        self.speed = 1
        self.points = points
        self.target_point = 0
        self.sprite = pg.transform.scale(images['minecart'], (Cart.width, Cart.height))

    def update(self):
        if self.p.x >= self.points[ self.target_point ].x and self.target_point < len(self.points) - 1:
            self.target_point+=1 
            # find next velocity
            # subtract
            dist = Vec2_f(0,0)
            dist.x = self.points[ self.target_point ].x - self.p.x 
            dist.y = self.points[ self.target_point ].y - self.p.y
            # unit vector
            direction = Vec2_f(0,0)
            direction.x = dist.x / math.sqrt( dist.x*dist.x + dist.y*dist.y )
            direction.y = dist.y / math.sqrt( dist.x*dist.x + dist.y*dist.y )
            # set velocity
            self.velocity.x = direction.x * self.speed
            self.velocity.y = direction.y * self.speed

        self.p.x += self.velocity.x
        self.p.y += self.velocity.y

    def draw(self, background):
        background.blit(self.sprite, (self.p.x, self.p.y))

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
        rect = result.get_rect(center = self.sprite.get_rect(topleft = (self.p.x, self.p.y)).center) # render from the center
        background.blit(result, rect)   

CANVASDIM = 640*2, 480
CANVASRECT = pg.Rect(0, 0, CANVASDIM[0], CANVASDIM[1])

SCREENDIM = 640, 480
SCREENRECT = pg.Rect(0, 0, SCREENDIM[0], SCREENDIM[1])

cw = Cart.width
ch = Cart.height
vw = SCREENDIM[0]
vh = SCREENDIM[1]
vcx = (vw-cw)/2
vcy = (vh-ch)/2
def background_coord_on_viewport(cart):
    bcx, bcy = cart.p.x, cart.p.y
    vbx = vcx - bcx
    vby = vcy - bcy
    return vbx, vby

def viewport_coord_on_background(cart, mx, my):
    vbx, vby = background_coord_on_viewport(cart)
    bmx = mx - vbx
    bmy = my - vby
    return bmx, bmy
        
def main():
    global images
    
    pg.init()
    screen = pg.display.set_mode(SCREENDIM, 0, 24)

    for image_filename in os.listdir('images'):
        image_name = image_filename.split('.')[0]
        images[image_name] = load_image(image_filename)

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
                bbx, bby = cart.p.x, cart.p.y
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
