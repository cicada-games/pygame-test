import pygame as pg
from pygame.locals import *
from random import random, randint, sample
import time
import os
import sys
import math

# Custom module to customize the cursor.
from cursor_aimer import CursorAimer

main_dir = os.path.dirname(os.path.abspath(__file__)) + '/../'

# ===================================================
# Logic to randomly generate levels from chunk files.
# ===================================================
chunk_list = os.listdir('chunks')
#chunk_list = ('chunk1','chunk1','chunk1','chunk1',) # handy for debugging
chunks_max = 3
chunks = []
num_chunks = 0
current_chunk_idx = 0

MAX_COLS = 40
MAX_ROWS = 30 
TILE_SIZE = 20

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
            x = col * TILE_SIZE
            y = row * TILE_SIZE
            if c == '#':
                chunk_tilemap[ row ][ col ] = Stone(Vec2_i(x, y))
            if c == 'C':
                Cicada(Vec2_f(x, y))
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

    Tile.master_map.clear()
    for chunk in chunks:
        for i, line in enumerate(chunk):
            if len(Tile.master_map) <= i:
                Tile.master_map += [line]
            else:
                Tile.master_map[i] += line

def render_master_map( background ):
    MAX_COLS = 40
    for row_num, row_arr in enumerate(Tile.master_map):
        for col_num, val in enumerate( row_arr ):
            if Tile in type(val).__mro__:
                val.draw(background)

# ============
# Entity logic
# ============
                
CANVASDIM = MAX_COLS*TILE_SIZE*chunks_max, MAX_ROWS*TILE_SIZE
CANVASRECT = pg.Rect(0, 0, CANVASDIM[0], CANVASDIM[1])

SCREENDIM = 640, 480
SCREENRECT = pg.Rect(0, 0, SCREENDIM[0], SCREENDIM[1])

# All coordinate type data uses one of these classes.
class Vec2_f: 
    x = 0.0
    y = 0.0

    def __init__( self, x, y ):
        self.x = x 
        self.y = y

class Vec2_i: 
    x = 0
    y = 0

    def __init__( self, x, y ):
        self.x = x 
        self.y = y

# Base class, fyi
# An important thing to note about the Entity class, and its
# subclasses, is that it maintains the list of entities.  Objects
# themselves to the list when created, and remove themselves when
# destroyed.
class Entity:
    entities = []
    def __init__(self, p):
        Entity.entities += [self]
        self.solid = True
        self.p = p

    def update(self):
        return
        
    def draw(self, background):
        return

    def remove(self):
        if self in Entity.entities:
            Entity.entities.remove(self)

# Tile entities have a different render system.
class Tile(Entity):
    # The master map is assembled from the chunk sequence, to avoid the need for calculating offsets.
    master_map = []
    def remove(self):
        super().remove()
        mmx = int(self.p.x/TILE_SIZE)
        mmy = int(self.p.y/TILE_SIZE)
        Tile.master_map[mmy][mmx] = None

class Stone(Entity):
    def remove(self):
        super().remove()
        self.kablooie()
        
    def kablooie(self):
        for _ in range(randint(5, 10)):
            gp = Vec2_f(self.p.x+TILE_SIZE/2, self.p.y+TILE_SIZE/2)
            angle = math.pi*2*random()
            mag = 2 * random()
            gv = Vec2_f(math.cos(angle)*mag, math.sin(angle)*mag)
            Dust(gp, gv)

    def draw(self, background):
        dest_tile_rect = pg.Rect(self.p.x, self.p.y, TILE_SIZE, TILE_SIZE )
        background.blit(images['stone'], dest_tile_rect )

# All particles have a limited lifespan and a velocity.
# There is some introspection trickery here because each particle type
# keeps a list of its own type, so there is a strict limit on number
# of particles, to avoid slowing down the engine too much.

# Basically, the idea is each subclass of Particle declares its own
# list to keep track of its particles.
class Particle(Entity):
    def set_lifespan(self):
        clz = self.__class__
        self.lifespan = clz.max_lifespan

    def __init__(self, p, v):
        super().__init__(p)
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

# Dust is created by breaking stones, purely cosmetic    
class Dust(Particle):
    particles_max = 100
    particles = []
    max_lifespan = 100
    colors = [(50,50,50), (100,100,100), (150,150,150), (200,200,200)]
    def __init__(self, p, v):
        super().__init__(p, v)
        self.size = randint(1, 3)
        self.color = Dust.colors[randint(0, len(Dust.colors)-1)]

    def move(self):
        super().move()
        self.v.y += 0.1
        
    def draw(self, background):
        angle = math.pi*2*random()
        expansion = self.size*self.lifespan/self.max_lifespan
        end_x = self.p.x+math.cos(angle)*expansion
        end_y = self.p.y+math.sin(angle)*expansion
        pg.draw.line(background, self.color, (self.p.x, self.p.y), (end_x, end_y), 5)

