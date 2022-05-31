"""
 ~~~ Coin collector game ~~~
 K_a, K_d : move left and right
 K_s  (s) : short speed boost to a direction where moving
 Try to collect 100 coins, and avoid the monsters!

"""
import sys
import math
import random
import logging
import pygame

logger = logging.getLogger(__name__)

stream_handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(message)s')
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
logger.setLevel(logging.WARN)  # INFO was used for some tests

# Default game screen resolution
RESO = (800, 600)


class InteractionObject:
    """ Default class for all interacting objects in the game """

    def __init__(
            self,
            r_image: str,  # location of image i.e. robo.png
            speed: tuple[int, int],
            start_location: tuple[int, int],
            top_start=False):
        global RESO
        # load object image
        self.__image = pygame.image.load(r_image)

        # take size width and height of objects image
        self.__w_obj = self.image.get_width()
        self.__h_obj = self.image.get_height()

        # Boundaries of movement based on screen resolution
        self.reso = RESO

        # Set initial velocity
        self.__speed = speed

        # initial angle
        self.angle = 0

        # initialize object starting location as tuple (x, y)
        if top_start:
            self.random_top_start()
        else:
            self.__location = start_location

    def random_top_start(self) -> tuple:
        """ choose random starting location from top with rand x, -200 on y"""
        self.__location = (random.randint(20,
                                          (self.reso[0] - self.__w_obj - 20)),
                           -200)

    @property
    def image(self):
        """ Return image of object """
        return self.__image

    @property
    def w_obj(self) -> int:
        """ Return width of object """
        return self.__w_obj

    @property
    def h_obj(self) -> int:
        """ Return height of object """
        return self.__h_obj

    @property
    def location(self) -> tuple:
        """ Return current location of object"""
        return self.__location

    @location.setter
    def location(self, new_location: tuple[int, int]):
        """
        Set new location for object.
        
        Bounds:
        Ground: Resolution height - Object.height
        Left bound: 0
        Right bound: Resolution width -  Object.width
        """
        new_x, new_y = new_location

        bound_left = 0
        bound_right = self.reso[0] - self.w_obj
        bound_y = self.reso[1] - self.h_obj

        if (new_x > bound_right) or (bound_left > new_x) or (new_y > bound_y):
            # logger.info(f"New location out of bounds: {new_location}")
            return

        self.__location = new_location

    @property
    def speed(self) -> tuple:
        """ Return object speed """
        return self.__speed

    @speed.setter
    def speed(self, new_speed: tuple[int, int]):
        self.__speed = new_speed


class Robo(InteractionObject):
    """ Class for robo interactions """

    def __init__(
            self,
            r_image: str,  # location of image i.e. robo.png
            speed: tuple[int, int],
            start_location: tuple[int, int]):
        super().__init__(r_image=r_image,
                         speed=speed,
                         start_location=start_location)

    def robo_move(self, way: list):
        """ Interpret events from command dict true/false 
            Dictionaries are nowadays ordered, so 
            first item is left, then right, and then jump.
        """
        x, y = self.location
        x_speed, y_speed = self.speed

        # left
        if way[0] and x > 0:
            self.location = (x - x_speed, y)
            # teleport to speed dir
            if way[2] and x - 100 > 0:
                self.location = (x - 70, y)

        # right
        if way[1] and x < self.reso[0] - self.w_obj:
            self.location = (x + x_speed, y)
            if way[2] and x + 100 <= self.reso[1] + self.w_obj:
                self.location = (x + 70, y)


class Ghost(InteractionObject):
    """ Class for ghost interactions """

    def __init__(
            self,
            r_image: str,  # location of image i.e. robo.png
            speed: tuple[int, int]):
        super().__init__(r_image=r_image,
                         speed=speed,
                         start_location=(0, 0),
                         top_start=True)

    def ghost_move(self):
        """ make ghost falling wavy """
        self.angle += 0.2
        x_osc = math.cos(self.angle)
        # Ghost speed
        x, y = self.location
        x_speed, _ = self.speed
        self.speed = (x_speed + x_osc, x_osc + 2)
        self.location = (x + x_speed + x_osc, y + x_osc + 2)


