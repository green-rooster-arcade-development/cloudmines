import pygame
import random
from pygame.locals import *

class Robot(pygame.sprite.Sprite):
    """
    THIS CLASS REPRESENTS THE PLAYER
    """
    def __init__(self,color,width,height,player=False):
        super().__init__()
        self.image = pygame.image.load("./resources/robot_right.png")
        #self.image = pygame.Surface((width,height))
        #self.image.fill(color)
        self.isplayer = player
        self.rect = self.image.get_rect()
        self.rect.x = 60
        self.rect.y = 40
        self.direction = 'r'

    def update(self):
        pass

    def set_direction(self,d):
        if d == 'l':
            self.image = pygame.image.load("./resources/robot_left.png")
            self.direction = 'l'
        if d == 'r':
            self.image = pygame.image.load("./resources/robot_right.png")
            self.direction = 'r'
        if d == 'u':
            self.rect.y -= 5
        if d == 'd':
            self.rect.y += 5

class Mine(pygame.sprite.Sprite):
    """
    THIS CLASS REPRESETS A FLOATING MINE
    """
    def __init__(self,color,width,height):
        super().__init__()
        self.image = pygame.Surface((width,height))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.y = random.randrange(0, ( 280 - height ))
        self.rect.x = 240
        self.exploded = False
        self.boom = pygame.mixer.Sound('./resources/explode.wav')

    def update(self):
        self.rect.x -= 1
        if self.rect.x < -20:
            self.kill()

    def explode(self):
        self.boom.play()
        self.exploded = True
        self.image.fill((255,0,0))

class Laser(pygame.sprite.Sprite):
    """
    THIS CLASS REPRESENTS A LASER BEAM
    """
    def __init__(self,color,width,height,robot):
        super().__init__()
        self.image = pygame.Surface((width,height))
        self.image.fill(color)
        self.direction = robot.direction
        self.rect = self.image.get_rect()
        self.rect.x = robot.rect.x + 40
        self.rect.y = robot.rect.y + 40

    def update(self):
        if self.direction == 'l':
            self.rect.x -= 2
        if self.direction == 'r':
            self.rect.x += 2


        if self.rect.x < -9 or self.rect.x > 243:
            self.kill()


def main():

    # Initialize the PyGame module
    pygame.init()

    logo = pygame.image.load("./resources/scroll_bg.png")
    pygame.display.set_icon(logo)
    pygame.display.set_caption("Cloud Mines")


    # Initialize the screen
    screen = pygame.display.set_mode((244,280))

    screen.blit(logo,(0,0))

    running = True
    clock = pygame.time.Clock()
    robot_sprites_list = pygame.sprite.Group()
    mine_sprites_list = pygame.sprite.Group()
    laser_sprites_list = pygame.sprite.Group()
    all_sprites_list = pygame.sprite.Group()
    robot1 = Robot((255,0,0),40,40,True)
    all_sprites_list.add(robot1)
    robot_sprites_list.add(robot1)

    all_sprites_list.draw(screen)
    pygame.display.flip();

    bgx = 0;
    release_timer = 0;
    score = 0;
    lives = 3;
    # Main loop
    while running:

        # event handling - get all the events from the queue
        for event in pygame.event.get():
            # do something when the event is QUIT
            if event.type == pygame.QUIT:
                # change the loop value to false
                running = False
            elif event.type == KEYDOWN:
                    if event.key == K_UP:
                        robot1.set_direction('u')
                    elif event.key == K_DOWN:
                        robot1.set_direction('d')
                    elif event.key == K_LEFT:
                        robot1.set_direction('l')
                    elif event.key == K_RIGHT:
                        robot1.set_direction('r')
                    elif event.key == K_SPACE:
                        laser = Laser((255,0,0),10,10,robot1)
                        laser_sprites_list.add(laser)
                        all_sprites_list.add(laser)

        if pygame.key.get_pressed()[K_UP]:
            robot1.set_direction('u')

        if pygame.key.get_pressed()[K_DOWN]:
            robot1.set_direction('d')

        bgx += 1 if robot1.direction == 'l' else -1;
        if bgx < -468:
            bgx = 0
        if bgx == 1:
            bgx = -468
        if (release_timer + 2000) < pygame.time.get_ticks():
            mine = Mine((0,0,255),20,20)
            mine_sprites_list.add(mine)
            all_sprites_list.add(mine)
            release_timer = pygame.time.get_ticks()


        shot_mine_list = pygame.sprite.groupcollide(laser_sprites_list, mine_sprites_list, True, True)
        if len(shot_mine_list) > 0 and lives > 0:
            score = score + (len(shot_mine_list) * 10)

        hit_mine_list = pygame.sprite.spritecollide(robot1, mine_sprites_list, False)

        for m in hit_mine_list:
            if m.exploded == False:
                m.explode()
                lives = lives - 1

        if lives <= 0:
            robot1.kill()
            score = 'Game Over'

        screen.blit(logo,(bgx,0))

        all_sprites_list.update()
        all_sprites_list.draw(screen)

        basicfont = pygame.font.SysFont(None, 40)
        text = basicfont.render('%s'%score, True, (0,255, 0), (0, 0, 0))
        textrect = text.get_rect()
        textrect.centerx = screen.get_rect().centerx
        textrect.y = 240
        textrect.width = 80
        screen.blit(text, textrect)

        posx = 0
        posy = 260
        for x in range(0,lives):
            bot = pygame.Surface((10,10))
            bot.fill((0,255,0))
            posx = posx + 15
            screen.blit(bot, (posx,posy) )

        clock.tick(60)
        pygame.display.flip()

if __name__ == "__main__":
    main()
