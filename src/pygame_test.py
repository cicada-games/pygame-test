import pygame as pg
from pygame.locals import *
import os
import sys
import math

main_dir = sys.argv[1] # run like: python3 pygame_test.py $(pwd)

class Vec2_f:
    x = 0.0
    y = 0.0

    def __init__( self, x, y ):
        self.x = x 
        self.y = y

TILE_SIZE = 20

chunk_tilemap = []
for _ in range(30):
    chunk_tilemap.append([" "] * 40 )

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
    print(file)
    try:
        surface = pg.image.load(file)
    except pg.error:
        raise SystemExit('Could not load image "%s" %s' % (file, pg.get_error()))
    return surface.convert()

CANVASDIM = 640*2, 480
CANVASRECT = pg.Rect(0, 0, CANVASDIM[0], CANVASDIM[1])

SCREENDIM = 640, 480
SCREENRECT = pg.Rect(0, 0, SCREENDIM[0], SCREENDIM[1])

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
    chunk_file = open("chunks/chunk1", "r")
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

    ## END JB PARSE LEVEL CHUNK

    background = pg.Surface(SCREENRECT.size)
    background.fill((255, 255, 255))
    background.blit(grass, ((SCREENDIM[0]-grass.get_width())/2, SCREENDIM[1]-grass.get_height()))

    ## JB RENDER TILEMAP CHUNK
    for row_num, row_arr in enumerate(chunk_tilemap):
        for col_num, val in enumerate( row_arr ):
            if( val == '#'):
                dest_tile_tect = pg.Rect(col_num * TILE_SIZE, row_num * TILE_SIZE, TILE_SIZE, TILE_SIZE )
                background.blit(tile, dest_tile_tect )
    ## JB END RENDER TILEMAP CHUNK

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
                mouse_pos = pg.mouse.get_pos()
                pg.draw.circle(background, (0,0,0), pg.mouse.get_pos(), 3, 3)
        screen.blit(background, (0, 0))
        # JB FOLLOW PATH
            # move entity to next position if hasn't reach last point
            # TODO: stop entity after reaches end
        if entity_position.x >= points[ target_point ].x and target_point < len(points) - 1:
            target_point+=1 
            # find next velocity
            # subtract
            dist = Vec2_f(0,0)
            dist.x = points[ target_point ].x - entity_position.x 
            dist.y = points[ target_point ].y - entity_position.y 
            # unit vector
            direction = Vec2_f(0,0)
            direction.x = dist.x / math.sqrt( dist.x*dist.x + dist.y*dist.y )
            direction.y = dist.y / math.sqrt( dist.x*dist.x + dist.y*dist.y )
            # set velocity
            entity_velocity.x = direction.x * entity_speed
            entity_velocity.y = direction.y * entity_speed

        entity_position.x += entity_velocity.x
        entity_position.y += entity_velocity.y
            
    
        pg.draw.circle( background, (255,0,0), (point1.x, point1.y), 3, 3 )
        pg.draw.circle( background, (255,0,0), (point2.x, point2.y), 3, 3 )
        pg.draw.circle( background, (255,0,0), (point3.x, point3.y), 3, 3 )
        
        pg.draw.circle( background, (0,0,255), (entity_position.x, entity_position.y ), 3, 3 )
        # JB END FOLLOW PATH

        pg.display.update()
        clock.tick(40)

if __name__ == '__main__':
    main()
