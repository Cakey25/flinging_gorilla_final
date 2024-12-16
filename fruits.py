
import pygame as pg
import random
from config import WINDOW_SIZE
import math

class Fruit:
    def __init__(self, app, pos):
        self.app = app
        self.pos = pos
        # Set a default surface and rect for fruits
        self.surf = pg.Surface((80, 80))
        self.rect = self.surf.get_rect(center=self.pos)
        # Setup other variables
        self.delete = False
        self.y_offset = 0
    
    def update(self):
        # Check for collisions and change y offset
        self.collide()
        self.y_offset = 6 * math.sin(self.app.time / 180)

    def render(self):
        # Calculate render rect based of y offset and render to screen
        render_rect = self.surf.get_rect(center=self.pos - self.app.world_position + WINDOW_SIZE / 2)
        render_rect.y += self.y_offset
        self.app.screen.blit(self.surf, render_rect)

    def collide(self):
        # If the fruit is colliding with the player, mark for deletion
        self.rect.center = self.pos
        if self.rect.colliderect(self.app.player.rect):
            self.effect() # Run effect of the fruit.
            self.delete = True

    def effect(self, score):
        # All fruits have the effect of add 4 the playing health
        self.app.player.health += 4
        # Play sound effect and add to the score
        self.app.sound_handler.player_sounds['eat'].play()
        self.app.score_counter.add_score(score, True)

class Mango(Fruit):
    def __init__(self, app, pos):
        super().__init__(app, pos)
        # Set sprite to mango
        self.surf = self.app.sprite_handler.fruit_sprites['mango']

    def effect(self):
        super().effect(50)
        # Effect of giving the player 3 extra health
        self.app.player.health += 3
        # Create pop up message
        self.app.fruits.append(Message(self.app, pg.Vector2(180, WINDOW_SIZE.y - 150), "+7 Health", True))

class Pineapple(Fruit):
    def __init__(self, app, pos):
        super().__init__(app, pos)
        # Set sprite to pineapple
        self.surf = self.app.sprite_handler.fruit_sprites['pineapple']

    def effect(self):
        super().effect(50)
        # Effect of giving the player increased defense
        self.app.player.defense_mult *= 0.9
        # Create pop up messages
        self.app.fruits.append(Message(self.app, self.pos, "0.9x Damage taken!", False))
        self.app.fruits.append(Message(self.app, pg.Vector2(180, WINDOW_SIZE.y - 150), "+4 Health", True))

class Banana(Fruit):
    def __init__(self, app, pos):
        super().__init__(app, pos)
        # Set sprite to banana
        self.surf = self.app.sprite_handler.fruit_sprites['banana']

    def effect(self):
        super().effect(50)
        # Effect of giving the player increased damage
        self.app.player.damage_mult *= 1.2
        # Create pop up messages
        self.app.fruits.append(Message(self.app, self.pos, "1.2x Damage!", False))
        self.app.fruits.append(Message(self.app, pg.Vector2(180, WINDOW_SIZE.y - 150), "+4 Health", True))

class Melon(Fruit):
    def __init__(self, app, pos):
        super().__init__(app, pos)
        # Set sprite to melon
        self.surf = self.app.sprite_handler.fruit_sprites['melon']

    def effect(self):
        super().effect(50)
        # Effect of giving the player increased score
        self.app.player.score_mult *= 1.2
        # Create pop up messages
        self.app.fruits.append(Message(self.app, self.pos, "1.2x Score multiplier!", False))
        self.app.fruits.append(Message(self.app, pg.Vector2(180, WINDOW_SIZE.y - 150), "+4 Health", True))

class Golden_Melon(Fruit):
    def __init__(self, app, pos):
        super().__init__(app, pos)
        # Set sprite to golden melon
        self.surf = self.app.sprite_handler.fruit_sprites['gold_melon']

    def effect(self):
        # Give the player 1000 score
        super().effect(1000)

class Message:
    def __init__(self, app, pos, message, gui):
        self.pos = pos - pg.Vector2(0, 50)
        self.app = app
        self.gui = gui
        # Create surface and rectangle
        self.font = pg.font.Font('sprites/pixel_font.ttf', size=60)
        self.surf = self.font.render(message, False, (255, 255, 255))
        self.rect = self.surf.get_rect(center=self.pos)
        # Define timers
        self.life_time = 2
        self.delete = False

    def update(self):
        # Decrease timers and y position
        self.life_time -= self.app.dt
        self.pos.y -= self.app.dt * 25
        # Delete the messages if timer finishes
        if self.life_time < 0:
            self.delete = True

    def render(self):
        # If not part of the gui, render at world position
        if not self.gui:
            self.rect.center = self.pos - self.app.world_position + WINDOW_SIZE / 2
        else: # Render at the same point on the screen
            self.rect.center = self.pos
        # Set the alpha of the surface and render
        self.surf.set_alpha(min(255 * (self.life_time * 5 / 3), 255))
        self.app.screen.blit(self.surf, self.rect)

def create_fruit(gold):
    # Return a type of fruit from the list of fruits
    if gold:
        return Golden_Melon
    fruits = [Mango, Pineapple, Banana, Melon]
    new_fruit = random.choice(fruits)
    return new_fruit


    
