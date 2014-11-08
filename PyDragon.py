# PyDragon (a Dragon Quest/Warrior clone)
# By Emre Motan  emre@emremotan.com
# Released under a "Simplified BSD" license

import random, sys, copy, os, pygame, ConfigParser
os.environ['PYGAME_FREETYPE'] = '1'
import pygame.locals as pg
from pygame.mixer import *
import logging

logger = logging.getLogger('scope.name')
file_log_handler = logging.FileHandler('logfile.log')
logger.addHandler(file_log_handler)
stderr_log_handler = logging.StreamHandler()
logger.addHandler(stderr_log_handler)


FPS = 30 # frames per second to update the screen
WINWIDTH = 512 # width of the program's window, in pixels
WINHEIGHT = 480 # height in pixels
HALF_WINWIDTH = int(WINWIDTH / 2)
HALF_WINHEIGHT = int(WINHEIGHT / 2)

# The total width and height of each tile in pixels.
TILEWIDTH = 32
TILEHEIGHT = 32

screen = 0

# Motion offsets for particular directions
#     N  E  S   W
DX = [0, 1, 0, -1]
DY = [-1, 0, 1, 0]

global FPSCLOCK, DISPLAYSURF, IMAGESDICT, TILEMAPPING, OUTSIDEDECOMAPPING, BASICFONT, PLAYERIMAGES, currentImage

class Map(object):
    """Load and store the map of the level, together with all the items."""

    def __init__(self, filename="Maps\level.map"):
        self.tileset = ''
        self.map = []
        self.width = 0
        self.height = 0
        self.load_file(filename)

    def load_file(self, filename="Maps\level.map"):
        """Load the level from specified file."""

        parser = ConfigParser.ConfigParser()
        parser.read(filename)
        self.tileset = parser.get("level", "tileset")

        #Load main game tileset
        self.MAPTILESET = self.load_tile_table(self.tileset, 32, 32)

        self.map = []
        self.map_pre = parser.get("level", "map").split("\n")

        for line in self.map_pre:
            self.map.append(line.strip().split(","))

        self.width = len(self.map[0])
        self.height = len(self.map)

    def load_tile_table(self, filename, width, height):
        """Load an image and split it into tiles."""

        image = pygame.image.load(filename).convert()
        image_width, image_height = image.get_size()
        tile_table = []
        for tile_y in range(0, image_height/height):
            line = []
            for tile_x in range(0, image_width/width):
                rect = (tile_x*width, tile_y*height, width, height)
                tile_table.append(image.subsurface(rect))
        return tile_table

    def render(self):
        """Draw the level on the surface."""

        image = pygame.Surface((self.width*TILEWIDTH, self.height*TILEHEIGHT))

        map_y = 0
        map_x = 0

        #for x, row in enumerate(self.MAPTILESET):
        #    for y, tile in enumerate(row):
        #        image.blit(tile, (x * 32, y * 32))

        for y, line in enumerate(self.map):
            for x, c in enumerate(line):
                tile_image = self.MAPTILESET[int(c)]
                image.blit(tile_image, (x*TILEWIDTH, y*TILEHEIGHT))

        screen.blit(image, (0, 0))

class Player():
    """ Display and animate the player character."""

    is_player = True

    mapPosX = 0
    mapPosY = 0

    def __init__(self, pos=(1, 1)):
        #Sprite.__init__(self, pos)
        self.direction = 0
        self.animation = None

        Player.name = "Emre"
        Player.Stats = { "Strength": 25,
                         "HP": 50,
                         "MaxHP": 50}
        Player.Equipped = { "Weapon": "Wooden Sword",
                            "Armor": "Cloth Tunic",
                            "Helm": "Hair"}

        self.SPRITESET = self.load_tile_table("Images\player.png", 32, 32)

    def walk_animation(self):
        """Animation for the player walking."""

        # # This animation is hardcoded for 4 frames and 16x24 map tiles
        # for frame in range(4):
        #     self.image = self.frames[self.direction][frame]
        #     yield None
        #     self.move(3*DX[self.direction], 2*DY[self.direction])
        #     yield None
        #     self.move(3*DX[self.direction], 2*DY[self.direction])

    def render(self):
        """Draw the player on the surface."""

        image = pygame.Surface((1*TILEWIDTH, 1*TILEHEIGHT))

        tile_image = self.SPRITESET[0].convert()
        transColor = tile_image.get_at((0,0))
        tile_image.set_colorkey(transColor)
        image.blit(tile_image, (0, 0))

        screen.blit(image, (self.mapPosX * TILEWIDTH, self.mapPosY * TILEHEIGHT))

    def load_tile_table(self, filename, width, height):
        """Load an image and split it into tiles."""

        image = pygame.image.load(filename).convert()
        image_width, image_height = image.get_size()
        tile_table = []
        for tile_y in range(0, image_height/height):
            line = []
            for tile_x in range(0, image_width/width):
                rect = (tile_x*width, tile_y*height, width, height)
                tile_table.append(image.subsurface(rect))
        return tile_table


'''
    def update(self, *args):
        """Run the current animation or just stand there if no animation set."""

        if self.animation is None:
            self.image = self.frames[self.direction][0]
        else:
            try:
                self.animation.next()
            except StopIteration:
                self.animation = None
'''

