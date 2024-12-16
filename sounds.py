
import pygame as pg

class Sound_handler:
    def __init__(self, app):
        pg.mixer.init()
        self.app = app
        self.current_music = None
        # load sounds
        self.load_enemies()
        self.load_gui()
        self.load_player()
        self.set_volume()

    def load_enemies(self):
        # load enemy sounds
        self.enemies_sounds = dict()
        self.enemies_sounds['parrot'] = pg.mixer.Sound('sounds/bird.mp3')
        self.enemies_sounds['parrot_death'] = pg.mixer.Sound('sounds/bird_death.mp3')
        self.enemies_sounds['snake'] = pg.mixer.Sound('sounds/snake.mp3')
        self.enemies_sounds['snake_death'] = pg.mixer.Sound('sounds/snake_death.mp3')
        self.enemies_sounds['spider_walk'] = pg.mixer.Sound('sounds/spider_walk.mp3')
        self.enemies_sounds['spider_spit'] = pg.mixer.Sound('sounds/spider_spit.mp3')
        self.enemies_sounds['spider_death'] = pg.mixer.Sound('sounds/spider_death.mp3')
        self.enemies_sounds['hit'] = pg.mixer.Sound('sounds/enemy_hit.mp3')

    def load_gui(self):
        # load gui sounds
        self.gui_sounds = dict()
        self.gui_sounds['button'] = pg.mixer.Sound('sounds/button_press.mp3')
        self.gui_sounds['level_complete'] = pg.mixer.Sound('sounds/level_complete.mp3')

    def load_player(self):
        # load player souds
        self.player_sounds = dict()
        self.player_sounds['death'] = pg.mixer.Sound('sounds/player_death.mp3')
        self.player_sounds['hit'] = pg.mixer.Sound('sounds/player_hit.mp3')
        self.player_sounds['eat'] = pg.mixer.Sound('sounds/eating.mp3')
        self.player_sounds['grab'] = []
        for i in range(1, 4):
            self.player_sounds['grab'].append(pg.mixer.Sound(f'sounds/player_grab{i}.mp3'))

    def load_music(self, music):
        # If the music is the same as the track playing, continue playing
        if music == self.current_music:
            return
        pg.mixer.music.unload()
        # Load new music
        pg.mixer.music.load(f'sounds/{music}.mp3')
        # -1 to loop the music playback
        pg.mixer.music.play(-1)
        self.current_music = music
        
    def set_volume(self):
        vol = self.app.settings['sound_volume']
        # Enemies
        self.enemies_sounds['parrot'].set_volume(0.25 * vol)
        self.enemies_sounds['parrot_death'].set_volume(0.25 * vol)
        self.enemies_sounds['snake'].set_volume(0.6 * vol)
        self.enemies_sounds['snake_death'].set_volume(0.7 * vol)
        self.enemies_sounds['spider_walk'].set_volume(0.8 * vol)
        self.enemies_sounds['spider_spit'].set_volume(0.3 * vol)
        self.enemies_sounds['spider_death'].set_volume(0.5 * vol)
        self.enemies_sounds['hit'].set_volume(1 * vol)
        # GUI
        self.gui_sounds['button'].set_volume(0.8 * vol)
        self.gui_sounds['level_complete'].set_volume(0.9 * vol)
        # Player
        self.player_sounds['death'].set_volume(0.7 * vol)
        self.player_sounds['hit'].set_volume(0.5 * vol)
        self.player_sounds['eat'].set_volume(0.15 * vol)
        for sound in self.player_sounds['grab']:
            sound.set_volume(0.2 * vol)

        # Music
        vol = self.app.settings['music_volume']
        pg.mixer.music.set_volume(0.5 * vol)
        
    def stop_sounds(self):
        # Stop playing all sounds
        for sound in self.enemies_sounds.values():
            sound.stop()

    def stop_music(self):
        # Stop playing music
        pg.mixer.music.stop()
        pg.mixer.music.unload()

    def pause_sounds(self):
        # Pause sounds
        pg.mixer.pause()

    def unpause_sounds(self):
        # Unpause sounds
        pg.mixer.unpause()