class Coin(InteractionObject):
    """ Class for coin interactions """

    def __init__(
            self,
            r_image: str,  # location of image i.e. robo.png
            speed: tuple[int, int]):
        super().__init__(r_image=r_image,
                         speed=speed,
                         start_location=(0, 0),
                         top_start=True)

    def coin_move(self):
        """ move coins, collision check after in for loop """
        x, y = self.location
        _, y_speed = self.speed
        self.location = (x, y + y_speed)


class IObjecthandler:
    """ InteractionObject handling; add/remove/keep/speed configuration"""

    def __init__(self):
        self.objects = []

    def add_robo(self, r_image, start_location=(0, 0), speed=(0, 0)):
        """ Adds robo to IO list """
        logger.info("Added robot to game")
        self.objects.append(
            Robo(r_image=r_image, start_location=start_location, speed=speed))

    def add_ghost(self, r_image, speed=(0, 2)):
        """ Adds ghost to IO list with 2 falling-speed """
        logger.info("Added ghost to game")
        self.objects.append(Ghost(r_image=r_image, speed=speed))

    def add_coin(self, r_image, speed=(0, 4)):
        """ Adds coin to IO list """
        logger.info("Added coin to game")
        self.objects.append(Coin(r_image=r_image, speed=speed))

    def del_iobject(self, idx: int):
        """ Removes IO from IO list """
        del self.objects[idx]


