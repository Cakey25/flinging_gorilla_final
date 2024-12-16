
import pygame as pg
import random
import math
from config import WINDOW_SIZE

class Parrot:
    def __init__(self, app, pos):
        self.app = app
        # Define positions
        self.pos = pos
        self.target = pos
        # Setup surfaces and rects
        self.surf = self.app.sprite_handler.parrot_sprites['moving_right'][0]
        self.rect = pg.Rect(0, 0, 80, 50)
        self.rect.center = self.pos
        # Keep track of idle time
        self.idle = 0
        # Health and damage variables
        self.i_frames = 0
        self.health = 8
        # Status of enemy variables
        self.dead = False
        self.delete = False
        # Animation variables
        self.frame = 0
        self.direction = 'right'
        # Sound variables
        self.sound_timer = 3 + (random.random() * 5)

    def update(self):
        if self.dead: # If enemy has died
            # Decay and move down enemy
            self.decay -= self.app.dt
            self.y_offset += 30 * self.app.dt
            # Delete enemy if fully decayed
            if self.decay <= 0:
                self.delete = True
            return
        
        # Decrease timers
        self.sound_timer -= self.app.dt
        self.idle -= self.app.dt
        self.i_frames -= self.app.dt
        # Get distance to player
        player_pos = self.app.player.pos
        distance_player = player_pos.distance_to(self.pos)
        # Check if the player is nearby
        if distance_player < 800:
            # Set a target to player
            self.target = player_pos.copy()
            self.sounds()
        else:
            # Find a random point to fly towards
            if self.target.distance_to(self.pos) <= 20: # Set a bounding box of sides of the level
                target = pg.Vector2(random.randint(-1200, 1200), random.randint(-1200, 1200))
                target_pos = target + self.pos
                if target.distance_to(pg.Vector2(0, 0)) <= 1200:
                    if self.app.level_handler.level_rect.collidepoint(target_pos):
                        self.target = target + self.pos
                    else:
                        self.target = target
                self.idle = random.random() + 1
        # Find a new target and stop jittering around player
        if self.idle < 0:
            if self.target != self.pos:
                vel = (self.target - self.pos).normalize() * 320
                # Set the direction of the parrot
                if vel.x > 0:
                    self.direction = 'right'
                elif vel.x < 0:
                    self.direction = 'left'
            else:
                vel = pg.Vector2(0, 0)
            # Move the parrot towards target
            if self.target.distance_to(self.pos) <= vel.length() * self.app.dt:
                self.pos = self.target
            else:
                self.pos += vel * self.app.dt
        # Update rect
        self.rect.center = self.pos
        # Animate and attack
        self.animate()
        self.attack()

    def animate(self):
        self.frame += self.app.dt
        # 0.6 is total time for animation loop
        # 4 is the number of frames
        # Calculate frame of animation
        if self.frame > 0.6:
            self.frame = 0
        index = math.floor(4 * self.frame / 0.6)
        # Use the correct sprite depending on the direction
        if self.direction == 'right':
            self.surf = self.app.sprite_handler.parrot_sprites['moving_right'][index]
        elif self.direction == 'left':
            self.surf = self.app.sprite_handler.parrot_sprites['moving_left'][index]

    def render(self):
        if self.dead: # Death animation
            # Calculate new render rect
            render_rect = self.surf.get_rect(center=self.pos - self.app.world_position + WINDOW_SIZE / 2)
            render_rect.y += self.y_offset
            # Set alpha value of surface for fade out
            self.surf.set_alpha(255 * (self.decay / 2))
            # Render parrot
            self.app.screen.blit(self.surf, render_rect)
            return
        # Render parrot
        rect = self.surf.get_rect(center=self.pos - self.app.world_position + WINDOW_SIZE / 2)
        self.app.screen.blit(self.surf, rect)

    def attack(self):
        # Deal damage to player if colliding with them
        if self.rect.colliderect(self.app.player.rect):
            self.app.player.damage(3)

    def damage(self, damage):
        # Take damage from player if parrot has not i-frames
        if self.i_frames < 0:
            self.health -= damage
            # Reset i-frames timer
            self.i_frames = 0.5
            # Play sound effect
            self.app.sound_handler.enemies_sounds['hit'].play()

    def death(self):
        # Check if the player is dead
        if self.health <= 0 and not self.dead:
            self.dead = True
            # Set the direction of sprite for death animation
            if self.direction == 'right':
                self.surf = self.app.sprite_handler.parrot_sprites['moving_right'][2]
            elif self.direction == 'left':
                self.surf = self.app.sprite_handler.parrot_sprites['moving_left'][2]
            # Create surface
            self.surf = pg.transform.rotate(self.surf, 180)
            # Set death animation variables
            self.decay = 2
            self.y_offset = 0
            # Add score for the player and play sound effect
            self.app.score_counter.add_score(300, True)
            self.app.sound_handler.enemies_sounds['parrot_death'].play()

    def collide_point(self, point):
        # Method that checks if player hand is colliding with parrot
        # Create a rectangle and move it to hand position
        hand_rect = pg.Rect(0, 0, 100, 100)
        hand_rect.center = point.copy()
        self.rect.center = self.pos
        # Check if hand and parrot are colliding
        if hand_rect.colliderect(self.rect):
            return True
        return False

    def sounds(self):
        # Play sound if the sound timer has finished
        if self.sound_timer <= 0:
            # Reset the sound timer and play sound effect
            self.sound_timer = 3 + (random.random() * 5)
            self.app.sound_handler.enemies_sounds['parrot'].play()

