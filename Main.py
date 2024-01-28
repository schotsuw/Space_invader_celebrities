from typing import Any
import pygame
import asyncio
from pygame import mixer
from pygame.locals import *
from pygame.sprite import Group
import random



pygame.font.init()

#sounds effect
pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
#define fps
clock = pygame.time.Clock()
#limited fps(framerate)
fps = 60
screen_width = 1200
screen_height = 600
#define game variable
rows = 3
cols = 11
alien_cooldown = 1000 



#gameover: 0 is game over, 1 is won, -1 is lost
game_over = 0
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Space Invader YUH YUH')

#load sounds

explosion_fx = pygame.mixer.Sound("explosion.wav")
explosion_fx.set_volume(0.25)

explosion2_fx = pygame.mixer.Sound("Voicy_Bonk.MP3")
explosion2_fx.set_volume(105)

laser_fx = pygame.mixer.Sound("laser.wav")
laser_fx.set_volume(0.25)

nicki1 = pygame.mixer.Sound("Voicy_Nicki Minaj Youre fired.MP3")
nicki1.set_volume(100)

spaceinvader1 = pygame.mixer.Sound("spaceinvaders1.mpeg")
spaceinvader1.set_volume(0.25)

spaceinvader1.play()
#define color
red = (255, 0, 0)
green = (0, 255, 0)
white = (255, 255, 255)
#load background
background = pygame.image.load("space_bg.png")
background_done = pygame.image.load("done_bg.png")
back_win = pygame.image.load("back_win.png")
#define fonts
font30 = pygame.font.SysFont('Constantia', 30)
font40 = pygame.font.SysFont('Constantia', 40)

def draw_background():
    screen.blit(background, (0, 0))

def draw_background_done():
    screen.blit(background_done, (0,0))

def draw_back_win():
    screen.blit(back_win, (0, 0))

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

