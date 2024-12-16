
import pygame as pg
from config import WINDOW_SIZE

class Timer:
    def __init__(self, app):
        self.app = app
        # Store the start time for calculating time passed
        self.start_time = pg.time.get_ticks()
        # Load in the font
        self.font = pg.font.Font('sprites/pixel_font.ttf', size=100)
        self.update()

    def update(self):
        # Find the time passed and convert into mins, secs, and decimals
        time = pg.time.get_ticks() - self.start_time
        minutes = (time // 1000) // 60
        seconds = (time // 1000) % 60
        hundredths = (time % 1000) // 10
        text = f'{minutes:02d}:{seconds:02d}:{hundredths:02d}'
        # Update the surface
        self.surf = self.font.render(text, False, (255, 255, 255))
        self.rect = self.surf.get_rect(topright=(1900, 0))

    def render(self):
        # Render the timer
        self.app.screen.blit(self.surf, self.rect)

class Score_Counter:
    def __init__(self, app):
        self.app = app
        # Set starting score
        self.score = 1250
        # Define messages list
        self.messages = []
        # Define font
        self.font = pg.font.Font('sprites/pixel_font.ttf', size=70)
        self.update()

    def update(self):
        # If the player has not beaten the level decrease the score over time
        if self.app.player.flinging == -1:
            self.score -= self.app.dt * 10
        # Create a new text surface and rectangle for the score
        self.text = self.font.render(f'Score:{round(self.score)}', False, (255, 255, 255))
        self.text_rect = self.text.get_rect(midleft=(WINDOW_SIZE.x - 270, 100))
        
        # Delete messages that have decayed
        indexes = []
        for index, message in enumerate(self.messages):
            message.update()
            if message.delete:
                indexes.append(index)
        for index in sorted(indexes, reverse=True):
            self.messages.pop(index)

    def render(self):
        # Render the score counter
        self.app.screen.blit(self.text, self.text_rect)
        # Render the messages
        for message in self.messages:
            message.render()

    def add_score(self, score, message):
        # Add score to the total score
        self.score += score * self.app.player.score_mult
        if message: # Create a message for the score added
            self.messages.append(Score_Message(self.app, score))

    def finish_game(self):
        # Round the final score
        self.score = round(self.score)


class Score_Message:
    def __init__(self, app, score):
        self.app = app
        self.pos = pg.Vector2(WINDOW_SIZE.x - 150, 180)
        # Create a surface and rectangle for the message
        font = pg.font.Font('sprites/pixel_font.ttf', size=60)
        self.surf = font.render(f'+{score} score!', False, (255, 255, 255))
        self.rect = self.surf.get_rect(center=self.pos)
        # Define a timer
        self.life_time = 2
        self.delete = False

    def update(self):
        # Decrease timer and decrease y position
        self.life_time -= self.app.dt
        self.pos.y += self.app.dt * 50
        # If timer has finished, delete message
        if self.life_time <= 0:
            self.delete = True

    def render(self):
        # Render the message after setting new alpha value based off life time
        self.rect.center = self.pos
        self.surf.set_alpha(min(255 * (self.life_time * 5 / 3), 255))
        self.app.screen.blit(self.surf, self.rect)


class Health_Bar:
    def __init__(self, app):
        self.app = app
        self.size = (288, 25)
        # Create surfaces and rects
        self.surf = self.app.sprite_handler.gui_sprites['health_empty']
        self.surf = pg.transform.scale(self.surf, (300, 48))
        self.health_surf_full = self.app.sprite_handler.gui_sprites['health_full']
        self.health_surf_full = pg.transform.scale(self.health_surf_full, (288, 48))
        # Rects
        self.rect = self.surf.get_rect(bottomleft=(50, 970))

        self.update()

    def update(self):
        # Create the red part of the health bar to match the current health
        self.health_surf = pg.Surface((288, 48), flags=pg.SRCALPHA)
        self.health_surf.blit(self.health_surf_full, (0, 0), (0, 0, (self.app.player.health / 20) * self.size[0], 48))
        self.health_rect = self.health_surf.get_rect(bottomleft=(56, 970))

    def render(self):
        # Render the empty health bar then the full health bar
        self.app.screen.blit(self.surf, self.rect)
        self.app.screen.blit(self.health_surf, self.health_rect)

