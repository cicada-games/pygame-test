import pygame as pg
from pygame.locals import *
from random import random
import os
import sys
import math
import random

main_dir = sys.argv[1] # run like: python3 pygame_test.py $(pwd)

class Vec2_f:
    x = 0.0
    y = 0.0

    def __init__( self, x, y ):
        self.x = x 
        self.y = y

TILE_SIZE = 20

chunks = []
num_chunks = 0
current_chunk_idx = 0


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

def load_chunk(filename):
    """ loads a chunk and adds it to global list of chunks
    """
    chunk_tilemap = []
    for _ in range(30):
        chunk_tilemap.append([" "] * 40 )

    chunks.append(chunk_tilemap)

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
    global num_chunks 
    num_chunks += 1

def load_chunks():
    """ Loads all chunk files into list and then randomizes
    """
    for chunk_filename in os.listdir('chunks'):
        load_chunk('chunks/' + chunk_filename)
    random.shuffle( chunks )

def generate_current_chunk_region( camera_position ):
    """ sets the chunk region which is the current and next chunk
    """
    num_cols = 40
    tile_x = int( camera_position[0] / TILE_SIZE )
    global current_chunk_idx
    current_chunk_idx = int( tile_x / num_cols )

def render_chunk( chunk_idx, background, tile ):
    MAX_COLS = 40
    for row_num, row_arr in enumerate(chunks[chunk_idx]):
        for col_num, val in enumerate( row_arr ):
            if( val == '#'):
                offset = chunk_idx * (MAX_COLS *TILE_SIZE)
                dest_tile_tect = pg.Rect(col_num * TILE_SIZE + offset, row_num * TILE_SIZE, TILE_SIZE, TILE_SIZE ) # don't need offset for y pos cause only moving right
                background.blit(tile, dest_tile_tect )

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
    tile = images['tile']
    
    ## JB PARSE LEVEL
    load_chunks()
    ## END JB PARSE LEVEL CHUNK
    dirt = images['dirt']

    background = pg.Surface(CANVASRECT.size)
    viewport = pg.Surface(SCREENRECT.size)

    

    minecart = images['minecart']

    ## JB SETUP FOLLOWING PATH POINTS
    entity_position = Vec2_f( 10, SCREENDIM[ 1 ]/2 )
    entity_speed = 2
    entity_velocity = Vec2_f(0,0)
    point1 = Vec2_f( 10, SCREENDIM[ 1 ]/2) # beginning 
    point2 = Vec2_f( SCREENDIM[ 0 ]/2, SCREENDIM[ 1 ]/2) # middle
    #point2 = Vec2_f( SCREENDIM[ 0 ]/2, SCREENDIM[1] -10 ) # middle
    point3 = Vec2_f( SCREENDIM[ 0 ] - 10, SCREENDIM[ 1 ]/2 ) # end
    points = [ point1, point2, point3 ]
    target_point = 0
    ## JB END SETUP FOLLOWING PATH POINTS

    cart = pg.transform.scale(images['minecart'], CARTDIM)

    entities = []
    
    t = 0
    mousedown = False
    while True:
        t += 3
        bcp = cart_coord_on_background(t)
        vbp = background_coord_on_viewport(t)

        generate_current_chunk_region(bcp)

        background.fill((255, 255, 255))
        ## JB RENDER TILEMAP CHUNK

        if( not current_chunk_idx-1 < 0) :
            render_chunk( current_chunk_idx-1, background, tile )

        render_chunk( current_chunk_idx, background, tile)

        if not current_chunk_idx+1 > num_chunks:
            render_chunk( current_chunk_idx + 1, background, tile )

        ## JB END RENDER TILEMAP CHUNK
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
                mouse_pos = pg.mouse.get_pos()
                pg.draw.circle(background, (0,0,0), pg.mouse.get_pos(), 3, 3)

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
                bbvxn = bbvx/bbvh * bbv + (random.random()-0.5)
                bbvyn = bbvy/bbvh * bbv + (random.random()-0.5)
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
