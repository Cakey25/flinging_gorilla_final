
# Imports
import pygame as pg
import math
import random
# My modules
from config import WINDOW_SIZE, GRAVITY
from config import HAND_SPEED, HAND_DISTANCE_DROPOFF

# Player class
class Player:

    def __init__(self, app) -> None:
        
        self.app = app # Create a pointer to the game class
        self.pos = pg.Vector2(0, 0) # Set the position
        self.vel = pg.Vector2(0, 0)
        
        # Create the player sprite and rectangle
        self.surf_left = app.sprite_handler.gorilla_sprite['gorilla_idle_left']
        self.surf_right = app.sprite_handler.gorilla_sprite['gorilla_idle_right']
        self.rect = self.surf_left.get_rect(center=self.pos)
       
        # Create variables required for the left arm movement
        self.right_offset = pg.Vector2(-30, -92) # The offset posititon of the right hand from the player
        self.right_pos = self.pos - self.right_offset # Position of right hand
        self.right_target = self.pos - self.right_offset # Where the right hand is trying to move to
        self.right_vel = pg.Vector2(0, 0) # The velocity of the right hand
        self.right_state = 'ready' # The state of the right hand
        self.right_time = 0
        # The velocity that the arm is
        # moving the player while attached
        self.push_vel = pg.Vector2(0, 0)
        # Where the player is trying to move to
        self.player_target = pg.Vector2(0, 0)
        # Create variables required for the left arm movement
        self.left_offset = pg.Vector2(30, -92) # The offset posittion of the left hand from the player
        self.left_pos = self.pos - self.left_offset # Position of the left hand
        self.left_target = self.pos - self.left_offset # Where the left hand is trying to move to
        self.left_vel = pg.Vector2(0, 0) # The velocity of the left hand
        self.left_state = 'ready' # The state of the left hand
        self.left_time = 0
        # Health variables
        self.i_frames = 0
        self.health = 20
        # Status variables
        self.direction = 'left'
        self.fallen = -1
        self.flinging = -1
        # Stats variables
        self.score_mult = 1
        self.damage_mult = 1
        self.defense_mult = 1

    def update(self) -> None:
        #self.health = 20
        # If the player has not beaten the level
        if self.flinging == -1:
            self.dt = self.app.dt
        else: # If they have, slow down time
            self.dt = self.app.dt * (self.flinging / 2)
        # If the player has beaten the level
        if self.flinging > 0:
            # Decrease flinging timer and slow down velocity
            self.flinging -= self.app.dt
            self.vel *= 1 - (0.4 * self.dt)
            # Move the hand targets with the player
            self.right_target = self.pos - self.right_offset
            self.left_target = self.pos - self.left_offset
            self.left_thrown()
            self.right_thrown()
            # If the timer has finished, move to level complete screen
            if self.flinging <= 0:
                self.app.level_complete()
            return
        # If the gorilla has fallen from the tree
        if self.fallen > 0:
            # Decrease the timer and velocity
            self.fallen -= self.dt
            self.vel *= 1 - (0.4 * self.dt)
            # Move the hand targets with the player
            self.right_target = self.pos - self.right_offset
            self.left_target = self.pos - self.left_offset
            self.left_thrown()
            self.right_thrown()
            # If the timer has finished, move to level failed screen
            if self.fallen <= 0:
                self.app.level_failed()
            return
        # Set position before movement
        x_before = self.pos.x
        # Air resistance
        self.vel *= 1 - (0.4 * self.dt)

        # Calculate the length of the arm
        self.arm_length = (self.pos - self.right_pos).length()
        
        # Increase time for since mouse buttons have been pressed
        self.left_time += self.dt
        self.right_time += self.dt
        # Reset the timers for the hands
        if self.app.mouse_click[1]:
            self.right_time = 0
        elif self.app.mouse_click[0]:
            self.left_time = 0

        # Check if the right hand has been thrown
        if self.app.mouse_click[1]:
            self.right_pos = self.pos.copy() - self.right_offset
            self.right_state = 'thrown'
        # If the right mouse is still pressed find a right target
        if self.app.mouse_pressed[1] and self.right_time < self.left_time:
            self.right_target = (self.app.mouse_pos - self.app.screen_off + self.app.world_position)
        else:
            self.right_target = (self.pos - self.right_offset).copy()

        # Find how the right hand should move depending on the hand state
        if self.right_state == 'thrown':
            self.right_thrown()
        elif self.right_state == 'attached':
            self.right_attached()
        elif self.right_state == 'ready':
            self.right_ready()

        # Check if the left hand has been thrown
        if self.app.mouse_click[0]:
            self.left_pos = self.pos.copy() - self.left_offset
            self.left_state = 'thrown'
        # If the left mouse is still pressed find a left target
        if self.app.mouse_pressed[0] and self.left_time < self.right_time:
            self.left_target = (self.app.mouse_pos - self.app.screen_off + self.app.world_position)
            # Reset the right arm if using the left arm
            if self.right_state == 'attached':
                self.right_state = 'thrown'
                self.right_target = (self.pos - self.right_offset).copy()
                self.vel = self.right_vel.copy() + self.vel
        else:
            self.left_target = (self.pos - self.left_offset).copy()

        # Find how the left hand should move depending on the hand state
        if self.left_state == 'thrown':
            self.left_thrown()
        elif self.left_state == 'ready':
            self.left_ready()

        # Set the position of the player
        self.rect.center = self.pos
        # Animation
        if self.pos.x - x_before >= 0:
            self.direction = 'right'
        elif self.pos.x - x_before < 0:
            self.direction = 'left'
        # Health
        self.i_frames -= self.app.dt
        if self.i_frames < -2 and self.health < 8:
            self.health += 1 * self.dt

        if self.health <= 0:
            self.app.sound_handler.player_sounds['death'].play()
            self.app.level_failed()

        if self.health > 20:
            self.health = 20
        # Attacking
        self.attack()
        beat = self.beat_level()
        if not beat:
            self.out_of_bounds()

    def right_thrown(self) -> None:
        # Add the force of gravity
        self.vel += pg.Vector2(0, GRAVITY) * self.dt
        # Calculate the velocity of the player's hand
        self.right_vel = self.calc_vel_vector(self.right_pos, self.right_target)

        # Fixed bug that cancels momentum and one that addes momentum
        if self.is_hand_attached() and self.app.mouse_pressed[1] and self.right_time < self.left_time:

            # If the hand is able to attach to a branch, attach it
            self.right_state = 'attached'
            self.player_target = self.pos.copy() # Save where the player should be moved
            # Play the grab sound effect
            self.app.sound_handler.player_sounds['grab'][random.randint(0, 2)].play()
             
        if self.right_pos.distance_to(self.right_target) <= self.right_vel.length():
            # If the hand is very close to its target, set the hand pos to the target
            self.right_pos = self.right_target.copy()
            if self.right_pos == (self.pos - self.right_offset):
                # If the target of the hand was the player position, the hand has returned
                # To the player and can be set to the ready state
                self.right_state = 'ready'
        else:
            # If the hand is not near the target move it closer to the target
            self.right_pos += self.right_vel * 60 * self.dt
            self.right_pos += self.vel * 60 * self.dt
        # Update the player position
        self.pos += self.vel * 60 * self.dt
        # Update the position of the hand if ready so there is no stuttering
        if self.right_state == 'ready':
            self.right_pos = (self.pos - self.right_offset).copy()
        if self.left_state == 'ready':
            self.left_pos = (self.pos - self.left_offset).copy()

    def left_thrown(self) -> None:
        # Calculate the velocity of the player's hand
        self.left_vel = self.calc_vel_vector(self.left_pos, self.left_target)
        
        if self.left_pos.distance_to(self.left_target) <= self.left_vel.length():
            # If the hand is very close to its target, set the hand pos to the target
            self.left_pos = self.left_target.copy()
            if self.left_pos == (self.pos - self.left_offset):

                # If the target of the hand was the player position, the hand has returned
                # To the player and can be set to the ready state
                self.left_state = 'ready'
        else:
            # If the hand is not near the target move it closer to the target
            self.left_pos += self.left_vel * 60 * self.dt
            self.left_pos += self.vel * 60 * self.dt
        # Update the position of the hand if ready so there is no stuttering
        if self.left_state == 'ready':
            self.left_pos = (self.pos - self.left_offset).copy()

    def right_attached(self) -> None:
        # Find the new player target depending on the mouse velocity
        self.player_target -= self.app.mouse_vel
        # Calculate the velocity of the hand relative to the player
        self.right_vel = self.calc_vel_vector(self.pos, self.player_target)
        self.pos += self.right_vel * 60 * self.dt
        # Find a value between 0.1 and 0 depending on the length of the arm
        # will be 0.1 when at 1000 length or more and 0 when length is 0
        arm_speed_mult = self.arm_length / 10_000 if self.arm_length <= 1_000 else 0.1
        # changes how the arm reacts depending on the length
        self.vel *= 0.91 + (arm_speed_mult * 60 * self.dt)

        # If the velocity of the player is too low, set it to 0
        if self.vel.length() < 1.0:
            self.vel = pg.Vector2(0, 0)
        self.pos += self.vel * 60 * self.dt# Add the velocity

        # If the player position is close to the target then set the position to target
        if self.pos.distance_to(self.player_target) <= self.right_vel.length():
            self.pos = self.player_target.copy()

        # If the player stops pressing down the mouse button, change the hand state
        if not self.app.mouse_pressed[1]:
            self.right_state = 'thrown'
            self.vel = self.right_vel.copy() + self.vel

    def right_ready(self) -> None:
        # This is for when the hand is not thrown out at all
        # Change the velocity of the player and add it to position
        self.vel += pg.Vector2(0, GRAVITY) * self.dt
        self.pos += self.vel * self.dt * 60
        self.right_pos = self.pos.copy() - self.right_offset

    def left_ready(self) -> None:
        # This is for when the hand is not thrown out at all
        # Change the velocity of the player and add it to position
        self.left_pos = self.pos.copy() - self.left_offset

    def calc_vel_vector(self, origin, desination) -> pg.Vector2:
        # Define velocity
        vel = pg.Vector2(0, 0)
    
        # Calculate displacement and distance from origin to desination
        displacement_to_target = (desination - origin)
        distance_to_target = displacement_to_target.length()
           
        # Change the distance to target to a value between 0 and 1
        # From a range of 0 to 500
        if distance_to_target != 0:
            if distance_to_target >= HAND_DISTANCE_DROPOFF:
                distance_to_target = 1
            else:
                distance_to_target /= HAND_DISTANCE_DROPOFF
            # Set the velocity to the unit vector of displacement
            vel = displacement_to_target.normalize()
            # Calculate some multipliers for finding the resulting velocity
            # Uses a scaled cos graph for distance multiplier
            dist_mult = math.cos((1 - distance_to_target) * 1.5)
            # Uses a scaled cubic graph for speed multiplier
            speed_mult = (1 - math.pow((1 - distance_to_target) / 2, 3))
            # Calculate the final velocity
            vel *= HAND_SPEED * dist_mult * speed_mult / 60

        return vel

    def is_hand_attached(self) -> bool:
        # The hand must be with in the range of 150 pixel to the target to attach
        if self.right_pos.distance_to(self.right_target) >= 150:
            return False
        # The hand must be further that 75 pixels away from the body to attach
        if self.right_pos.distance_to(self.pos - self.right_offset) <= 75:
            return False
        # This will be the collision check against branches
        if self.tree_collision():
            return False
    
        return True

    def tree_collision(self) -> bool:
        # Finds all the chunk positions in and around the player hand
        chunk_positions = [
            pg.Vector2(0, 0),
            pg.Vector2(-1, 0), pg.Vector2(1, 0),
            pg.Vector2(0, 1), pg.Vector2(0, -1)]
        right_pos = self.right_pos // 640
        chunk_positions = [(chunk_pos + right_pos) for chunk_pos in chunk_positions]
        # Iterates over the found chunk positions
        for chunk in chunk_positions:
            check_pos = f'{int(chunk.x)};{int(chunk.y)}'
            if check_pos in self.app.level_handler.data:
                for tile in self.app.level_handler.data[check_pos].data['0']:
                    # layer 0 is where all the trees will be
                    tile_pos = pg.Vector2(tile.pos)
                    # Checks distance between hand and tile to see if colliding
                    if self.right_pos.distance_to(tile_pos) <= 50 * tile.size:
                        return False
        return True

    def attack(self):
        # Iterate all the enemies in the level and check if the player is hitting them
        for enemy in self.app.enemies:
            if enemy.collide_point(self.left_pos):
                # Deal damage to the enemy and check if they are dead
                enemy.damage((self.left_vel + self.vel).length() * self.dt * 6 * self.damage_mult)
                enemy.death()

    def damage(self, damage):
        # If the player has not got i-frames
        if self.i_frames < 0:
            # Reset i-frames timer
            self.i_frames = 0.5
            # Deal damage to the player and play a sound
            self.health -= damage * self.defense_mult
            self.app.sound_handler.player_sounds['hit'].play()

    def beat_level(self):
        # If the player is at the top of the level
        if self.pos.y < self.app.level_handler.level_rect.top:
            if self.app.level_handler.level_rect.left < self.pos.x < self.app.level_handler.level_rect.right:
                # Start the flinging timer and play a sound
                self.flinging = 2
                self.app.sound_handler.gui_sounds['level_complete'].play()
                return True
        return False

    def out_of_bounds(self):
        # If the player is out of bounds
        if not self.app.level_handler.level_rect.collidepoint(self.pos) and not self.app.level_editor:
            # Start a timer and save the last position
            self.world_position = self.pos.copy()
            self.fallen = 2
            # Play a sound effect
            self.app.sound_handler.player_sounds['death'].play()

    def render(self) -> None:
        # Body
        render_rect = pg.Rect(0, 0, self.rect.width, self.rect.height)
        render_rect.center = (self.pos + self.app.screen_off - self.app.world_position)
        if self.direction == 'left':
            self.app.screen.blit(self.surf_left, render_rect)
        elif self.direction == 'right':
            self.app.screen.blit(self.surf_right, render_rect)
        # Right arm --------------------------------------------------------------

        # Calculate the angle that the hand is pointing away from
        right_angle = math.atan2(self.pos.y - self.right_pos.y, (self.pos.x - self.right_offset.x) - self.right_pos.x)
        # Player arm
        # Calculate arm length
        right_arm_length = (self.pos - pg.Vector2(self.right_offset.x, 0)).distance_to(self.right_pos)
        # Scale and rotate the player arm
        self.right_arm = pg.transform.scale(self.app.sprite_handler.gorilla_sprite['gorilla_arm_0'],
                                            (self.app.sprite_handler.gorilla_sprite['gorilla_arm_0'].get_width(),
                                             right_arm_length))
        self.right_arm = pg.transform.rotate(self.right_arm, -math.degrees(right_angle) + 90)
        right_arm_pos = ((self.pos - pg.Vector2(self.right_offset.x, 2)) + self.right_pos) / 2
        self.right_arm_rect = self.right_arm.get_rect(
            center=right_arm_pos + self.app.screen_off - self.app.world_position)
        self.app.screen.blit(self.right_arm, self.right_arm_rect)
        # Hand
        # Rotate the hand sprite
        self.right_hand_rotated = pg.transform.rotate(self.app.sprite_handler.gorilla_sprite['gorilla_hand_right'],
                                                      -math.degrees(right_angle) + 90)
        self.right_hand_rect = self.right_hand_rotated.get_rect( # Create a new rectangle around the new sprite
            center=self.right_pos + self.app.screen_off - self.app.world_position)
        # Render the hand to the screen
        self.app.screen.blit(self.right_hand_rotated, self.right_hand_rect)

        # Left arm --------------------------------------------------------------

        # Calculate the angle that the hand is pointing away from
        left_angle = math.atan2(self.pos.y - self.left_pos.y, (self.pos.x - self.left_offset.x) - self.left_pos.x)
        # Player arm
        # Calculate arm length
        left_arm_length = (self.pos - pg.Vector2(self.left_offset.x, 2)).distance_to(self.left_pos)
        # Scale and rotate the player arm
        self.left_arm = pg.transform.scale(self.app.sprite_handler.gorilla_sprite['gorilla_arm_0'],
                                           (self.app.sprite_handler.gorilla_sprite['gorilla_arm_0'].get_width(),
                                            left_arm_length))
        self.left_arm = pg.transform.rotate(self.left_arm, -math.degrees(left_angle) + 90)
        left_arm_pos = ((self.pos - pg.Vector2(self.left_offset.x, 0)) + self.left_pos) / 2
        self.left_arm_rect = self.left_arm.get_rect(
            center=left_arm_pos + self.app.screen_off - self.app.world_position)
        self.app.screen.blit(self.left_arm, self.left_arm_rect)
        # Hand
        # Rotate the hand sprite
        self.left_hand_rotated = pg.transform.rotate(self.app.sprite_handler.gorilla_sprite['gorilla_hand_left'],
                                                     -math.degrees(left_angle) + 90)
        self.left_hand_rect = self.left_hand_rotated.get_rect( # Create a new rectangle around the new sprite
            center=self.left_pos + self.app.screen_off - self.app.world_position)
        # Render the hand to the screen
        self.app.screen.blit(self.left_hand_rotated, self.left_hand_rect)

        if self.flinging > 0:
            surf = self.app.sprite_handler.background_sprites['level_complete_menu']
            surf.set_alpha(255 * (1 - self.flinging))
            self.app.screen.blit(surf, (0, 0))

        
