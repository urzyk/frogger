# -*- coding: utf-8 -*-

import pygame
import random as Random
from pygame.locals import *
from sys import exit
import multiprocessing as mp
import pandas as pd
import filterlib as flt
import blink as blk
#from pyOpenBCI import OpenBCIGanglion


def blinks_detector(quit_program, blink_det, blinks_num, blink,):
    def detect_blinks(sample):
        if SYMULACJA_SYGNALU:
            smp_flted = sample
        else:
            smp = sample.channels_data[0]
            smp_flted = frt.filterIIR(smp, 0)
        #print(smp_flted)

        brt.blink_detect(smp_flted, -38000)
        if brt.new_blink:
            if brt.blinks_num == 1:
                #connected.set()
                print('CONNECTED. Speller starts detecting blinks.')
            else:
                blink_det.put(brt.blinks_num)
                blinks_num.value = brt.blinks_num
                blink.value = 1

        if quit_program.is_set():
            if not SYMULACJA_SYGNALU:
                print('Disconnect signal sent...')
                board.stop_stream()


####################################################
    SYMULACJA_SYGNALU = True
####################################################
    mac_adress = 'd2:b4:11:81:48:ad'
####################################################

    clock = pygame.time.Clock()
    frt = flt.FltRealTime()
    brt = blk.BlinkRealTime()

    if SYMULACJA_SYGNALU:
        df = pd.read_csv('dane_do_symulacji/data.csv')
        for sample in df['signal']:
            if quit_program.is_set():
                break
            detect_blinks(sample)
            clock.tick(200)
        print('KONIEC SYGNAŁU')
        quit_program.set()
    else:
        board = OpenBCIGanglion(mac=mac_adress)
        board.start_stream(detect_blinks)