class Snake:
    def __init__(self, app, pos):
        self.app = app
        self.pos = pos
        # Setup surfaces and rect
        self.surf = self.app.sprite_handler.snake_sprites['moving_right'][0]
        self.rect = pg.Rect(0, 0, 40, 90)
        self.rect.center = self.pos
        # Keep track of idle and move time
        self.idle = 0
        self.move_time = 0
        # Variable for attacking
        self.attacking = False
        self.length = 0
        # Create variables for health
        self.i_frames = 0
        self.health = 12
        # Variables for the status of the snake
        self.dead = False
        self.delete = False
        # Variables for animation
        self.frame = 0
        self.direction_x = 'right'
        # Variables for sound effects
        self.sound_timer = 2 + (random.random() * 6)
        # Variables for direction and distance to player
        diff = self.app.player.pos - self.pos
        self.direction = math.atan2(diff.y, diff.x)

    def update(self):
        # If the snake has died
        if self.dead:
            # Decrease decay timer and move rect down
            self.decay -= self.app.dt
            self.y_offset += 30 * self.app.dt
            # Delete snake if decayed
            if self.decay <= 0:
                self.delete = True
            return
        # Decrease timers
        self.attacking = False
        self.sound_timer -= self.app.dt
        self.idle -= self.app.dt
        self.i_frames -= self.app.dt
        self.move_time -= self.app.dt
        # Check if the player is nearby
        player_pos = self.app.player.pos
        distance_player = player_pos.distance_to(self.pos)
        if distance_player < 300:
            # If player is nearby, extend length
            if self.length < 275:
                self.length += 600 * self.app.dt
                if self.length > 275:
                    self.length = 275
        # Descrease the length if the player is not nearby
        elif self.length > 0:
            self.length -= 600 * self.app.dt
            if self.length < 0:
                self.length = 0
        if distance_player < 650 and self.length <= 0:
            # Get the direction to the player
            self.diff_x = self.app.player.pos.x - self.pos.x
            self.idle = -1
            self.move_time = 1
        elif self.length <= 0:
            if self.move_time < 0:
                # Pick a random direction to move
                self.move_time = random.random() * 5
                self.idle = random.random() + 0.5
                self.diff_x = random.choice([-100, 100])
        # Find a position for the snake
        if self.move_time > 0 and self.idle < 0 and not self.attacking and distance_player > 350:
            if self.diff_x != 0:
                # Create a new possible position
                self.new_pos = pg.Vector2(self.pos.x + (self.diff_x / abs(self.diff_x)) * 150 * self.app.dt, self.pos.y)
                # Check if that position is near a branch
                if self.tree_collision() and self.app.level_handler.level_rect.collidepoint(self.new_pos):
                    # Find a velocity to move near the target
                    vel = pg.Vector2(0, 0)
                    if self.diff_x != 0:
                        vel.x = (self.diff_x / abs(self.diff_x)) * 150 * self.app.dt
                    if abs(self.diff_x) < (75 * self.app.dt):
                        vel.x = 0
                    if (self.target_y - self.pos.y) != 0:
                        vel.y = 20 * self.app.dt * (self.target_y - self.pos.y) / abs(self.target_y - self.pos.y)
                    # Update position
                    self.pos += vel
                    if vel.x >= 0:
                        self.direction_x = 'right'
                    elif vel.y < 0:
                        self.direction_x = 'left'
        # Update rect
        self.rect.center = self.pos
        # Attack and sounds
        if self.length > 0:
            self.attacking = True
            self.attack()
            self.sounds()
        else:
            # Calculate variables if snake attacks player next frame
            self.diff = self.app.player.pos - self.pos
            self.direction = math.degrees(math.atan2(self.diff.y, self.diff.x))
        # Animate
        self.animate()

    def animate(self):
        # Calcualte the new frame to display
        self.frame += self.app.dt
        if self.frame > 0.6:
            self.frame = 0
        index = math.floor(3 * self.frame / 0.6)
        # Only animate if not attacking
        if not self.attacking:
            # Pick a direction to display
            if self.direction_x == 'right':
                self.surf = self.app.sprite_handler.snake_sprites['moving_right'][index]
            elif self.direction_x == 'left':
                self.surf = self.app.sprite_handler.snake_sprites['moving_left'][index]

    def sounds(self):
        # If sound timer has finished, play new sound and reset timer
        if self.sound_timer <= 0:
            self.sound_timer = 2 + (random.random() * 6)
            self.app.sound_handler.enemies_sounds['snake'].play()

    def tree_collision(self):
        # Finds all the chunk positions in and around the snake position
        chunk_positions = [
            pg.Vector2(0, 0),
            pg.Vector2(-1, 0), pg.Vector2(1, 0),
            pg.Vector2(0, 1), pg.Vector2(0, -1)]
        new_pos = self.new_pos // 640
        chunk_positions = [(chunk_pos + new_pos) for chunk_pos in chunk_positions]
        # Iterates over the found chunk positions
        for chunk in chunk_positions:
            check_pos = f'{int(chunk.x)};{int(chunk.y)}'
            if check_pos in self.app.level_handler.data:
                for tile in self.app.level_handler.data[check_pos].data['0']:
                    # layer 0 is where all the trees will be
                    tile_pos = pg.Vector2(tile.pos)
                    # Checks distance between pos and tile to see if colliding yeag
                    if self.new_pos.distance_to(tile_pos) <= 50 * tile.size:
                        self.target_y = tile_pos.y
                        return True
        return False

    def attack(self):
        
        diff_current = self.app.player.pos - self.pos # Get vector towards player
        dir = math.radians(self.direction - 90) # Change direction to work with dot product
        diff_rot = pg.Vector2(math.cos(dir), math.sin(dir)) # Get vector of current direction
        dot = diff_rot.dot(diff_current) # Calculate the dot product
        # Correct rotation when facing player
        correct_rot = math.degrees(math.atan2(diff_current.y, diff_current.x))
        # If close to correct rotation, set direction to correct
        if abs(self.direction - correct_rot) < 75 * self.app.dt:
            self.direction = correct_rot
        elif dot > 0: # Rotate left
            self.direction -= 75 * self.app.dt
        elif dot < 0: # Rotate right
            self.direction += 75 * self.app.dt
        # Calaculate the direction in radians and find new head position
        dir = math.radians(self.direction)
        self.head_pos = self.pos + (pg.Vector2(math.cos(dir), math.sin(dir)) * self.length)

        # Damage to player
        if self.app.player.rect.clipline(self.pos, self.head_pos):
            self.app.player.damage(5)

    def render(self):
        # Render snake
        if self.dead: # If the snake is dead
            # Calculate new rectangle
            render_rect = self.surf.get_rect(center=self.pos - self.app.world_position + WINDOW_SIZE / 2)
            render_rect.y += self.y_offset
            # Fade out the surface alpha and render
            self.surf.set_alpha(255 * (self.decay / 2))
            self.app.screen.blit(self.surf, render_rect)
            return
        if self.attacking:
            coil_pos = (self.pos - self.app.world_position + WINDOW_SIZE / 2)
            head_pos = (self.head_pos - self.app.world_position + WINDOW_SIZE / 2)
            # Coil
            coil_surf = self.app.sprite_handler.snake_sprites['coil']
            coil_rect = coil_surf.get_rect(center=coil_pos)
            # Body
            coil_offset = pg.Vector2(math.cos(math.radians(self.direction)),
                                     math.sin(math.radians(self.direction))) * 25
            body_center = (head_pos + coil_pos - coil_offset) * 0.5
            body_surf = self.app.sprite_handler.snake_sprites['body']
            body_surf = pg.transform.scale(body_surf, (coil_pos.distance_to(head_pos), body_surf.get_height()))
            body_surf = pg.transform.rotate(body_surf, -self.direction)
            body_rect = body_surf.get_rect(center=body_center)
            # Head
            head_surf = pg.transform.rotate(self.app.sprite_handler.snake_sprites['head'], -self.direction)
            head_rect = head_surf.get_rect(center=head_pos)
            # Render
            self.app.screen.blit(body_surf, body_rect)
            self.app.screen.blit(coil_surf, coil_rect)
            self.app.screen.blit(head_surf, head_rect)

        else:
            # Calculate new rectangle
            render_rect = self.surf.get_rect(center=self.pos - self.app.world_position + WINDOW_SIZE / 2)
            render_rect.y -= 20
            # Choose direction
            if self.direction == 'right':
                render_rect.x -= 20
            elif self.direction == 'left':
                render_rect.x += 20
            # Render snake
            self.app.screen.blit(self.surf, render_rect)

    def damage(self, damage):
        # If the snake has no i-frames, take damage
        if self.i_frames < 0:
            self.health -= damage
            self.i_frames = 0.5
            self.app.sound_handler.enemies_sounds['hit'].play()

    def death(self):
        # Check if the snake is dead
        if self.health <= 0 and not self.dead:
            self.dead = True
            # Set sprite for death animation
            self.surf = self.app.sprite_handler.snake_sprites['dead']
            # Start decay timer and y offset
            self.decay = 2
            self.y_offset = 0
            # Add score and play sound
            self.app.score_counter.add_score(350, True)
            self.app.sound_handler.enemies_sounds['snake_death'].play()

    def collide_point(self, point):
        # Get position of the player hand
        hand_rect = pg.Rect(0, 0, 100, 100)
        hand_rect.center = point.copy()
        # If snake is attacking, use a line collision
        if self.attacking:
            if hand_rect.clipline(self.head_pos, self.pos):
                return True
        else: # Otherwise, use a rectangle collision
            self.rect.center = self.pos
            if hand_rect.colliderect(self.rect):
                return True
        return False


