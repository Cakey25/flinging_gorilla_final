
import pygame as pg


class Button:

    def __init__(self, app, name, pos, function) -> None:
        self.app = app
        self.pos = pos

        # Create button text
        font = pg.font.Font('sprites/pixel_font.ttf', size=50)
        self.text = font.render(name, False, (255, 255, 255))
        # Find button width from text width
        self.width = max(self.text.get_width() + 20, 200)
        # Create button surface
        self.surf = self.app.sprite_handler.gui_sprites['button']
        self.surf = pg.transform.scale(self.surf, (self.width, 50))
        # Create dark overlay surface
        self.dark = pg.Surface((self.width, 50), flags=pg.SRCALPHA)
        self.dark.fill((200, 200, 200, 255))
        # Create rectangle for button
        self.rect = self.surf.get_rect(center=pos)
        # Defining what the button should do
        self.activation = function

    def update(self) -> None:
        # Check if the button has been clicked
        if self.rect.collidepoint(self.app.mouse_pos) and self.app.mouse_rise[0]:
            # Play sound effect and activate button
            self.app.sound_handler.gui_sounds['button'].play()
            self.activation()
    
    def render(self) -> None:
        # If the button is being hovered over, darken the button
        if self.rect.collidepoint(self.app.mouse_pos) and self.app.mouse_pressed[0]:
            self.text_rect = self.text.get_rect(center=(self.width / 2, 25))
            # Create empty surface for button
            surf = pg.Surface((self.width, 50), flags=pg.SRCALPHA)
            # Put the button surface, text and dark overlay on the surface
            surf.blit(self.surf, (0, 0))
            surf.blit(self.text, self.text_rect)
            surf.blit(self.dark, (0, 0), special_flags=pg.BLEND_MULT)
            # Render the final button
            self.app.screen.blit(surf, self.rect)
        else:
            # Render button without darken effect
            self.text_rect = self.text.get_rect(center=self.pos)
            self.app.screen.blit(self.surf, self.rect)
            self.app.screen.blit(self.text, self.text_rect)

class Slider:

    def __init__(self, app, surf, pos, setting, slide_range, name) -> None:
        self.app = app
        self.pos = pos
        # Define the size of the slider
        self.size = (200, 50)
        # Create text for the slider
        font = pg.font.Font('sprites/pixel_font.ttf', size=60)
        self.text = font.render(name, False, (30, 30, 30))
        self.text_rect = self.text.get_rect(midright=self.pos - pg.Vector2(150, 0))
        # Create surfaces and rects
        self.surf = pg.Surface(self.size, flags=pg.SRCALPHA)
        surf = pg.transform.scale(self.app.sprite_handler.gui_sprites['slider'], self.size)
        self.surf.blit(surf, (0, 0))
        self.pointer = pg.Surface((20, 70), flags=pg.SRCALPHA)
        surf = pg.transform.scale(self.app.sprite_handler.gui_sprites['pointer'], (20, 70))
        self.pointer.blit(surf, (0, 0))
        # Rects
        self.rect = self.surf.get_rect(center=pos)
        self.pointer_rect = self.pointer.get_rect(center=pos)
        # What setting the button should change
        self.setting = setting
        self.slide_range = slide_range
        self.held = False
        # Update before first frame
        self.update()

    def update(self) -> None:
        # Find where the pointer of the slider should be displaying
        min_val, max_val = self.slide_range
        x_fraction = (self.app.settings[self.setting] - min_val) / (max_val - min_val)
        self.pointer_rect.centerx = self.rect.left + (self.size[0] * x_fraction)
        # Check if the mouse has clicked on the slider
        if self.app.mouse_click[0] and self.pointer_rect.collidepoint(self.app.mouse_pos):
            # Keep track of the relative position of the mouse
            self.original_x = self.app.mouse_pos.x - self.pointer_rect.centerx
            self.held = True
        # If the slider is begin moved
        if self.held:
            self.pointer_rect.centerx = self.app.mouse_pos.x - self.original_x
            # Range check to stop the slider from moving too far
            if self.pointer_rect.centerx > self.rect.right:
                self.pointer_rect.centerx = self.rect.right
            if self.pointer_rect.centerx < self.rect.left:
                self.pointer_rect.centerx = self.rect.left
        # Check if the mouse has stopping clicking
        if self.app.mouse_rise[0]:
            self.held = False
            if self.pointer_rect.collidepoint(self.app.mouse_pos):
                self.app.sound_handler.gui_sounds['button'].play()
        # Calculate what value the setting should be
        x_fraction = (self.pointer_rect.centerx - self.rect.left) / self.rect.width
        self.app.settings[self.setting] = min_val + (max_val - min_val) * x_fraction
        # Create the dark fill on the left side of the pointer
        self.dark = pg.Surface(self.size, pg.SRCALPHA)
        self.dark.fill((200, 200, 200, 255))
        self.dark = pg.transform.scale(self.dark, (self.pointer_rect.centerx - self.rect.left, self.size[1]))
        self.dark_rect = self.dark.get_rect(midleft=self.rect.midleft)

    def render(self) -> None:
        # Render the slider
        surf = self.surf.__copy__()
        surf.blit(self.dark, (0, 0), special_flags=pg.BLEND_MULT)
        self.app.screen.blit(surf, self.rect)
        self.app.screen.blit(self.pointer, self.pointer_rect)
        self.app.screen.blit(self.text, self.text_rect)