if __name__ == "__main__":


    blink_det = mp.Queue()
    blink = mp.Value('i', 0)
    blinks_num = mp.Value('i', 0)
    #connected = mp.Event()
    quit_program = mp.Event()

    proc_blink_det = mp.Process(
        name='proc_',
        target=blinks_detector,
        args=(quit_program, blink_det, blinks_num, blink,)
        )

    # rozpoczęcie podprocesu
    proc_blink_det.start()
    print('subprocess started')

    ############################################
    # Poniżej należy dodać rozwinięcie programu
    ############################################

    pygame.init()
    pygame.font.init()
    pygame.mixer.pre_init(44100, 32, 2, 4096)

    font_name = pygame.font.get_default_font()
    game_font = pygame.font.SysFont(font_name, 72)
    info_font = pygame.font.SysFont(font_name, 24)
    menu_font = pygame.font.SysFont(font_name, 36)

    screen = pygame.display.set_mode((448,546), 0, 32)


    background_filename = './images/bg.png'
    frog_filename = './images/sprite_sheets_up.png'
    arrived_filename = './images/frog_arrived.png'
    car1_filename = './images/car1.png'
    car2_filename = './images/car2.png'
    car3_filename = './images/car3.png'
    car4_filename = './images/car4.png'
    car5_filename = './images/car5.png'
    plataform_filename = './images/tronco.png'

    background = pygame.image.load(background_filename).convert()
    sprite_sapo = pygame.image.load(frog_filename).convert_alpha()
    sprite_arrived = pygame.image.load(arrived_filename).convert_alpha()
    sprite_car1 = pygame.image.load(car1_filename).convert_alpha()
    sprite_car2 = pygame.image.load(car2_filename).convert_alpha()
    sprite_car3 = pygame.image.load(car3_filename).convert_alpha()
    sprite_car4 = pygame.image.load(car4_filename).convert_alpha()
    sprite_car5 = pygame.image.load(car5_filename).convert_alpha()
    sprite_plataform = pygame.image.load(plataform_filename).convert_alpha()


    hit_sound = pygame.mixer.Sound('./sounds/boom.wav')
    agua_sound = pygame.mixer.Sound('./sounds/agua.wav')
    chegou_sound = pygame.mixer.Sound('./sounds/success.wav')
    trilha_sound = pygame.mixer.Sound('./sounds/guimo.wav')

    pygame.display.set_caption('Frogger')
    clock = pygame.time.Clock()


    class Object():
        def __init__(self,position,sprite):
            self.sprite = sprite
            self.position = position

        def draw(self):
            screen.blit(self.sprite,(self.position))

        def rect(self):
            return Rect(self.position[0],self.position[1],self.sprite.get_width(),self.sprite.get_height())


    class Frog(Object):
        def __init__(self,position,sprite_sapo):
            self.sprite = sprite_sapo
            self.position = position
            self.lives = 3
            self.animation_counter = 0
            self.animation_tick = 1
            self.way = "UP"
            self.can_move = 1

        def updateSprite(self,key_pressed):
            if self.way != key_pressed:
                self.way = key_pressed
                frog_filename = './images/sprite_sheets_up.png'
                self.sprite = pygame.image.load(frog_filename).convert_alpha()


        def moveFrog(self,key_pressed, key_up):
            if self.animation_counter == 0 :
                self.updateSprite(key_pressed)
            self.incAnimationCounter()
            if self.position[1] > 39:
                self.position[1] = self.position[1]-13


        def animateFrog(self,key_pressed,key_up):
            if self.animation_counter != 0 :
                if self.animation_tick <= 0 :
                    self.moveFrog(key_pressed,key_up)
                    self.animation_tick = 1
                else :
                    self.animation_tick = self.animation_tick - 1

        def setPos(self,position):
            self.position = position

        def decLives(self):
            self.lives = self.lives - 1

        def cannotMove(self):
            self.can_move = 0

        def incAnimationCounter(self):
            self.animation_counter = self.animation_counter + 1
            if self.animation_counter == 3 :
                self.animation_counter = 0
                self.can_move = 1

        def frogDead(self,game):
            self.setPositionToInitialPosition()
            self.decLives()
            game.resetTime()
            self.animation_counter = 0
            self.animation_tick = 1
            self.way = "UP"
            self.can_move = 1

        def setPositionToInitialPosition(self):
            self.position = [207, 475]

        def draw(self):
            current_sprite = self.animation_counter * 30
            screen.blit(self.sprite,(self.position),(0 + current_sprite, 0, 30, 30 + current_sprite))

        def rect(self):
            return Rect(self.position[0],self.position[1],30,30)

    class Enemy(Object):
        def __init__(self,position,sprite_enemy,way,factor):
            self.sprite = sprite_enemy
            self.position = position
            self.way = way
            self.factor = factor

        def move(self,speed):
            if self.way == "right":
                self.position[0] = self.position[0] + speed * self.factor
            elif self.way == "left":
                self.position[0] = self.position[0] - speed * self.factor


    class Plataform(Object):
        def __init__(self,position,sprite_plataform,way):
            self.sprite = sprite_plataform
            self.position = position
            self.way = way

        def move(self,speed):
            if self.way == "right":
                self.position[0] = self.position[0] + speed
            elif self.way == "left":
                self.position[0] = self.position[0] - speed


    class Game():
        def __init__(self,speed,level):
            self.speed = speed
            self.level = level
            self.points = 0
            self.time = 30
            self.gameInit = 0

        def incLevel(self):
            self.level = self.level + 1

        def incSpeed(self):
            self.speed = self.speed + 1

        def incPoints(self,points):
            self.points = self.points + points

        def decTime(self):
            self.time = self.time - 1

        def resetTime(self):
            self.time = 30


    def drawList(list):
        for i in list:
            i.draw()

    def moveList(list,speed):
        for i in list:
            i.move(speed)

    def destroyEnemys(list):
        for i in list:
            if i.position[0] < -80:
                list.remove(i)
            elif i.position[0] > 516:
                list.remove(i)

    def destroyPlataforms(list):
        for i in list:
            if i.position[0] < -100:
                list.remove(i)
            elif i.position[0] > 448:
                list.remove(i)

    def createEnemys(list,enemys,game):
        for i, tick in enumerate(list):
            list[i] = list[i] - 1
            if tick <= 0:
                if i == 0:
                    list[0] = (40*game.speed)/game.level
                    position_init = [-55,436]
                    enemy = Enemy(position_init,sprite_car1,"right",1)
                    enemys.append(enemy)
                elif i == 1:
                    list[1] = (30*game.speed)/game.level
                    position_init = [506, 397]
                    enemy = Enemy(position_init,sprite_car2,"left",2)
                    enemys.append(enemy)
                elif i == 2:
                    list[2] = (40*game.speed)/game.level
                    position_init = [-80, 357]
                    enemy = Enemy(position_init,sprite_car3,"right",2)
                    enemys.append(enemy)
                elif i == 3:
                    list[3] = (30*game.speed)/game.level
                    position_init = [516, 318]
                    enemy = Enemy(position_init,sprite_car4,"left",1)
                    enemys.append(enemy)
                elif i == 4:
                    list[4] = (50*game.speed)/game.level
                    position_init = [-56, 280]
                    enemy = Enemy(position_init,sprite_car5,"right",1)
                    enemys.append(enemy)

    def createPlataform(list,plataforms,game):
        for i, tick in enumerate(list):
            list[i] = list[i] - 1
            if tick <= 0:
                if i == 0:
                    list[0] = (30*game.speed)/game.level
                    position_init = [-100,200]
                    plataform = Plataform(position_init,sprite_plataform,"right")
                    plataforms.append(plataform)
                elif i == 1:
                    list[1] = (30*game.speed)/game.level
                    position_init = [448, 161]
                    plataform = Plataform(position_init,sprite_plataform,"left")
                    plataforms.append(plataform)
                elif i == 2:
                    list[2] = (40*game.speed)/game.level
                    position_init = [-100, 122]
                    plataform = Plataform(position_init,sprite_plataform,"right")
                    plataforms.append(plataform)
                elif i == 3:
                    list[3] = (40*game.speed)/game.level
                    position_init = [448, 83]
                    plataform = Plataform(position_init,sprite_plataform,"left")
                    plataforms.append(plataform)
                elif i == 4:
                    list[4] = (20*game.speed)/game.level
                    position_init = [-100, 44]
                    plataform = Plataform(position_init,sprite_plataform,"right")
                    plataforms.append(plataform)

    def carChangeRoad(enemys):
        enemy = Random.choice(enemys)
        initialPosition = enemy.position[1]

        choice = Random.randint(1,2)
        if (choice % 2 == 0):
            enemy.position[1] = enemy.position[1] + 39
        else :
            enemy.position[1] = enemy.position[1] - 39

        if enemy.position[1] > 436:
            enemy.position[1] = initialPosition
        elif enemy.position[1] < 280:
            enemy.position[1] = initialPosition


    def frogOnTheStreet(frog,enemys,game):
        for i in enemys:
            enemyRect = i.rect()
            frogRect = frog.rect()
            if frogRect.colliderect(enemyRect):
                hit_sound.play()
                frog.frogDead(game)

    def frogInTheLake(frog,plataforms,game):
        seguro = 0
        wayPlataform = ""
        for i in plataforms:
            plataformRect = i.rect()
            frogRect = frog.rect()
            if frogRect.colliderect(plataformRect):
                seguro = 1
                wayPlataform = i.way

        if seguro == 0:
            agua_sound.play()
            frog.frogDead(game)

        elif seguro == 1:
            if wayPlataform == "right":
                frog.position[0] = frog.position[0] + game.speed

            elif wayPlataform == "left":
                frog.position[0] = frog.position[0] - game.speed

    def frogArrived(frog,chegaram,game):
        if frog.position[0] > 33 and frog.position[0] < 53:
            position_init = [43,7]
            createArrived(frog,chegaram,game,position_init)

        elif frog.position[0] > 115 and frog.position[0] < 135:
            position_init = [125,7]
            createArrived(frog,chegaram,game,position_init)

        elif frog.position[0] > 197 and frog.position[0] < 217:
            position_init = [207,7]
            createArrived(frog,chegaram,game,position_init)

        elif frog.position[0] > 279 and frog.position[0] < 299:
            position_init = [289,7]
            createArrived(frog,chegaram,game,position_init)

        elif frog.position[0] > 361 and frog.position[0] < 381:
            position_init = [371,7]
            createArrived(frog,chegaram,game,position_init)

        else:
            frog.position[1] = 46
            frog.animation_counter = 0
            frog.animation_tick = 1
            frog.can_move = 1


    def whereIsTheFrog(frog):
        if frog.position[1] > 240 :
            frogOnTheStreet(frog,enemys,game)

        elif frog.position[1] < 240 and frog.position[1] > 40:
            frogInTheLake(frog,plataforms,game)

        elif frog.position[1] < 40 :
            frogArrived(frog,chegaram,game)


    def createArrived(frog,chegaram,game,position_init):
        sapo_chegou = Object(position_init,sprite_arrived)
        chegaram.append(sapo_chegou)
        chegou_sound.play()
        frog.setPositionToInitialPosition()
        game.incPoints(10 + game.time)
        game.resetTime()
        frog.animation_counter = 0
        frog.animation_tick = 1
        frog.can_move = 1


    def nextLevel(chegaram,enemys,plataforms,frog,game):
        if len(chegaram) == 5:
            chegaram[:] = []
            frog.setPositionToInitialPosition()
            game.incLevel()
            game.incSpeed()
            game.incPoints(100)
            game.resetTime()


    trilha_sound.play(-1)
    text_info = menu_font.render(('Nacisnij dowolny przycisk!'),1,(0,0,0))
    gameInit = 0

    while gameInit == 0:
        for event in pygame.event.get():
            if event.type == QUIT:
                exit()
            if event.type == KEYDOWN:
                gameInit = 1

        screen.blit(background, (0, 0))
        screen.blit(text_info,(80,150))
        pygame.display.update()

    while True:
        gameInit = 1
        game = Game(3,1)
        key_up = 1
        frog_initial_position = [207,475]
        frog = Frog(frog_initial_position,sprite_sapo)

        enemys = []
        plataforms = []
        chegaram = []
        #30 ticks == 1 segundo
        #ticks_enemys = [120, 90, 120, 90, 150]
        #ticks_plataforms = [90, 90, 120, 120, 60]
        ticks_enemys = [30, 0, 30, 0, 60]
        ticks_plataforms = [0, 0, 30, 30, 30]
        ticks_time = 30
        pressed_keys = 0
        key_pressed = 0

        while frog.lives > 0:

            if blink.value == 1:
                frog.moveFrog(key_pressed,key_up)
                blink.value = 0
                print("HOP!")

            for event in pygame.event.get():
                if event.type == QUIT:
                    exit()
                if event.type == KEYUP:
                    key_up = 1
                if event.type == KEYDOWN:
                    if key_up == 1 and frog.can_move == 1 :
                        key_pressed = pygame.key.name(event.key)
                        frog.moveFrog(key_pressed,key_up)
                        frog.cannotMove()
            if not ticks_time:
                ticks_time = 30
                game.decTime()
            else:
                ticks_time -= 1

            if game.time == 0:
                frog.frogDead(game)

            createEnemys(ticks_enemys,enemys,game)
            createPlataform(ticks_plataforms,plataforms,game)

            moveList(enemys,game.speed)
            moveList(plataforms,game.speed)

            whereIsTheFrog(frog)

            nextLevel(chegaram,enemys,plataforms,frog,game)

            text_info1 = info_font.render(('Poziom: {0}               Punkty: {1}'.format(game.level,game.points)),1,(255,255,255))
            text_info2 = info_font.render(('Czas: {0}           Zycia: {1}'.format(game.time,frog.lives)),1,(255,255,255))
            screen.blit(background, (0, 0))
            screen.blit(text_info1,(10,520))
            screen.blit(text_info2,(250,520))

            random = Random.randint(0,100)
            if(random % 100 == 0):
                carChangeRoad(enemys)

            drawList(enemys)
            drawList(plataforms)
            drawList(chegaram)

            frog.animateFrog(key_pressed,key_up)
            frog.draw()

            destroyEnemys(enemys)
            destroyPlataforms(plataforms)

            pygame.display.update()
            time_passed = clock.tick(30)

        while gameInit == 1:
            for event in pygame.event.get():
                if event.type == QUIT:
                    exit()
                if event.type == KEYDOWN:
                    gameInit = 0

            screen.blit(background, (0, 0))
            text = game_font.render('ROZJECHANA!', 1, (255, 0, 0))
            text_points = game_font.render(('Punkty: {0}'.format(game.points)),1,(255,0,0))
            text_reiniciar = info_font.render('Nacisnij przycisk, aby sprobowac ponownie!',1,(255,0,0))
            screen.blit(text, (75, 120))
            screen.blit(text_points,(10,170))
            screen.blit(text_reiniciar,(70,250))

            pygame.display.update()

# Zakończenie podprocesów
    proc_blink_det.join()