# Projectiles are particles that impact the surroundings            
class Projectile(Particle):
    particles_max = 100
    particles = []
    max_lifespan = 10
    
    def decrease_lifespan(self):
        self.lifespan -= 20

    # A special callout function specially made for Bullet
    def cicada_update_context(self):
        return
        
    def update(self):
        super().update()
        
        tx = int(self.p.x/TILE_SIZE)
        ty = int(self.p.y/TILE_SIZE)
        
        entities_copy = [entity for entity in Entity.entities]
        for entity in entities_copy:
            if type(entity) in (Projectile,):
                continue
            ex = int(entity.p.x/TILE_SIZE)
            ey = int(entity.p.y/TILE_SIZE)
            if tx == ex and ty == ey:
                if type(entity) is Cicada:
                    entity.remove() # KILL CICADA!!
                    self.cicada_update_context()

        if 0 <= ty < len(Tile.master_map) and 0 <= tx < len(Tile.master_map[ty]): # Prevent out of bounds errors
            if type(Tile.master_map[ty][tx]) == Stone:
                self.decrease_lifespan()
                if self.lifespan > 0 or random() < 0.03:
                    Tile.master_map[ty][tx].remove() # Destructible terrain
        
    def draw(self, background):
        pg.draw.circle(background, (0,0,0), (self.p.x, self.p.y), 3, 3)

class Bullet(Projectile):
    particles_max = 100
    particles = []
    max_lifespan = 100

    def __init__(self, p, v, cart):
        super().__init__(p, v)
        self.cart = cart

    # Special callout function, it's a bit weird, but neatens the code
    # It is called by the Projectile update function
    # Needed to retain context that the bullet killed a cicada
    def cicada_update_context(self):
        self.cart.bullets += 4 # Dead cicadas mean more bullets

    def move(self):
        super().move()
        self.v.y += 0.1

# The projectiles generated by the exploding cart        
class Gore(Projectile):
    particles_max = 100
    particles = []
    max_lifespan = 50
    def __init__(self, p, v):
        super().__init__(p, v)

    def decrease_lifespan(self):
        self.lifespan -= random()*25
        
    def draw(self, background):
        decay = self.lifespan/Goo.max_lifespan
        pg.draw.circle(background, (200,50,0), (self.p.x, self.p.y), random()*10*decay*2, 5)
        pg.draw.circle(background, (100,0,0), (self.p.x, self.p.y), random()*10*decay, 5)
        pg.draw.circle(background, (100,100,0), (self.p.x, self.p.y), random()*5*decay, 3)
        pg.draw.circle(background, (200,200,200), (self.p.x, self.p.y), random()*5*decay, 5)
        pg.draw.circle(background, (50,0,0), (self.p.x, self.p.y), random()*10*decay, 8)

# The projectiles generated by the exploding cicadas        
class Goo(Projectile):
    particle_max = 1000
    particles = []
    max_lifespan = 20

    def set_lifespan(self):
        self.lifespan = random()*self.max_lifespan
    
    def __init__(self, p, v):
        super().__init__(p, v)

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

# ******
# Cicada
# ******
# The cicada!
class Cicada(Tile):

    # First are the parameters and utilities for the cicada twitch animation.
    
    sprite = None
    size = None
    angle = 0
    nangle = 0
    twitch_timeout = 350
    last_twitch = 0
    
    def get_ticks():
        return round(time.time() * 1000)

    def lerp(start, end, amt):
        return (1-amt)*start+amt*end

    # Then follows the update logic.

    cart = None 
    
    def __init__(self, p):
        super().__init__(p)
        self.angle = randint(-45, 45)
        cicada_height = 65
        self.size = (int(cicada_height * 0.568421053), cicada_height)
        self.sprite = pg.transform.smoothscale(images['cicada'], self.size) 
        self.last_twitch = Cicada.get_ticks()

    def update(self):
        if(Cicada.get_ticks()-self.last_twitch > self.twitch_timeout):
            self.angle = randint(-45, 45)
            self.last_twitch = Cicada.get_ticks()

        self.nangle = Cicada.lerp(self.nangle, self.angle, 0.05)

        tx = int(self.p.x/TILE_SIZE)
        ty = int(self.p.y/TILE_SIZE)
        cx = int(Cicada.cart.p.x/TILE_SIZE)
        cy = int(Cicada.cart.p.y/TILE_SIZE)
        if tx == cx and -1 <= ty - cy < 2:
            if Cicada.cart in Entity.entities:
                Cicada.cart.remove()
            
    def draw(self, background):
        result = pg.transform.rotate(self.sprite, self.nangle) # apply some on the fly transformations
        rect = result.get_rect(center = self.sprite.get_rect(topleft = (self.p.x, self.p.y)).center) # render from the center
        background.blit(result, rect)

    # This is the important function for the cicada's chain reaction
    # of exploding each other.
    def remove(self):
        super().remove()
        Cicada.cart.score += 1
        self.kablooie()

    def kablooie(self):
        for _ in range(randint(0, 50)):
            gp = Vec2_f(self.p.x+TILE_SIZE/2, self.p.y+TILE_SIZE/2)
            gv = Vec2_f((random()-0.5)*3, (random()-0.5)*3)
            Goo(gp, gv)

            
