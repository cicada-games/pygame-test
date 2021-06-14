import pygame as pg
from pygame.locals import *
from random import random, randint, sample
import time
import os
import sys
import math

from cursor_aimer import CursorAimer

main_dir = os.path.dirname(os.path.abspath(__file__)) + '/../'

TILE_SIZE = 20

chunks = []
master_map = []
num_chunks = 0
current_chunk_idx = 0

bullets = 100

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


chunk_list = os.listdir('chunks')
#chunk_list = ('chunk1','chunk1','chunk1','chunk1',) # handy for debugging
chunks_max = 3
MAX_COLS = 40
MAX_ROWS = 30 
TILE_SIZE = 20
CANVASDIM = MAX_COLS*TILE_SIZE*chunks_max, MAX_ROWS*TILE_SIZE
CANVASRECT = pg.Rect(0, 0, CANVASDIM[0], CANVASDIM[1])

SCREENDIM = 640, 480
SCREENRECT = pg.Rect(0, 0, SCREENDIM[0], SCREENDIM[1])

def load_chunk(filename):
    """ loads a chunk and adds it to global list of chunks
    """
    chunk_tilemap = []
    for _ in range(30):
        chunk_tilemap.append([" "] * MAX_COLS )

    chunks.append(chunk_tilemap)

    chunk_file = open(filename, "r")
    row = 0
    col = 0
    lines = chunk_file.readlines()
    for line in lines:
        for c in line:
            if c == '\n' :
                break
            if col >= MAX_COLS :
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
    global chunks
    chunks.clear()
    for chunk_filename in sample(chunk_list, chunks_max):
        load_chunk( 'chunks/' + chunk_filename )

    global master_map
    master_map.clear()
    for chunk in chunks:
        for i, line in enumerate(chunk):
            if len(master_map) <= i:
                master_map += [line]
            else:
                master_map[i] += line

def load_entities(entities, cart):
    global master_map
    for row, line in enumerate(master_map):
        for col, c in enumerate(line):
            x = col * TILE_SIZE
            y = row * TILE_SIZE
            p = Vec2_f(x, y)
            if c == 'C':
                Cicada(entities, p, cart)
                
def render_master_map( background, tile ):
    MAX_COLS = 40
    for row_num, row_arr in enumerate(master_map):
        for col_num, val in enumerate( row_arr ):
            if( val == '#'):
                dest_tile_tect = pg.Rect(col_num * TILE_SIZE, row_num * TILE_SIZE, TILE_SIZE, TILE_SIZE )
                background.blit(tile, dest_tile_tect )

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
        self.solid = True
        self.p = p

    def update(self):
        return
        
    def draw(self, background):
        return

    def remove(self):
        if self in self.entities:
            self.entities.remove(self)

class Particle(Entity):
    def set_lifespan(self):
        clz = self.__class__
        self.lifespan = clz.max_lifespan

    def __init__(self, entities, p, v):
        super().__init__(entities, p)
        clz = self.__class__
        self.v = v
        self.set_lifespan()
        clz.particles += [self]
        if len(clz.particles) == clz.particles_max:
            clz.particles[0].remove()

    def remove(self):
        super().remove()
        if self in self.__class__.particles:
            self.__class__.particles.remove(self)

    def health_check(self):
        self.lifespan -= 1
        if self.lifespan < 0:
            self.remove()

    def move(self):
        self.p.x += self.v.x
        self.p.y += self.v.y
            
    def update(self):
        self.health_check()
        self.move()
        
    def draw(self, background):
        return

class Dust(Particle):
    particles_max = 100
    particles = []
    max_lifespan = 10
    colors = [(0,0,0), (50,50,50), (150,150,150), (250,250,250)]
    def __init__(self, entities, p, v):
        super().__init__(entities, p, v)
        self.size = randint(5, 10)
        self.color = Dust.colors[randint(0, len(Dust.colors)-1)]
    
    def draw(self, background):
        angle = math.pi*2*random()
        pg.draw.line(background, self.color, (self.p.x, self.p.y), (self.p.x+math.cos(angle)*self.size*(self.lifespan/self.max_lifespan), self.p.y+math.sin(angle)*self.size*(self.lifespan/self.max_lifespan)), 1)