class Game(object):
    """The main game object."""

    def __init__(self):
        self.pressed_key = None
        self.quit = False
        #self.shadows = pygame.sprite.RenderUpdates()
        #self.sprites = SortedUpdates()
        #self.overlays = pygame.sprite.RenderUpdates()
        #self.use_level(Level())

    def main(self):
        """Run the main loop."""

        #TitleScreen().main()

        self.InitNewGame()

        self.MainGameLoop()

        terminate()

    def InitNewGame(self):
        self.player = Player()

        # Load map
        self.map = Map()

        self.player.mapPosX = 1
        self.player.mapPosY = 1

        # Go to MainGameLoop()
        self.MainGameLoop()

    def control(self):
        """Handle the controls of the game."""

        keys = pygame.key.get_pressed()

        def pressed(key):
            """Check if the specified key is pressed."""

            return self.pressed_key == key or keys[key]

        def walk(d):
            """Start walking in specified direction."""

            x, y = self.player.pos
            self.player.direction = d
            #if not self.level.is_blocking(x+DX[d], y+DY[d]):
            #    self.player.animation = self.player.walk_animation()

            if pressed(pg.K_UP):
                walk(0)
            elif pressed(pg.K_DOWN):
                walk(2)
            elif pressed(pg.K_LEFT):
                walk(3)
            elif pressed(pg.K_RIGHT):
                walk(1)
            self.pressed_key = None

    def MainGameLoop(self):
        # The main game loop
        while not self.quit:
            # Clear screen
            screen.fill((0,0,0)) # Black (must be tuple with appropriate parentheses)

            # Draw map on background
            self.map.render()

            # Draw Player on surface
            self.player.render()

            # Draw NPCs on surface

            pygame.display.flip()

            # Get Player Input
            # Process pygame events
            for event in pygame.event.get():
                if event.type == pg.QUIT:
                    terminate()
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        terminate()
                    self.pressed_key = event.key

            # Update environment based on input
            if self.player.animation is None:
                self.control()
                #self.player.update()


            # Wait for one tick of the game clock
            #clock.tick(15)

class TitleScreen(object):

    def __init__(self):
        self.IMAGESDICT = {'title': pygame.image.load('Images\DragonWarriorTitleScreen.png')}
        self.titleRect = self.IMAGESDICT['title'].get_rect()
        self.titleRect.centery = HALF_WINHEIGHT
        self.titleRect.centerx = HALF_WINWIDTH

    def main(self):
        # Draw the whole screen initially
        screen.fill((0, 0, 0)) # Black (must be tuple with appropriate parentheses)
        screen.blit(self.IMAGESDICT['title'], self.titleRect)
        pygame.display.flip()

        pygame.mixer.init(96000)
        pygame.mixer.music.load("C:\Dev\PyDragon\Music\(002-048) Dragon Quest - Koichi Sugiyama.mp3")
        pygame.mixer.music.play()

        while True: # Main loop for the start screen.
            for event in pygame.event.get():
                if event.type == pg.QUIT:
                    terminate()
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        terminate()
                    if event.key == pg.K_RETURN:
                        pygame.mixer.music.stop()
                        return # user has pressed a key, so return.

            pygame.display.update()
            clock.tick()

# def main():
#
#
#     # Pygame initialization and basic set up of the global variables.
#     pygame.init()
#     FPSCLOCK = pygame.time.Clock()
#
#
#
#     # Because the Surface object stored in DISPLAYSURF was returned
#     # from the pygame.display.set_mode() function, this is the
#     # Surface object that is drawn to the actual computer screen
#     # when pygame.display.update() is called.
#     DISPLAYSURF = pygame.display.set_mode((WINWIDTH, WINHEIGHT))
#
#     pygame.display.set_caption('PyDragon')
#     BASICFONT = pygame.font.SysFont('arial', 30) #pygame.freetype.Font('dw-font.ttf', 18, 0)
#
#     # A global dict value that will contain all the Pygame
#     # Surface objects returned by pygame.image.load().
#
#     # startScreen() # show the title screen until the user presses a key
#
#     # Load main game tileset
#     MAPTILESET = load_tile_table("Images\dw1tileset.png", 32, 32)
#
#     xOffset = 0
#     yOffset = 0
#
#     while True: # Main loop
#         for event in pygame.event.get():
#             if event.type == QUIT:
#                 terminate()
#             elif event.type == KEYDOWN:
#                 if event.key == K_ESCAPE:
#                     terminate()
#                 if event.key == K_DOWN:
#                     yOffset += 1
#                 if event.key == K_RETURN:
#                     return # user has pressed a key, so return.
#
#         for x, row in enumerate(MAPTILESET):
#             for y, tile in enumerate(row):
#                 DISPLAYSURF.blit(tile, (x * 32 + xOffset, y * 32 + yOffset))
#
#         DISPLAYSURF.blit(BASICFONT.render("Hello, World", False, (255,255,255)), (100,100))
#
#         #DISPLAYSURF.blit(MAPTILESET[0][0], (0, 0))
#
#         # Display the DISPLAYSURF contents to the actual screen.
#         pygame.display.update()
#         #pygame.display.flip()
#         FPSCLOCK.tick()


def terminate():
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    pygame.init()
    clock = pygame.time.Clock()
    pygame.display.set_mode((512, 480))
    BASICFONT = pygame.font.SysFont('arial', 30) #pygame.freetype.Font('dw-font.ttf', 18, 0)
    screen = pygame.display.get_surface()

    # nice output format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_log_handler.setFormatter(formatter)
    stderr_log_handler.setFormatter(formatter)
    logger.setLevel(logging.INFO)

    Game().main()