import pygame
import random
from pygame.locals import *



class Machine():
    """
    THIS CLASS IS THE STATE MACHINE FOR THE APPLICATION
    """
    def __init__(self):
        self.transitions = {}
        self.state = 'pause'

    def addTransition(self,**kwargs):
        if kwargs['name'] in self.transitions:
            self.transitions[kwargs['name']]['states'].append(kwargs['state'])
        else:
            self.transitions[kwargs['name']] = {'states':[kwargs['state']]}
            #self.transitions[kwargs['name']]['states'].add(kwargs['state'])
            print(self.transitions[kwargs['name']]['states'])
#            self.transitions[kwargs['name']]['states'] = [kwargs['state']]

    def update(self,state):
        if self.transitions[state] and self.state in self.transitions[state]['states']:
            self.state = state
            print(self.state)
        else:
            # error states
            pass

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
        self.direction = ''

    def handleKeyPress(self,key):
        if key == K_UP:
            self.direction = 'u'
        elif key == K_DOWN:
            self.direction = 'd'
        else:
            self.direction = ''

    def update(self):
        if app_machine.state == 'forward':
            self.image = pygame.image.load("./resources/robot_right.png")
        if app_machine.state == 'backward':
            self.image = pygame.image.load("./resources/robot_left.png")

    def set_direction(self,d):
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
        self.rect.x += 1 if app_machine.state == 'backward' else -1
        if self.rect.x < -20 or app_machine.state == 'pause':
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
        self.direction = 'l' if app_machine.state == 'backward' else 'r'
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

app_machine = Machine()
app_machine.addTransition(name='forward', state='off')
app_machine.addTransition(name='forward', state='pause')
app_machine.addTransition(name='forward', state='backward')
app_machine.addTransition(name='backward', state='forward')
app_machine.addTransition(name='backward', state='pause')
app_machine.addTransition(name='off', state='forward')
app_machine.addTransition(name='off', state='backward')
app_machine.addTransition(name='off', state='pause')
app_machine.addTransition(name='pause', state='forward')
app_machine.addTransition(name='pause', state='backward')

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

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                app_machine.update('end')
            elif event.type == KEYDOWN:
                if event.key == K_LEFT:
                    app_machine.update('backward')
                elif event.key == K_RIGHT:
                    app_machine.update('forward')
                elif event.key == K_s:
                    app_machine.update('off')
                elif event.key == K_p:
                    app_machine.update('pause')
                elif event.key == K_SPACE:
                    laser = Laser((255,0,0),10,10,robot1)
                    laser_sprites_list.add(laser)
                    all_sprites_list.add(laser)

                robot1.handleKeyPress(event.key)

        if app_machine.state == 'forward' or app_machine.state == 'backward':
        # handle thrusters
            if pygame.key.get_pressed()[K_UP]:
                robot1.set_direction('u')
            if pygame.key.get_pressed()[K_DOWN]:
                robot1.set_direction('d')
        # drop mines
            if (release_timer + 2000) < pygame.time.get_ticks():
                if app_machine.state == 'forward':
                    release_timer = pygame.time.get_ticks()
                    mine = Mine((0,0,255),20,20)
                    mine_sprites_list.add(mine)
                    all_sprites_list.add(mine)
        # update screen scroll
            bgx += 1 if app_machine.state == 'backward' else -1
            if bgx < -468:
                bgx = 0
            if bgx == 1:
                bgx = -468

        elif app_machine.state == 'pause':
            pass
        elif app_machine.state == 'off':
            running = False
        else:
            pass


        shot_mine_list = pygame.sprite.groupcollide(laser_sprites_list, mine_sprites_list, True, True)
        if len(shot_mine_list) > 0 and lives > 0:
            score = score + (len(shot_mine_list) * 10)

        hit_mine_list = pygame.sprite.spritecollide(robot1, mine_sprites_list, False)

        for m in hit_mine_list:
            if m.exploded == False:
                m.explode()
                lives = lives - 1

        if lives <= 0:
            app_machine.update('pause')
            #robot1.kill()
            score = 0

        screen.blit(logo,(bgx,0))

        all_sprites_list.update()
        all_sprites_list.draw(screen)

        basicfont = pygame.font.SysFont(None, 40)
        if app_machine.state == 'off':
            text = basicfont.render('Game Over', True, (0,255,0), (0, 0, 0))
        elif app_machine.state == 'pause':
            text = basicfont.render('Paused', True, (0,255,0), (0, 0, 0))
        else:
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
