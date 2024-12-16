
# Imports
import pygame as pg

class Sprite_handler:

    def __init__(self):
        # Load sprites
        self.load_tiles()
        self.load_gorilla()
        self.load_enemies()
        self.load_fruits()
        self.load_gui()
        self.load_background()

    def load_tiles(self):
        self.tile_sprites = dict()
        
        # Load in the tiles
        tile_0 = pg.image.load('sprites/tile0.png').convert_alpha()
        self.tile_sprites['tile_0'] = (pg.transform.scale_by(tile_0, 4), 'big leaves')
        tile_1 = pg.image.load('sprites/tile1.png').convert_alpha()
        self.tile_sprites['tile_1'] = (pg.transform.scale_by(tile_1, 4), 'tree trunk')
        tile_2 = pg.image.load('sprites/tile2.png').convert_alpha()
        self.tile_sprites['tile_2'] = (pg.transform.scale_by(tile_2, 4), 'flower leaves')
        tile_3 = pg.image.load('sprites/tile3.png').convert_alpha()
        self.tile_sprites['tile_3'] = (pg.transform.scale_by(tile_3, 4), 'vines')
        tile_4 = pg.image.load('sprites/tile4.png').convert_alpha()
        self.tile_sprites['tile_4'] = (pg.transform.scale_by(tile_4, 4), 'small leaf')
        tile_5 = pg.image.load('sprites/tile5.png').convert_alpha()
        self.tile_sprites['tile_5'] = (pg.transform.scale_by(tile_5, 4), 'small flower')
        tile_6 = pg.image.load('sprites/tile6.png').convert_alpha()
        self.tile_sprites['tile_6'] = (pg.transform.scale_by(tile_6, 4), 'moss')

    def load_gorilla(self):
        self.gorilla_sprite = dict()
        
        # Load in the base sprites
        arm = pg.image.load('sprites/gorilla_arm_0.png').convert_alpha()
        hand = pg.image.load('sprites/gorilla_hand_0.png').convert_alpha()
        hand = pg.transform.scale_by(hand, 6)
        body_idle = pg.image.load('sprites/gorilla_idle_0.png').convert_alpha()
        body_idle = pg.transform.scale_by(body_idle, 6)

        # Create and properly resize the player sprites
        self.gorilla_sprite['gorilla_idle_left'] = body_idle
        self.gorilla_sprite['gorilla_idle_right'] = pg.transform.flip(body_idle, True, False)
        self.gorilla_sprite['gorilla_hand_left'] = hand
        self.gorilla_sprite['gorilla_hand_right'] = pg.transform.flip(hand, True, False)
        player_arm_base = pg.Surface((5, 12), pg.SRCALPHA)
        player_arm_base.blit(arm, (0, 0), (5, 3, 5, 12))
        self.gorilla_sprite['gorilla_arm_0'] = pg.transform.scale_by(player_arm_base, 6)

    def load_enemies(self):
        # Parrot
        self.parrot_sprites = dict()
        self.parrot_sprites['moving_right'] = []
        self.parrot_sprites['moving_left'] = []
        for i in range(1, 5):
            image = pg.image.load(f'sprites/Parrot{i}.png').convert_alpha()
            image = pg.transform.scale_by(image, 5)
            self.parrot_sprites['moving_right'].append(image)
            image = pg.transform.flip(image, True, False)
            self.parrot_sprites['moving_left'].append(image)
        # Spider
        self.spider_sprites = dict()
        idle = pg.image.load('sprites/spider_idle.png').convert_alpha()
        self.spider_sprites['idle'] = pg.transform.scale_by(idle, 5)
        self.spider_sprites['walking'] = []
        for i in range(1, 5):
            image = pg.image.load(f'sprites/spider{i}.png').convert_alpha()
            image = pg.transform.scale_by(image, 5)
            self.spider_sprites['walking'].append(image)
        dead = pg.image.load('sprites/spider_dead.png').convert_alpha()
        self.spider_sprites['dead'] = pg.transform.scale_by(dead, 5)
        # Web
        web = pg.image.load('sprites/SpiderWeb.png').convert_alpha()
        self.spider_sprites['web'] = pg.transform.scale_by(web, 6)
        spit = pg.image.load('sprites/Spiderspit.png').convert_alpha()
        self.spider_sprites['spit'] = pg.transform.scale_by(spit, 4)
        # Snake
        self.snake_sprites = dict()
        self.snake_sprites['moving_left'] = []
        self.snake_sprites['moving_right'] = []
        for i in range(1, 4):
            image = pg.image.load(f'sprites/Snake{i}.png').convert_alpha()
            image = pg.transform.scale_by(image, 5)
            self.snake_sprites['moving_right'].append(image)
            image = pg.transform.flip(image, True, False)
            self.snake_sprites['moving_left'].append(image)
        coil = pg.image.load('sprites/Snakecoil.png').convert_alpha()
        self.snake_sprites['coil'] = pg.transform.scale_by(coil, 5)
        head = pg.image.load('sprites/Snakehead.png').convert_alpha()
        head = pg.transform.rotate(head, 90)
        self.snake_sprites['head'] = pg.transform.scale_by(head, 5)
        body = pg.image.load('sprites/Snakebody.png').convert_alpha()
        body = pg.transform.rotate(body, 90)
        self.snake_sprites['body'] = pg.transform.scale_by(body, 3.2)
        dead = pg.image.load('sprites/Snake_dead.png').convert_alpha()
        self.snake_sprites['dead'] = pg.transform.scale_by(dead, 5)

    def load_fruits(self):
        # Load all fruit sprites
        self.fruit_sprites = dict()
        self.fruit_sprites['melon'] = pg.transform.scale_by(
            pg.image.load('sprites/Melon.png').convert_alpha(), 5)
        self.fruit_sprites['mango'] = pg.transform.scale_by(
            pg.image.load('sprites/Mango.png').convert_alpha(), 5)
        self.fruit_sprites['banana'] = pg.transform.scale_by(
            pg.image.load('sprites/Banana.png').convert_alpha(), 5)
        self.fruit_sprites['pineapple'] = pg.transform.scale_by(
            pg.image.load('sprites/Pineapple.png').convert_alpha(), 5)
        self.fruit_sprites['gold_melon'] = pg.transform.scale_by(
            pg.image.load('sprites/Golden_Melon.png').convert_alpha(), 5)

    def load_gui(self):
        # Load health bar
        self.gui_sprites = dict()
        full_health = pg.image.load('sprites/HealthbarFill.png').convert_alpha()
        self.gui_sprites['health_full'] = full_health
        empty_bar = pg.image.load('sprites/HealthbarOutline.png').convert_alpha()
        self.gui_sprites['health_empty'] = empty_bar
        # Load button and slider sprites
        self.gui_sprites['button'] = pg.image.load('sprites/ButtonBase.png').convert_alpha()
        self.gui_sprites['slider'] = pg.image.load('sprites/SliderBase.png').convert_alpha()
        self.gui_sprites['pointer'] = pg.image.load('sprites/SliderPointer.png').convert_alpha()

    def load_background(self):
        # Load background sprites
        self.background_sprites = dict()
        image = pg.image.load('sprites/Background1.png').convert_alpha()
        self.background_sprites['main_menu'] = pg.transform.scale_by(image, 6)
        image = pg.image.load('sprites/Background2.png').convert_alpha()
        self.background_sprites['settings_menu'] = pg.transform.scale_by(image, 6)
        image = pg.image.load('sprites/Background3.png').convert_alpha()
        self.background_sprites['level_complete_menu'] = pg.transform.scale_by(image, 6)
        image = pg.image.load('sprites/Background4.png').convert_alpha()
        self.background_sprites['level_failed_menu'] = pg.transform.scale_by(image, 6)

    