class Stone:
    def kablooie(entities, p):
        for _ in range(randint(5, 10)):
            gp = Vec2_f(p.x+TILE_SIZE/2, p.y+TILE_SIZE/2)
            angle = math.pi*2*random()
            mag = 2 * random()
            gv = Vec2_f(math.cos(angle)*mag, math.sin(angle)*mag)
            Dust(entities, gp, gv)

class Projectile(Particle):
    particles_max = 100
    particles = []
    max_lifespan = 10
    
    def decrease_lifespan(self):
        self.lifespan -= 20

    def cicada_update_context(self):
        return
        
    def update(self):
        super().update()
        
        tx = int(self.p.x/TILE_SIZE)
        ty = int(self.p.y/TILE_SIZE)
        
        entities_copy = [entity for entity in self.entities]
        for entity in entities_copy:
            if type(entity) in (Projectile,):
                continue
            ex = int(entity.p.x/TILE_SIZE)
            ey = int(entity.p.y/TILE_SIZE)
            if tx == ex and ty == ey:
                if type(entity) is Cicada:
                    entity.remove() # KILL CICADA!!
                    self.cicada_update_context()
                    
        if 0 <= ty < len(master_map) and 0 <= tx < len(master_map[ty]) and master_map[ty][tx] == '#':
            self.decrease_lifespan()
            if self.lifespan > 0 or random() < 0.03:
                master_map[ty][tx] = ' ' # Destructible terrain
                Stone.kablooie(self.entities, self.p)
        
    def draw(self, background):
        pg.draw.circle(background, (0,0,0), (self.p.x, self.p.y), 3, 3)

class Bullet(Projectile):
    particles_max = 100
    particles = []
    max_lifespan = 10

    def __init__(self, entities, p, v, cart):
        super().__init__(entities, p, v)
        self.cart = cart

    def cicada_update_context(self):
        self.cart.bullets += 4
        
class Gore(Projectile):
    particles_max = 100
    particles = []
    max_lifespan = 50
    def __init__(self, entities, p, v):
        super().__init__(entities, p, v)

    def decrease_lifespan(self):
        self.lifespan -= random()*25
        
    def draw(self, background):
        decay = self.lifespan/Goo.max_lifespan
        pg.draw.circle(background, (200,50,0), (self.p.x, self.p.y), random()*10*decay*2, 5)
        pg.draw.circle(background, (100,0,0), (self.p.x, self.p.y), random()*10*decay, 5)
        pg.draw.circle(background, (100,100,0), (self.p.x, self.p.y), random()*5*decay, 3)
        pg.draw.circle(background, (200,200,200), (self.p.x, self.p.y), random()*5*decay, 5)
        pg.draw.circle(background, (50,0,0), (self.p.x, self.p.y), random()*10*decay, 8)

class Goo(Projectile):
    particle_max = 1000
    particles = []
    max_lifespan = 20

    def set_lifespan(self):
        self.lifespan = random()*self.max_lifespan
    
    def __init__(self, entities, p, v):
        super().__init__(entities, p, v)

    def decrease_lifespan(self):
        self.lifespan -= 1000
        
    def draw(self, background):
        decay = self.lifespan/Goo.max_lifespan
        pg.draw.circle(background, (200,50,0), (self.p.x, self.p.y), random()*10*decay, 5)
        pg.draw.circle(background, (0,200,0), (self.p.x, self.p.y), random()*20*decay, 8)
        pg.draw.circle(background, (0,100,0), (self.p.x, self.p.y), random()*20*decay, 8)
        pg.draw.circle(background, (200,0,0), (self.p.x, self.p.y), random()*10*decay*2, 5)
        pg.draw.circle(background, (0,10,0), (self.p.x, self.p.y), random()*20*decay, 8)
        pg.draw.circle(background, (100,200,100), (self.p.x, self.p.y), random()*20*decay, 8)
        pg.draw.circle(background, (0,100,200), (self.p.x, self.p.y), random()*5*decay, 3)
        pg.draw.circle(background, (100,100,200), (self.p.x, self.p.y), random()*10*decay, 8)
            