#create spcaeship class
class Spaceship(pygame.sprite.Sprite):
    def __init__(self, x, y, health):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("spaceship.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.health_start = health
        self.health_remaining = health
        #define the limited bullet
        self.last_shot = pygame.time.get_ticks()

    
    def update(self):
        #set moevment speed
        speed = 8
        #set cooldown time in milliseconds
        cooldown = 400 
        game_over = 0
        #get key press
        #contains all the key that has been pressed
        key = pygame.key.get_pressed()
        #if left k has been pressed
        #limit it to be at the end of both side of screen
        if key[pygame.K_LEFT] and self.rect.left > 0:
            #move left
            self.rect.x -= speed #decrease by 8 each time
        if key[pygame.K_RIGHT] and self.rect.right < screen_width:
            #move to right
            self.rect.x += speed
        #record current time
        #use time stop each bullet at a certain time
        time_now = pygame.time.get_ticks()
        #shooting by tapping a spacebar and if half of the time has passed
        if key[pygame.K_SPACE] and time_now - self.last_shot > cooldown:
                #play the sound everytime it got hit
                laser_fx.play()
                #create a bullet instance
                #set in at center and on top of the spaceship
                bullet = Bullets(self.rect.centerx, self.rect.top)
                bullet_group.add(bullet)
                #restart the timer for the cooldown
                self.last_shot = time_now
        #mask --> ignore anything that is transparent
        self.mask = pygame.mask.from_surface(self.image)
        #draw health bar
        pygame.draw.rect(screen, red, (self.rect.x, (self.rect.bottom + 10), self.rect.width, 10))
        if self.health_remaining > 0:
            pygame.draw.rect(screen, green, (self.rect.x, (self.rect.bottom + 10), int(self.rect.width * (self.health_remaining / self.health_start)), 10))
        
        #once runout of the health
        elif self.health_remaining <= 0:
            explosion = Explosion(self.rect.centerx, self.rect.centery, 3)
            explosion_group.add(explosion)
            self.kill()
            nicki1.play()
            game_over = -1
        return game_over

#create bullet class
class Bullets(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("bullet.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
    
    #move the bullet
    #straight up
    def update(self):
        self.rect.y -= 5
        #dont forget to delete each bullet once hit the top
        if self.rect.bottom < 0:
            self.kill()
        #collision
        #kill the alien
        if pygame.sprite.spritecollide(self, alien_group, True):
            #destroy the bullet 
            self.kill()
            explosion_fx.play()
            explosion = Explosion(self.rect.centerx, self.rect.centery, 2)
            explosion_group.add(explosion)
            

#create Alien class
class Aliens(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("alien" + str(random.randint(1, 4)) + ".png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.move_counter = 0
        self.move_direction = 1

    def update(self):
        #move
        self.rect.x += self.move_direction
        self.move_counter += 1
        if abs(self.move_counter) > 75:
            self.move_direction *= -1
            self.move_counter *= self.move_direction

#create alien bullet class
class Alien_Bullets(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("alien_bullet.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
    
    #move the bullet
    #straight up
    def update(self):
        self.rect.y += 2
        #dont forget to delete each bullet once hit the top
        if self.rect.top > screen_height:
            self.kill()
    #collision
    #set to False since we dont want our spaceship to be wiped away
    #look for pixel collision, no rect. collision
        if pygame.sprite.spritecollide(self, spaceship_group, False, pygame.sprite.collide_mask):
            self.kill()
            explosion2_fx.play()
            #reduce spaceship health
            spaceship.health_remaining -= 1
            #destroy the spaceship
            explosion = Explosion(self.rect.centerx, self.rect.centery, 1)
            explosion_group.add(explosion)

#create an explosion class
class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, size):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(1,6):
            img = pygame.image.load(f"exp{num}.png")
            #scaling the image size
            if size == 1:
                img = pygame.transform.scale(img, (20, 20))
            if size == 2:
                img = pygame.transform.scale(img, (40, 40))
            if size == 3:
                img = pygame.transform.scale(img, (160, 160))
            self.images.append(img)
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        #to control the speed
        self.counter = 0
    
    def update(self):
        explosion_speed = 3
        #update explosionanimation
        self.counter += 1

        if self.counter >= explosion_speed and self.index < len(self.images) - 1:
            self.counter = 0
            self.index += 1
            self.image = self.images[self.index]
        
        #if the animation is completed
        if self.index >= len(self.images) - 1 and self.counter >= explosion_speed:
            self.kill()

    

#create sprite groups
#work as a list
spaceship_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
alien_group = pygame.sprite.Group()
alien_bullets_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
def create_aliens():
    #generate aliens
    for row in range(rows):
        for item in range(cols):
            #how much pixel apart (x,y)
            alien = Aliens(100 + item * 100, 100 + row * 70)
            #once an alien is create
            alien_group.add(alien)

#create aliens
create_aliens()

#create Player
#at the center, and the bottom
spaceship = Spaceship(int(screen_width / 2), screen_height - 100, 5)
spaceship_group.add(spaceship)
sound_end = False


async def main():
    #gameover: 0 is game over, 1 is won, -1 is lost
    game_over = 0
    countdown = 3
    last_count = pygame.time.get_ticks()
    #bullets cooldown in millisecond
    last_alien_shot = pygame.time.get_ticks()
    run = True
    while run:
        clock.tick(fps)
        #draw background
        draw_background()
    
        if countdown == 0:

            #alien randomly shoots
            #record the current time
            time_now = pygame.time.get_ticks()
            #shoot
            #and limited bullets(no more than 5)
            if time_now - last_alien_shot > alien_cooldown and len(alien_bullets_group) < 5 and len(alien_group) > 0:
                #assign an alien
                attacking_alien = random.choice(alien_group.sprites())
                #right under the selected alien
                alien_bullets = Alien_Bullets(attacking_alien.rect.centerx, attacking_alien.rect.bottom)
                alien_bullets_group.add(alien_bullets)
                last_alien_shot = time_now

            #if destroys all aliens
            if len(alien_group) == 0:
                game_over = 1
            
            if game_over == 0:
                #update spaceship
                game_over = spaceship.update()

                #update sprite group
                #Sprite already contain a built-in draw() and update() function
                bullet_group.update()
                alien_group.update()
                alien_bullets_group.update()
            else:
                
                if game_over == -1:  
                    draw_background_done()
                    draw_text('GAME OVER :(', font40, white, int(screen_width / 2 - 350), int(screen_height / 2 + 150))
                elif game_over == 1:
                    draw_back_win()
                    draw_text('YOU WON!!!', font40, white, int(screen_width / 2 - 150), int(screen_height / 2 + 50))

        
        if countdown > 0:
            draw_text('Welcome to Space Invader YUH YUH', font40, white, int(screen_width / 2 - 320), int(screen_height / 2 + 10))
            draw_text('GET READY', font40, white, int(screen_width / 2 - 110), int(screen_height / 2 + 50))
            draw_text(str(countdown), font40, white, int(screen_width / 2 - 10), int(screen_height / 2 + 100))
            

            count_timer = pygame.time.get_ticks()
            if count_timer - last_count > 1000:
                countdown -= 1
                last_count = count_timer
        
        #update explosion group
        explosion_group.update()


        #draw sapceship on the screen
        spaceship_group.draw(screen)
        #draw bullet on the screen
        bullet_group.draw(screen)
        #draw aliens
        alien_group.draw(screen)
        alien_bullets_group.draw(screen)
        explosion_group.draw(screen)


        #event handler
        for event in pygame.event.get():
            #done playing
            if event.type == pygame.QUIT:
                run = False 
        #update background, aliens, etc.
        pygame.display.update()
        await asyncio.sleep(0)
    pygame.quit()
asyncio.run(main())