class Spider:
    def __init__(self, app, pos):
        self.app = app
        self.pos = pos
        # Setup surfaces and rects
        self.surf = self.app.sprite_handler.spider_sprites['idle']
        self.rect = pg.Rect(0, 0, 80, 80)
        self.rect.center = self.pos
        # Setup web surface and rect
        self.web_pos = pos.copy()
        self.web_surface = self.app.sprite_handler.spider_sprites['web']
        self.web_surface = pg.transform.rotate(self.web_surface, random.randint(0, 360))
        self.web_rect = self.web_surface.get_rect(center=pos.copy())
        # Keep track of idle time
        self.idle = 1
        # List for all projectiles
        self.projectiles = []
        # Cool down timer
        self.cool_down = 0.5
        # Status of the spider
        self.dead = False
        self.delete = False
        # Health variables
        self.health = 20
        self.i_frames = 0
        self.direction = 0
        # Animation variables
        self.frame = 0
        self.walking = False
        # Sound variables
        self.sound_timer = random.random()

    def update(self):
        if self.dead: # If the spider is dead
            # Decrease decay timer and move sprite down.
            self.decay -= self.app.dt
            self.y_offset += 30 * self.app.dt
            # If decay timer is finished, delete spider
            if self.decay <= 0:
                self.delete = True
            return
        self.web_size = 150
        # Decrease timers
        self.sound_timer -= self.app.dt
        self.idle -= self.app.dt
        self.i_frames -= self.app.dt
        self.cool_down -= self.app.dt
        # Get distance to player
        player_pos = self.app.player.pos
        distance_player = player_pos.distance_to(self.pos)
        # Check if the player is nearby
        if distance_player < 700: # If player is nearby, attack
            self.walking = False
            self.attack()
        elif self.idle < 0:
            self.walking = True
            self.sounds()
            # Move towards the target
            if self.target != self.pos:
                self.vel = (self.target - self.pos).normalize() * 80 * self.app.dt
                self.direction = math.atan2(-self.vel.y, -self.vel.x)
            else:
                self.vel = pg.Vector2(0, 0)
            if self.target.distance_to(self.pos) <= self.vel.length():
                self.pos = self.target
            if self.target != self.pos:
                self.pos += self.vel
            else:
                self.idle = random.random() + 1.5
        # When the spider is idle
        if self.idle > 0:
            self.walking = False
            # Find a random target
            self.target = pg.Vector2(random.randint(-self.web_size, self.web_size),
                                     random.randint(-self.web_size, self.web_size))
            if self.target.distance_to(pg.Vector2(0, 0)) > self.web_size:
                self.target = self.pos.copy()
            else:
                self.target += self.web_pos
        # Update position
        self.rect.center = self.pos
        self.animate()
        # Update projectiles
        for projectile in self.projectiles:
            projectile.update()
        # Delete projectiles
        indices = []
        for index, projectile in enumerate(self.projectiles):
            if projectile.delete():
                indices.append(index)
        for index in sorted(indices, reverse=True):
            self.projectiles.pop(index)

    def animate(self):
        self.frame += self.app.dt
        # 0.6 is total time for animation loop
        # 4 is the number of frames
        # Calculate new frame for animation
        if self.frame > 0.4:
            self.frame = 0
        index = math.floor(4 * self.frame / 0.4)
        # If the spider is walking, player then animation
        if self.walking:
            surf = self.app.sprite_handler.spider_sprites['walking'][index]
            self.surf = pg.transform.rotate(surf, math.degrees(-self.direction) + 90)
        else: # Otherwise, face away from the player
            surf = self.app.sprite_handler.spider_sprites['idle']
            self.surf = pg.transform.rotate(surf, math.degrees(-self.direction) + 90)

    def sounds(self):
        # If the sound timer has finished, play sound
        if self.sound_timer <= 0 and self.pos.distance_to(self.app.player.pos) <= 1000:
            # Reset sound timer and play sound
            self.sound_timer = 1
            self.app.sound_handler.enemies_sounds['spider_walk'].play()

    def render(self):
        # Render web as circle and spider as surface
        if self.dead:
            # Calculate new render rectangle
            render_rect = self.surf.get_rect(center=self.pos - self.app.world_position + WINDOW_SIZE / 2)
            render_rect.y += self.y_offset
            # Set new surface alpha
            self.surf.set_alpha(255 * (self.decay / 2))
            # Set surface alpha of the web
            self.web_rect.center = self.web_pos - self.app.world_position + WINDOW_SIZE / 2
            self.web_surface.set_alpha(255 * (self.decay / 2))
            # Render the spider and the web
            self.app.screen.blit(self.web_surface, self.web_rect)
            self.app.screen.blit(self.surf, render_rect)
            return
        # Calculate new render rectangle
        render_rect = self.surf.get_rect(center=self.pos - self.app.world_position + WINDOW_SIZE / 2)
        self.web_rect.center = self.web_pos - self.app.world_position + WINDOW_SIZE / 2
        # Render the spider and its web
        self.app.screen.blit(self.web_surface, self.web_rect)
        self.app.screen.blit(self.surf, render_rect)
        # Render Projectiles
        for projectile in self.projectiles:
            projectile.render()

    def attack(self):
        # Calculate the difference to the player's position and direction to them
        diff = self.app.player.pos - self.pos
        self.direction = math.atan2(diff.y, diff.x)
        # If the cool down timer has finished
        if self.cool_down < 0:
            # Create a new projectile facing towards the player and play a sound effect
            self.projectiles.append(Projectile(self.app, self.pos, self.direction))
            self.app.sound_handler.enemies_sounds['spider_spit'].play()
            self.cool_down = 1.25 # Reset cool down

    def damage(self, damage):
        # If the spider still has i-frames
        if self.i_frames < 0:
            self.health -= damage
            # Reset i-frames timer and play sound
            self.i_frames = 0.5
            self.app.sound_handler.enemies_sounds['hit'].play()

    def death(self):
        # Check if the spider has reached 0 health
        if self.health <= 0 and not self.dead:
            self.dead = True
            # Set surface for death animation
            self.surf = self.app.sprite_handler.spider_sprites['dead']
            # Start decay timer and set y offset
            self.decay = 2
            self.y_offset = 0
            # Add score and play sound effect
            self.app.score_counter.add_score(400, True)
            self.app.sound_handler.enemies_sounds['spider_death'].play()

    def collide_point(self, point):
        hand_rect = pg.Rect(0, 0, 100, 100)
        hand_rect.center = point.copy()
        self.rect.center = self.pos
        if hand_rect.colliderect(self.rect):
            return True
        return False