class CoinCollector:
    """ Main class for the pygame CoinCollector """

    def __init__(self):
        global RESO

        pygame.init()
        self.__robos = IObjecthandler()  # more than 1 player?
        self.__coins = IObjecthandler()
        self.__ghosts = IObjecthandler()
        self.reso = RESO

        # RESO: default game resolution 800x600
        self.screen = pygame.display.set_mode(self.reso)
        self.font = pygame.font.SysFont("Comic Sans", 20)
        self.end_font = pygame.font.SysFont("Comic Sans", 40)
        self.clock = pygame.time.Clock()
        pygame.display.set_caption("CoinCollector")
        self.rcolor = 0  #redness color for blit

        # coins from start
        self.coins = 0
        # coins needed for winning
        self.coins_for_win = 100
        # add operable robot, and jump checker
        self.add_robo()

        # robo movement:
        self.commands = {
            pygame.K_a: False,
            pygame.K_d: False,
            pygame.K_s: False
        }

        self.alive = True

        # increase ghosts every 10 ghosts
        self.ghosts = 0
        self.begin()

    def begin(self):
        """
        Loop through (record events and draw output)
        Summon coins/monsters randomly
        """
        logger.info("Game started")
        chance_ghosts = 130  # lower number, greater chance

        while True:
            self.event_inspector()
            self.screen_out()
            if random.randint(0, 60) == 60:
                self.add_coin()

            # every two ghosts, increase chance of getting ghosts, and
            # increase redness
            if self.ghosts == 2:
                chance_ghosts = max(chance_ghosts - 1, 0)
                self.ghosts = 0  # reset counter
                # change screen color too.
                self.rcolor = min(self.rcolor + 2, 255)
            if random.randint(0, chance_ghosts) == chance_ghosts:
                self.add_ghost()
            self.clock.tick(60)
            if not self.alive:
                break
        while True:
            self.event_inspector()

    def event_inspector(self):
        """ record specific key presses for action """

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                self.commands[event.key] = True

            if event.type == pygame.KEYUP:
                self.commands[event.key] = False

            if event.type == pygame.QUIT:
                exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F2:
                    self.__init__()
                if event.key == pygame.K_ESCAPE:
                    exit()

    def screen_out(self):
        """ render game with instructions """
        self.screen.fill((self.rcolor, 10, 10))

        coins_to_delete = []
        ghosts_to_delete = []
        # draw robot and move it
        self.screen.blit(self.robo.image, self.robo.location)
        way = [d for _, d in self.commands.items()]
        self.robo.robo_move(way)

        # draw coins
        for i, iobj in enumerate(self.__coins.objects):
            iobj.coin_move()
            c_touching = self.istouching(iobj)
            if c_touching == 0:
                coins_to_delete.append(i)
            elif c_touching == 1:
                coins_to_delete.append(i)
                self.coins += 1
            self.screen.blit(iobj.image, iobj.location)

        # Checking if coins enough for win
        # Note, coins will keep dropping after victory
        # This is on purpose. If you dont want coins dropping you
        # need to adjust self.alive to False
        if self.coins >= self.coins_for_win:
            self.win_game()
            return
        # draw ghosts
        for j, iobj in enumerate(self.__ghosts.objects):
            iobj.ghost_move()
            ghost_touching = self.istouching(iobj)
            if ghost_touching == 0:
                ghosts_to_delete.append(j)
            elif ghost_touching == 1:
                self.alive = False
                self.lost_game()
                break

            self.screen.blit(iobj.image, iobj.location)

        # delete coins and ghosts that have reached the ground or picked
        for c in coins_to_delete:
            self.__coins.del_iobject(c)

        for g in ghosts_to_delete:
            self.__ghosts.del_iobject(g)

        # render texts
        _coins = self.font.render(f"Coins collected: {self.coins}", True,
                                  (150, 150, 0))
        self.screen.blit(_coins, (10, 0))

        _newg = self.font.render("F2 to restart game", True, (100, 0, 250))
        self.screen.blit(_newg, (self.reso[0] / 2 - 70, 0))

        _exg = self.font.render("Esc to quit", True, (100, 100, 100))
        self.screen.blit(_exg, (self.reso[0] - 110, 0))

        pygame.display.flip()

    def add_coin(self):
        """ add dropping coins with speed 2"""
        self.__coins.add_coin(r_image="kolikko.png")

    def add_ghost(self):
        """ add dropping ghosts to game with speed 4"""
        self.__ghosts.add_ghost(r_image="hirvio.png")
        self.ghosts += 1

    def add_robo(self):
        """ add the controllable robot to list, and define it to be robo"""
        self.__robos.add_robo(r_image="robo.png",
                              start_location=(0, self.reso[1] - 90),
                              speed=(5, 0))
        self.robo = self.__robos.objects[0]

    def istouching(self, io: InteractionObject):
        """ check to see if robot and object are touching """
        obj_x, obj_y = io.location
        robo_x, robo_y = self.robo.location

        # error bounds img location is in upper left corner of image
        x_touching = abs(obj_x - robo_x)

        # if obj is on right side of robo, then robo width matters, else
        # obj width - comparing upper left corners again
        if obj_x > robo_x:
            x_error = self.robo.w_obj
        else:
            x_error = io.w_obj

        y_touching = abs(obj_y - robo_y)
        # Only obj height matters for touching robo head
        y_error = io.h_obj

        collision_y = y_touching - y_error
        collision_x = x_touching - x_error

        if obj_y >= self.reso[1] - io.h_obj - 20:
            return 0

        if collision_y <= 0 and collision_x <= 0:
            logger.info(f"Collision {collision_y}, {collision_x}")
            return 1
        return 3

    def win_game(self):
        """ game won """
        g_end = self.end_font.render(" YOU WON THE GAME ", True, (255, 255, 0))
        g_end_rect = g_end.get_rect(center=self.screen.get_rect().center)
        self.screen.blit(g_end, g_end_rect)
        self.game_end()

    def lost_game(self):
        """ game lost msg """
        g_end = self.end_font.render(" YOU GOT EATEN BY A GHOST ", True,
                                     (150, 10, 150))
        g_end_rect = g_end.get_rect(center=self.screen.get_rect().center)
        self.screen.blit(g_end, g_end_rect)
        self.game_end()

    def game_end(self):
        """Game end, and tips"""

        tips = self.font.render("Press F2 to restart, ESC to quit", True,
                                (100, 100, 150))
        tips_rect = tips.get_rect(center=(self.reso[0] / 2,
                                          self.reso[1] / 2 + 40))
        self.screen.blit(tips, tips_rect)
        tips_2 = self.font.render(
            "Did you know if you press S while moving you can teleport a distance?",
            True, (255, 255, 255))

        tips_2rect = tips_2.get_rect(center=(self.reso[0] / 2,
                                             self.reso[1] - 40))
        self.screen.blit(tips_2, tips_2rect)
        pygame.display.flip()


if __name__ == "__main__":
    CoinCollector()
