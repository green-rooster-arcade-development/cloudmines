import pygame
import random
from pygame.locals import *

"""
STATES
"""
APP_OFF      = "off"
APP_WIN      = "win"
APP_FAIL     = "fail"
APP_PAUSE    = "pause"
APP_FORWARD  = "forward"
APP_BACKWARD = "backward"

"""
SETTINGS
"""
DISP_WIDTH         = 244
DISP_HEIGHT        = 280
DISP_STATUS_HEIGTH = 40
TEXT_GAMETITLE     = "Cloud Mines"
TEXT_GAMEOVER      = "GAME OVER"
TEXT_GAMEPAUSE     = "PAUSED"
TEXT_GAMECONGRATS  = "CONGRATS"
SOUND_MINE         = "./resources/explode.wav"
SOUND_LASERSHOT    = ""
SOUND_LASERHIT     = ""
DATA_TOPSCORE      = 300
DATA_LIVES         = 3

class Machine():
    """
    THIS CLASS IS THE STATE MACHINE FOR THE APPLICATION
    """
    def __init__(self):
        self.transitions = {}
        self.state = APP_PAUSE

    def addTransition(self,**kwargs):
        if kwargs['name'] in self.transitions:
            self.transitions[kwargs['name']]['states'].append(kwargs['state'])
        else:
            self.transitions[kwargs['name']] = {'states':[kwargs['state']]}

    def update(self,state):
        if state in self.transitions and self.state in self.transitions[state]['states']:
            self.state = state
        else:
            print('ERROR: Could Not Switch To State %s From %s' % (state,self.state))

class Robot(pygame.sprite.Sprite):
    """
    THIS CLASS REPRESENTS THE PLAYER
    """
    DIR_UP = "up"
    DIR_DN = "dn"
    BOOST = 5

    def __init__(self,color,width,height,player=False):
        super().__init__()
        self.image = pygame.image.load("./resources/robot_right.png")
        self.image = pygame.transform.scale(self.image, (width,height))
        self.isplayer = player
        self.rect = self.image.get_rect()

        # GET THE X,Y COORDS OFF THE DISPLAY AND IMAGE SIZE
        # EXTRA 40 PIXELS FROM BASE FOR SCOREBOARD

        self.rect.x = ((DISP_WIDTH-self.rect.width)/2)
        self.rect.y = ((DISP_HEIGHT-self.rect.height)/2)-40
        self.direction = ''
        self.lives = DATA_LIVES
        self.score = 0

    def updateLives(self,val):
        self.lives += val
        if self.lives <= 0:
            app_machine.update(APP_FAIL)
            self.kill()

    def updateScore(self,val):
        self.score += val
        if self.score > DATA_TOPSCORE:
            app_machine.update(APP_WIN)
            self.kill()

    def handleKeyPress(self,key):
        if key == K_UP:
            self.direction = Robot.DIR_UP
        elif key == K_DOWN:
            self.direction = Robot.DIR_DN
        else:
            self.direction = ''

    def update(self):
        if app_machine.state == APP_FORWARD:
            self.image = pygame.transform.scale( pygame.image.load("./resources/robot_right.png"), (self.rect.width, self.rect.height))
        if app_machine.state == APP_BACKWARD:
            self.image = pygame.transform.scale( pygame.image.load("./resources/robot_left.png"), (self.rect.width, self.rect.height))

    def boost(self):
        if self.direction == Robot.DIR_UP:
            self.rect.y -= Robot.BOOST
        if self.direction == Robot.DIR_DN:
            self.rect.y += Robot.BOOST

class Mine(pygame.sprite.Sprite):
    """
    THIS CLASS REPRESETS A FLOATING MINE
    """
    STEP = 1

    def __init__(self,color,width,height):
        super().__init__()
        self.image = pygame.Surface((width,height))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.y = random.randrange(0, (DISP_HEIGHT-height))
        self.rect.x = DISP_WIDTH
        self.exploded = False
        self.boom = pygame.mixer.Sound(SOUND_MINE)

    def update(self):
        if app_machine.state == APP_BACKWARD:
            self.rect.x += Mine.STEP
        else:
            self.rect.x -= Mine.STEP
        if (self.rect.x+self.rect.width) < 0 or app_machine.state in [APP_PAUSE,APP_FAIL]:
            self.kill()

    def explode(self):
        self.boom.play()
        self.exploded = True
        self.image.fill((255,0,0))

class Laser(pygame.sprite.Sprite):
    """
    THIS CLASS REPRESENTS A LASER BEAM
    """

    LEFT  = "left"
    RIGHT = "right"
    STEP  = 2

    def __init__(self,color,width,height,robot):
        super().__init__()
        self.image = pygame.Surface((width,height))
        self.image.fill(color)
        self.direction = Laser.LEFT if app_machine.state == APP_BACKWARD else Laser.RIGHT
        self.rect = self.image.get_rect()
        self.rect.x = robot.rect.x + ((robot.rect.width-width)/2)
        self.rect.y = robot.rect.y + ((robot.rect.height-height)/2)
        if SOUND_LASERSHOT:
            pygame.mixer.Sound(SOUND_LASERSHOT).play()

    def update(self):
        if self.direction == Laser.LEFT:
            self.rect.x -= Laser.STEP
        if self.direction == Laser.RIGHT:
            self.rect.x += Laser.STEP
        if (self.rect.x+self.rect.width) < 0 or self.rect.x > (DISP_WIDTH):
            if SOUND_LASERHIT:
                pygame.mixer.Sound(SOUND_LASERHIT).play()
            self.kill()