class Projectile:
    
    def __init__(self, app, pos, direction):
        self.pos = pos.copy()
        self.app = app
        self.vel = pg.Vector2(math.cos(direction), math.sin(direction)) * 600
        # Surfaces and rects
        surf = self.app.sprite_handler.spider_sprites['spit']
        self.surf = pg.transform.rotate(surf, -math.degrees(direction))
        self.rect = pg.Rect(0, 0, 45, 45)
        self.rect.center = self.pos
        # Whether the player has been hit by this Projectile
        self.hit = False

    def update(self):
        # Move projectile
        self.pos += self.vel * self.app.dt
        self.rect.center = self.pos
        # Deal damage to the player
        if self.app.player.rect.colliderect(self.rect):
            self.app.player.damage(4)
            self.hit = True

    def render(self):
        # Render projectile
        render_rect = self.surf.get_rect(center=self.pos - self.app.world_position + WINDOW_SIZE / 2)
        self.app.screen.blit(self.surf, render_rect)

    def delete(self):
        # Check if the projectile has hit the player
        if self.hit:
            return True
        # If the projectile is out of bounds and offscreen, delete the projectile
        if not self.app.level_handler.level_rect.collidepoint(self.pos):
            if self.app.player.pos.distance_to(self.pos) > 1200:
                return True

