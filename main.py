
# Imports
import pygame as pg
import sys
import time
import json
import random
# My modules
from config import WINDOW_SIZE, TARGET_FPS
from player import Player
from level import Level_handler
from sprites import Sprite_handler
from button import Button, Slider
from gui import Timer, Health_Bar, Score_Counter
from enemies import Parrot, Spider, Snake
from fruits import create_fruit
from sounds import Sound_handler

# Game class
class FlingingGorilla:

    def __init__(self) -> None:
        
        # Initialize modules and window
        pg.init()

        self.screen = pg.display.set_mode(WINDOW_SIZE, display=0)
        self.clock = pg.time.Clock()
        
        # Set the game to running
        self.running = True
        self.dt = 0.0
        # Import settings
        with open('settings.json', 'r') as file:
            self.settings = json.load(file)
        # Load handling objects
        self.sprite_handler = Sprite_handler()
        self.sound_handler = Sound_handler(self)
        self.level_handler = Level_handler(self)

        self.level_editor = False
        self.game_state = 'main_menu'
        self.font = pg.font.Font('sprites/pixel_font.ttf', size=120)
        # Brightness screen
        self.white_screen = pg.Surface(WINDOW_SIZE, flags=pg.SRCALPHA)
        self.white_screen.fill((255, 255, 255))
        self.black_screen = pg.Surface(WINDOW_SIZE, flags=pg.SRCALPHA)
        self.black_screen.fill((0, 0, 0))

    def restart_input(self) -> None:
        # Create the mouse input for continous presses
        self.mouse_pressed = [False] * 5
        self.old_mouse_pos = pg.mouse.get_pos()
        self.sound_handler.stop_sounds()

    def new_scene(self) -> None:
        self.restart_input()
        
        self.sound_handler.load_music('level_music')

        self.game_state = 'in_game'
        # Setup vectors to calculate where objects render
        self.screen_off = pg.Vector2(WINDOW_SIZE[0] / 2, WINDOW_SIZE[1] / 2)
        self.world_position = pg.Vector2(0, 0)
        # Create the objects
        self.player = Player(self)
        self.world_position = self.player.pos.copy()
        self.level_handler.load_level('level_1')
        self.timer = Timer(self)
        self.score_counter = Score_Counter(self)
        self.health_bar = Health_Bar(self)
        self.enemies = []
        self.fruits = []

        self.spawn_entities(1, 1, 1, 2)

    def spawn_entities(self, parrots, snakes, spiders, fruits):
        # Parrot
        if '0' in self.level_handler.entity_locations:
            locations = random.sample(self.level_handler.entity_locations['0'], parrots)
            for location in locations:
                x, y = tuple(location.split(';'))
                self.enemies.append(Parrot(self, pg.Vector2(int(x), int(y))))
        # Snake
        if '1' in self.level_handler.entity_locations:
            locations = random.sample(self.level_handler.entity_locations['1'], snakes)
            for location in locations:
                x, y = tuple(location.split(';'))
                self.enemies.append(Snake(self, pg.Vector2(int(x), int(y))))
        # Spiders
        if '2' in self.level_handler.entity_locations:
            locations = random.sample(self.level_handler.entity_locations['2'], spiders)
            for location in locations:
                x, y = tuple(location.split(';'))
                self.enemies.append(Spider(self, pg.Vector2(int(x), int(y))))
        # Fruits
        if '3' in self.level_handler.entity_locations:
            locations = random.sample(self.level_handler.entity_locations['3'], fruits)
            last = locations.pop(-1)
            for location in locations:
                x, y = tuple(location.split(';'))
                self.fruits.append(create_fruit(False)(self, pg.Vector2(int(x), int(y))))
            x, y = tuple(last.split(';'))
            self.fruits.append(create_fruit(True)(self, pg.Vector2(int(x), int(y))))
                
    def main_menu(self) -> None:
        self.restart_input()
        self.sound_handler.load_music('main_menu')
        # Main menu objects
        self.game_state = 'main_menu'
        self.start_button = Button(self, 'Start Game', WINDOW_SIZE / 2, self.new_scene)
        self.exit_button = Button(self, 'Exit Game', (960, 700), self.game_close)
        self.settings_button = Button(self, 'Settings', (960, 620), self.settings_menu)

    def settings_menu(self) -> None:
        self.restart_input()
        # Settings menu objects
        self.game_state = 'settings'
        self.back_button = Button(self, 'Back', (960, 780), self.main_menu)
        # Sliders
        self.music_slider = Slider(
            self, (240, 20, 230), (960, 480), 'music_volume', (0, 1), 'Music volume')
        self.sound_slider = Slider(
            self, (240, 240, 5), (960, 580), 'sound_volume', (0, 1), 'Sound volume')
        self.brightness_slider = Slider(
            self, (50, 240, 30), (960, 680), 'brightness', (0.5, 1.5), 'Screen brightness')

    def level_complete(self) -> None:
        self.restart_input()

        self.game_state = 'complete'
        self.score_counter.finish_game()
        self.play_again_button = Button(self, 'Play again?', (960, 800), self.new_scene)
        self.main_menu_button = Button(self, 'Main menu', (960, 880), self.main_menu)

    def level_failed(self) -> None:
        self.restart_input()

        self.game_state = 'failed'
        self.restart_button = Button(self, 'Restart Game', (960, 780), self.new_scene)

    def game_close(self) -> None:
        self.running = False
        # Save settings
        with open('settings.json', 'w') as file:
            json.dump(self.settings, file)

    def events(self) -> None:
        self.time = pg.time.get_ticks()
        self.mouse_click = [False] * 5
        self.mouse_rise = [False] * 5
        # Get all events in the last frame
        for event in pg.event.get():
            if event.type == pg.QUIT:
                # Set running to false if the window close button was pressed
                self.running = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE and self.game_state == 'in_game':
                    self.main_menu()
                if self.level_editor:
                    if event.key == pg.K_l:
                        self.level_handler.selected_layer += 1
                    elif event.key == pg.K_p:
                        self.level_handler.selected_layer -= 1
                    elif event.key == pg.K_t:
                        self.level_handler.selected_tile += 1
                    elif event.key == pg.K_g:
                        self.level_handler.selected_tile -= 1
                    elif event.key == pg.K_r:
                        self.level_handler.selected_entity += 1
                    elif event.key == pg.K_f:
                        self.level_handler.selected_entity -= 1
                    elif event.key == pg.K_z:
                        bounds = {'left': -1000, 'right': 2000, 'up': -1000, 'down': 1000}
                        self.level_handler.save_level('level_1', bounds)
                    elif event.key == pg.K_c:
                        self.level_handler.add_entities = self.level_handler.add_entities ^ True
                    elif event.key == pg.K_x:
                        self.level_handler.add_tiles = self.level_handler.add_tiles ^ True
            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == pg.BUTTON_RIGHT:
                    # Checking if the right mouse button has been pressed
                    self.mouse_click[1] = True
                    self.mouse_pressed[1] = True
                if event.button == pg.BUTTON_LEFT:
                    self.mouse_click[0] = True
                    self.mouse_pressed[0] = True
            if event.type == pg.MOUSEBUTTONUP:
                if event.button == pg.BUTTON_RIGHT:
                    # Checking if the right mouse button has been released
                    self.mouse_pressed[1] = False
                    self.mouse_rise[1] = True
                if event.button == pg.BUTTON_LEFT:
                    self.mouse_pressed[0] = False
                    self.mouse_rise[0] = True

        # Get the current mouse input
        self.mouse_pos = pg.Vector2(pg.mouse.get_pos())
        self.mouse_vel = pg.Vector2(self.mouse_pos - self.old_mouse_pos)
        self.old_mouse_pos = self.mouse_pos.copy()
        # Get a dictionary of all the keys currently pressed
        self.keys = pg.key.get_pressed()

    def update(self) -> None:
        self.sound_handler.set_volume()
        if self.game_state == 'in_game':
            # Update objects
            self.player.update()
            # Change the world position
            if self.player.fallen < 0:
                self.world_position = self.player.pos.copy()
            self.timer.update()
            if self.level_editor:
                self.level_handler.editor()
            # Delete dead enemies
            indexes = []
            for index, enemy in enumerate(self.enemies):
                if enemy.delete:
                    indexes.append(index)
            indexes = sorted(indexes, reverse=True)
            for index in indexes:
                self.enemies.pop(index)
            for enemy in self.enemies:
                enemy.update()
            # Fruits
            indexes = []
            for index, fruit in enumerate(self.fruits):
                if fruit.delete:
                    indexes.append(index)
            indexes = sorted(indexes, reverse=True)
            for index in indexes:
                self.fruits.pop(index)
            for fruit in self.fruits:
                fruit.update()

            self.health_bar.update()
            self.score_counter.update()

        elif self.game_state == 'main_menu':
            self.start_button.update()
            self.exit_button.update()
            self.settings_button.update()

        elif self.game_state == 'settings':
            self.back_button.update()
            self.music_slider.update()
            self.sound_slider.update()
            self.brightness_slider.update()

        elif self.game_state == 'failed':
            self.restart_button.update()

        elif self.game_state == 'complete':
            self.play_again_button.update()
            self.main_menu_button.update()

    def render(self) -> None:
        if self.game_state == 'in_game':
            # Fill the screen
            self.screen.fill((10, 170, 255)) # Cyan
            # Render objects
            self.level_handler.render()
            for fruit in self.fruits:
                fruit.render()

            for enemy in self.enemies:
                enemy.render()
            self.player.render()
            self.timer.render()
            self.health_bar.render()
            self.score_counter.render()

        elif self.game_state == 'main_menu':
            # Fill the screen
            self.screen.blit(self.sprite_handler.background_sprites['main_menu'], (0, 0))
            # Render buttons
            self.start_button.render()
            self.exit_button.render()
            self.settings_button.render()
            # Render title
            title = self.font.render('FLINGING', False, (160, 160, 160))
            title_back = self.font.render('FLINGING', False, (60, 60, 60))
            rect = title.get_rect(center=WINDOW_SIZE / 2 - pg.Vector2(0, 250))
            rect.center += pg.Vector2(3, 3)
            self.screen.blit(title, rect)
            rect.center -= pg.Vector2(6, 6)
            self.screen.blit(title_back, rect)
            title = self.font.render('GORILLA', False, (160, 160, 160))
            title_back = self.font.render('GORILLA', False, (60, 60, 60))
            rect = title.get_rect(center=WINDOW_SIZE / 2 - pg.Vector2(0, 180))
            rect.center += pg.Vector2(3, 3)
            self.screen.blit(title, rect)
            rect.center -= pg.Vector2(6, 6)
            self.screen.blit(title_back, rect)
        
        elif self.game_state == 'settings':
            # Render background
            self.screen.blit(self.sprite_handler.background_sprites['settings_menu'], (0, 0))
            # Render buttons and sliders
            self.back_button.render()
            self.music_slider.render()
            self.sound_slider.render()
            self.brightness_slider.render()
            # Render title
            title = self.font.render('SETTINGS', False, (255, 255, 255))
            title_back = self.font.render('SETTINGS', False, (60, 60, 60))
            rect = title.get_rect(center=WINDOW_SIZE / 2 - pg.Vector2(0, 180))
            rect.center += pg.Vector2(3, 3)
            self.screen.blit(title, rect)
            rect.center -= pg.Vector2(6, 6)
            self.screen.blit(title_back, rect)

        elif self.game_state == 'failed':
            # Render background
            self.screen.blit(self.sprite_handler.background_sprites['level_failed_menu'], (0, 0))
            # Render button
            self.restart_button.render()
            # Render title
            font = pg.font.Font('sprites/pixel_font.ttf', size=200)
            text = font.render('FAILED', False, (220, 20, 60))
            rect = text.get_rect(center=WINDOW_SIZE / 2 - pg.Vector2(0, 200))
            self.screen.blit(text, rect)

        elif self.game_state == 'complete':
            # Render background
            self.screen.blit(self.sprite_handler.background_sprites['level_complete_menu'], (0, 0))
            # Render buttons
            self.play_again_button.render()
            self.main_menu_button.render()
            # Render title
            font = pg.font.Font('sprites/pixel_font.ttf', size=200)
            text = font.render('LEVEL COMPLETED', False, (30, 30, 30))
            rect = text.get_rect(center=WINDOW_SIZE / 2 - pg.Vector2(0, 200))
            self.screen.blit(text, rect)
            font = pg.font.Font('sprites/pixel_font.ttf', size=100)
            text = font.render(f'Score:{self.score_counter.score}', False, (30, 30, 30))
            rect = text.get_rect(center=WINDOW_SIZE / 2)
            self.screen.blit(text, rect)


        # Apply the brightness settings
        if self.settings['brightness'] > 1:
            self.white_screen.set_alpha(128 * (self.settings['brightness'] - 1))
            self.screen.blit(self.white_screen, (0, 0))
        if self.settings['brightness'] < 1:
            self.black_screen.set_alpha(128 * (1 - self.settings['brightness']))
            self.screen.blit(self.black_screen, (0, 0))
        
        # Update the window
        pg.display.set_caption(f'{self.clock.get_fps() :.0f}')
        pg.display.flip()
        

if __name__ == '__main__':

    # Initialize the game
    game = FlingingGorilla()
    game.main_menu()
    # Start the game loop
    while game.running:
        
        game.events()
        game.update()
        game.dt = game.clock.tick(TARGET_FPS) / 1_000
        game.render()

    # Quit the game
    pg.quit()
    sys.exit()