class Cart(Entity):
    height = 30
    width = int(30 * 1.01923077)
    cw = width
    ch = height
    vw = SCREENDIM[0]
    vh = SCREENDIM[1]
    vcx = (vw-cw)/2
    vcy = (vh-ch)/2
    def canvas_coord_on_viewport(self):
        bcx, bcy = self.p.x, self.p.y
        vbx = max(min(Cart.vcx - bcx, 0), SCREENDIM[0]-CANVASDIM[0])
        vby = Cart.vcy - bcy
        return vbx, vby

    def viewport_coord_on_background(self, mx, my):
        vbx, vby = self.canvas_coord_on_viewport()
        bmx = mx - vbx
        bmy = my - vby
        return bmx, bmy

    def __init__(self, entities, p):
        super().__init__(entities, p)
        self.velocity = Vec2_f(1, 0)
        self.speed = 1
        self.sprite = pg.transform.scale(images['minecart'], (Cart.width, Cart.height))
        self.bullets = 100
        self.score = 0

    def update(self):
        self.p.x += self.velocity.x * self.speed
        tx = int(self.p.x/TILE_SIZE)
        ty = int(self.p.y/TILE_SIZE)
        if tx < len(master_map[0]) and ty < len(master_map) and (master_map[ty][tx] == '#' or master_map[ty+1][tx] == '#'):
            self.remove()
                    
    def draw(self, background):
        background.blit(self.sprite, (self.p.x, self.p.y))

    def remove(self):
        super().remove()
        self.kablooie()

    def kablooie(self):
        for _ in range(randint(100, 300)):
            gp = Vec2_f(self.p.x+TILE_SIZE/2, self.p.y+TILE_SIZE/2)
            angle = math.pi*2*random()
            mag = 5 * random()
            gv = Vec2_f(math.cos(angle)*mag, math.sin(angle)*mag)
            Gore(self.entities, gp, gv)
        
    def shoot(self):
        mouse_pos = pg.mouse.get_pos()
        vmx, vmy = pg.mouse.get_pos()
        bmx, bmy = self.viewport_coord_on_background(vmx, vmy)
        bmp = (bmx, bmy)
        bbx, bby = self.p.x, self.p.y
        bbx += self.width/2 # Position bullets to come from middle of cart
        bbp = Vec2_f(bbx, bby)
        bbvx = bmx - bbx
        bbvy = bmy - bby
        bbvh = (bbvx ** 2 + bbvy ** 2) ** (1/2)
        bbv = 10
        bbvn = Vec2_f(bbv, 0)
        if bbvh > 0:
            bbvxn = bbvx/bbvh * bbv + (random()-0.5)
            bbvyn = bbvy/bbvh * bbv + (random()-0.5)
            bbvn = Vec2_f(bbvxn, bbvyn)
        bbvn.x += self.speed # Correct for forward velocity
        if self.bullets >= 1:
            self.bullets -= 1
            Bullet(self.entities, bbp, bbvn, self)
            
def get_ticks():
    return round(time.time() * 1000)

def lerp(start, end, amt):
    return (1-amt)*start+amt*end

class Cicada(Entity):
    sprite = None
    size = None
    angle = 0
    nangle = 0
    twitch_timeout = 350
    last_twitch = 0
    
    def __init__(self, entities, p, cart):
        super().__init__(entities, p)
        self.cart = cart
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

        tx = int(self.p.x/TILE_SIZE)
        ty = int(self.p.y/TILE_SIZE)
        cx = int(self.cart.p.x/TILE_SIZE)
        cy = int(self.cart.p.y/TILE_SIZE)
        if tx == cx and -1 <= ty - cy < 2:
            if self.cart in self.entities:
                self.cart.remove()
            
    def draw(self, background):
        result = pg.transform.rotate(self.sprite, self.nangle) # apply some on the fly transformations
        rect = result.get_rect(center = self.sprite.get_rect(topleft = (self.p.x, self.p.y)).center) # render from the center
        background.blit(result, rect)

    def remove(self):
        super().remove()
        
        self.cart.score += 1

        self.kablooie()

    def kablooie(self):
        for _ in range(randint(0, 50)):
            gp = Vec2_f(self.p.x+TILE_SIZE/2, self.p.y+TILE_SIZE/2)
            gv = Vec2_f((random()-0.5)*3, (random()-0.5)*3)
            Goo(self.entities, gp, gv)
        