# ****
# Cart
# ****
# The cart!        
class Cart(Entity):

    # The camera is tied to the cart, so all the positional
    # calculations for blitting to maintain the illusion of movement
    # are done here.
    
    height = 30
    width = int(30 * 1.01923077)
    cw = width
    ch = height
    vw = SCREENDIM[0]
    vh = SCREENDIM[1]
    vcx = (vw-cw)/2
    vcy = (vh-ch)/2
    max_lifespan = 100
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

    # Now begins the actual cart behavior logic.
    # The logic does two main things:
    # 1. Move the cart forward
    # 2. Fire bullets
    
    def __init__(self, p):
        super().__init__(p)
        self.velocity = Vec2_f(1, 0)
        self.speed = 1
        self.sprite = pg.transform.scale(images['minecart'], (Cart.width, Cart.height))
        self.bullets = 100
        self.score = 0

    def update(self):
        self.p.x += self.velocity.x * self.speed
        tx = int(self.p.x/TILE_SIZE)
        ty = int(self.p.y/TILE_SIZE)
        if tx < len(Tile.master_map[0]) and ty < len(Tile.master_map) and type(Tile.master_map[ty+1][tx]) == Stone:
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
            Gore(gp, gv)
        
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
            Bullet(bbp, bbvn, self)


            
# =========
# Utilities
# =========

def load_image(file):
    """ loads an image, prepares it for play
    """
    file = os.path.join(main_dir, "images", file)
    try:
        surface = pg.image.load(file)
    except pg.error:
        raise SystemExit('Could not load image "%s" %s' % (file, pg.get_error()))
    return surface.convert_alpha() # use png's alpha channel

# Images have to be loaded in the main function because pygame must be initialized
# OTOH, images has to be a global function
images = {}



# ==============
# Main game loop
# ==============
def main():
    global images
    
    pg.init()
    CursorAimer()
    clock = pg.time.Clock()
        
    #screen = pg.display.set_mode(SCREENDIM, pg.FULLSCREEN, 24) # Funnerer
    screen = pg.display.set_mode(SCREENDIM, 0, 24) # Better for debugging and testing

    canvas = pg.Surface(CANVASRECT.size)
    viewport = pg.Surface(SCREENRECT.size)

    pg.font.init()
    myfont = pg.font.SysFont('Times New Roman', 14)

    # Has to be here because pygame needs to initialize beforehand
    for image_filename in os.listdir('images'):
        image_name = image_filename.split('.')[0]
        images[image_name] = load_image(image_filename)

    mountains = images['mountains']
    def render_background(canvas, cart):
        vbx, vby = cart.canvas_coord_on_viewport()
        px = -vbx/1.5
        canvas.blit(mountains, (px, 0))
        
    grass = images['grass']
    def render_foreground(canvas):
        canvas.blit(grass, (SCREENDIM[0]*0 + (SCREENDIM[0]-grass.get_width())/2, SCREENDIM[1]-grass.get_height()+50))
        canvas.blit(grass, (SCREENDIM[0]*1 + (SCREENDIM[0]-grass.get_width())/2, SCREENDIM[1]-grass.get_height()+50))
        canvas.blit(grass, (SCREENDIM[0]*2 + (SCREENDIM[0]-grass.get_width())/2, SCREENDIM[1]-grass.get_height()+50))
        
    stone = pg.transform.scale(images['stone'], (20, 20))
    
    cart_start = Vec2_f(0, 230)
    cart = Cart(Vec2_f(cart_start.x, cart_start.y))
    Cicada.cart = cart
        
    fullauto = False
    dead = False

    while not dead:
        # Create the master_map
        load_chunks()

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
                if cart in Entity.entities: 
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

            # Draw the background in parallax
            render_background(canvas, cart)
            
            # Draw the static parts of level
            render_master_map(canvas)

            # Draw the cart track
            pg.draw.line(canvas, (100, 30, 20), (0, 260), (CANVASDIM[0], 260), 2) 

            # Draw the dynamic entities
            for e in Entity.entities:
                if not Tile in type(e).__mro__:
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
            entities_copy = [entity for entity in Entity.entities]
            for e in entities_copy: # Copy necessary b/c destructive of entities list
                e.update()
    
            if not cart in Entity.entities:
                if len(Gore.particles) == 0 and len(Goo.particles) == 0:
                    dead = True
                    break # Cart was killed
    
            if cart.p.x > CANVASDIM[0]:
                break # Cart finished level

            clock.tick(40)

    # Let the player know the sad news.
    myfont = pg.font.SysFont('Comic Sans MS', 30)
    textsurface = myfont.render('GAMEOVER', False, (0, 0, 0))
    screen.blit(textsurface,(320,240))
    pg.display.update()

if __name__ == '__main__':
    main()