app_machine = Machine()
app_machine.addTransition(name=APP_FORWARD,  state=APP_OFF)
app_machine.addTransition(name=APP_FORWARD,  state=APP_PAUSE)
app_machine.addTransition(name=APP_FORWARD,  state=APP_BACKWARD)
app_machine.addTransition(name=APP_BACKWARD, state=APP_FORWARD)
app_machine.addTransition(name=APP_BACKWARD, state=APP_PAUSE)
app_machine.addTransition(name=APP_OFF,      state=APP_FORWARD)
app_machine.addTransition(name=APP_OFF,      state=APP_BACKWARD)
app_machine.addTransition(name=APP_OFF,      state=APP_PAUSE)
app_machine.addTransition(name=APP_OFF,      state=APP_FAIL)
app_machine.addTransition(name=APP_PAUSE,    state=APP_FORWARD)
app_machine.addTransition(name=APP_PAUSE,    state=APP_BACKWARD)
app_machine.addTransition(name=APP_FAIL,     state=APP_FORWARD)
app_machine.addTransition(name=APP_FAIL,     state=APP_BACKWARD)
app_machine.addTransition(name=APP_WIN,      state=APP_FORWARD)
app_machine.addTransition(name=APP_WIN,      state=APP_BACKWARD)

def scrollBackground(xpos):
    limit = -468
    if app_machine.state == APP_BACKWARD:
        xpos += 1
    if app_machine.state == APP_FORWARD:
        xpos -= 1
    if xpos < limit:
        xpos = 0
    if xpos == 1:
        xpos = limit
    return xpos

def writeStatusBar(screen, robot):
    basicfont = pygame.font.SysFont(None, DISP_STATUS_HEIGTH)
    if app_machine.state is APP_FAIL:
        text = basicfont.render(TEXT_GAMEOVER, True, (0,255,0), (0, 0, 0))
    elif app_machine.state is APP_PAUSE:
        text = basicfont.render(TEXT_GAMEPAUSE, True, (0,255,0), (0, 0, 0))
    elif app_machine.state is APP_WIN:
        text = basicfont.render(TEXT_GAMECONGRATS, True, (0,255,0), (0, 0, 0))
    else:
        text = basicfont.render('%s'%robot.score, True, (0,255, 0), (0, 0, 0))
    textrect = text.get_rect()
    textrect.centerx = screen.get_rect().centerx
    textrect.y = (DISP_HEIGHT-40)
    textrect.width = 80
    screen.blit(text, textrect)

    if app_machine.state in [APP_FORWARD,APP_BACKWARD]:
        posx = 0
        posy = 260
        for x in range(0,robot.lives):
            bot = pygame.Surface((10,10))
            bot.fill((0,255,0))
            posx = posx + 15
            screen.blit(bot, (posx,posy) )


def main():
    # INITIALIZE PYGAME
    pygame.init()

    logo = pygame.image.load("./resources/scroll_bg.png")
    pygame.display.set_icon(logo)
    pygame.display.set_caption(TEXT_GAMETITLE)

    # INITIALIZE SCREEN
    screen = pygame.display.set_mode((DISP_WIDTH,DISP_HEIGHT))
    screen.blit(logo,(0,0))

    # SET MAIN LOOP VARIABLES
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

    background_xpos = 0;
    release_timer = 0;

    # MAIN LOOP
    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == KEYDOWN:
                if event.key == K_LEFT:
                    app_machine.update(APP_BACKWARD)
                elif event.key == K_RIGHT:
                    app_machine.update(APP_FORWARD)
                elif event.key == K_s:
                    app_machine.update(APP_OFF)
                elif event.key == K_p:
                    app_machine.update(APP_PAUSE)
                elif event.key == K_SPACE:
                    laser = Laser((255,0,0),10,10,robot1)
                    laser_sprites_list.add(laser)
                    all_sprites_list.add(laser)

                robot1.handleKeyPress(event.key)

        if app_machine.state == APP_FORWARD or app_machine.state == APP_BACKWARD:
        # handle thrusters
            if pygame.key.get_pressed()[K_UP] or pygame.key.get_pressed()[K_DOWN]:
                robot1.boost()
        # drop mines
            if (release_timer + 2000) < pygame.time.get_ticks():
                if app_machine.state == APP_FORWARD:
                    release_timer = pygame.time.get_ticks()
                    mine = Mine((0,0,255),20,20)
                    mine_sprites_list.add(mine)
                    all_sprites_list.add(mine)
        # update screen scroll
            background_xpos = scrollBackground(background_xpos)

        elif app_machine.state == APP_WIN:
            pass
        elif app_machine.state == APP_PAUSE:
            pass
        elif app_machine.state == APP_OFF:
            running = False
        else:
            pass


        shot_mine_list = pygame.sprite.groupcollide(laser_sprites_list, mine_sprites_list, True, True)
        if len(shot_mine_list) > 0:
            robot1.updateScore((len(shot_mine_list) * 10))

        hit_mine_list = pygame.sprite.spritecollide(robot1, mine_sprites_list, False)

        for m in hit_mine_list:
            if m.exploded == False:
                m.explode()
                robot1.updateLives(-1)

        screen.blit(logo,(background_xpos,0))
        writeStatusBar(screen, robot1)

        all_sprites_list.update()
        all_sprites_list.draw(screen)


        clock.tick(60)
        pygame.display.flip()

if __name__ == "__main__":
    main()