def main():
    global images
    
    pg.init()
    CursorAimer()
    clock = pg.time.Clock()
        
    screen = pg.display.set_mode(SCREENDIM, pg.FULLSCREEN, 24) # Funnerer
    #screen = pg.display.set_mode(SCREENDIM, 0, 24) # Better for debugging and testing

    canvas = pg.Surface(CANVASRECT.size)
    viewport = pg.Surface(SCREENRECT.size)

    pg.font.init()
    myfont = pg.font.SysFont('Times New Roman', 14)

    # Has to be here because pygame needs to initialize beforehand
    for image_filename in os.listdir('images'):
        image_name = image_filename.split('.')[0]
        images[image_name] = load_image(image_filename)

    grass = images['grass']
    def render_foreground(canvas):
        canvas.blit(grass, (SCREENDIM[0]*0 + (SCREENDIM[0]-grass.get_width())/2, SCREENDIM[1]-grass.get_height()+50))
        canvas.blit(grass, (SCREENDIM[0]*1 + (SCREENDIM[0]-grass.get_width())/2, SCREENDIM[1]-grass.get_height()+50))
        canvas.blit(grass, (SCREENDIM[0]*2 + (SCREENDIM[0]-grass.get_width())/2, SCREENDIM[1]-grass.get_height()+50))
        
    stone = pg.transform.scale(images['stone'], (20, 20))
    
    entities = []
    cart_start = Vec2_f(0, 230)
    cart = Cart(entities, Vec2_f(cart_start.x, cart_start.y))
        
    fullauto = False
    dead = False

    while not dead:
        # Create the master_map
        load_chunks()

        # Load the entities from the master_map
        load_entities(entities, cart) 

        # Initialize the cart
        cart.p = Vec2_f(cart_start.x, cart_start.y)
        cart.speed += 0.5
        Bullet.max_lifespan += 2
        
        while True:
            # Slowly recharge bullets so never completely hopeless
            cart.bullets += 0.02
            
            for event in pg.event.get():
                # Just shut it all down
                if event.type == pg.QUIT:
                    return
                if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    return
                
                # Game loop may still be running when cart is dead, so don't process input.
                if cart in entities: 
                    if event.type == pg.KEYDOWN and event.key == pg.K_s:
                        cart.remove()
                    if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                        fullauto = True
                    if event.type == pg.KEYUP and event.key == pg.K_SPACE:
                        fullauto = False
                    if fullauto:
                        cart.shoot()
                    if event.type == pg.MOUSEBUTTONDOWN:
                        cart.shoot()

            # Fill in the canvas
            canvas.fill((255, 255, 255))

            # Draw the static parts of level
            render_master_map(canvas, stone)

            # Draw the cart track
            pg.draw.line(canvas, (100, 30, 20), (0, 260), (CANVASDIM[0], 260), 2) 

            # Draw the dynamic entities
            for e in entities:
                e.draw(canvas)

            # Draw anything in the foreground
            render_foreground(canvas)
            
            # Adjust the viewport to center on the cart
            vbp = cart.canvas_coord_on_viewport()
            viewport.fill((255, 255, 255))
            viewport.blit(canvas, vbp)
            screen.blit(viewport, (0, 0))

            # Heads up display
            textsurface = myfont.render('dead cicadas: ' + str(cart.score), False, (0, 0, 0))
            screen.blit(textsurface, (0, 0))
            textsurface = myfont.render('bullets: ' + str(int(cart.bullets)), False, (0, 0, 0))
            screen.blit(textsurface, (400, 0))
            textsurface = myfont.render('mouse button: single fire        spacebar: spray and pray        ESC: exit', False, (0, 0, 0))
            screen.blit(textsurface, (100, 15))
            textsurface = myfont.render('***WARNING*** NEVER, EVER PRESS S', False, (0, 0, 0))
            screen.blit(textsurface, (180, 30))

            # Draw it all
            pg.display.update()
    
            # Update the dynamic entities
            entities_copy = [entity for entity in entities]
            for e in entities_copy: # Copy necessary b/c destructive of entities list
                e.update()
    
            if not cart in entities:
                if len(Gore.particles) == 0 and len(Goo.particles) == 0:
                    dead = True
                    break # Cart was killed
    
            if cart.p.x > CANVASDIM[0]:
                break # Cart finished level

            clock.tick(40)
            
    myfont = pg.font.SysFont('Comic Sans MS', 30)
    textsurface = myfont.render('GAMEOVER', False, (0, 0, 0))
    screen.blit(textsurface,(320,240))
    pg.display.update()

if __name__ == '__main__':
    main()
