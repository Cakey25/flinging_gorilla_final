
import pygame as pg
from tile import Tile
from config import WINDOW_SIZE

class Chunk:

    def __init__(self, app, pos, data):
        
        self.app = app
        # Set the position of the chunk
        pos_x, pos_y = tuple(pos.split(';'))
        self.pos = pg.Vector2(int(pos_x), int(pos_y))
        
        # Build the data of the chunk
        self.data = dict()
        for layer in data.keys():
            self.data[layer] = []
            for tile_data in data[layer]:
                self.data[layer].append(Tile(self.app, tile_data))
        
    def render(self):
        # Go throug the layers in order so things at the back are displayed first
        layers = sorted([int(layer) for layer in list(self.data.keys())])
        for layer in layers:
            for tile in self.data[str(layer)]:
                # Culling to only draw things that are on screen
                x, y = tuple(self.app.world_position)
                if x - WINDOW_SIZE.x / 2 - 100 < tile.pos.x < x + WINDOW_SIZE.x / 2 + 100:
                    if y - WINDOW_SIZE.y / 2 - 100 < tile.pos.y < y + WINDOW_SIZE.y / 2 + 100:
                        # Get the sprite and rect of the tile and blit it to screen
                        tile.rect.center = tile.pos - self.app.world_position + WINDOW_SIZE / 2
                        self.app.screen.blit(tile.surf, tile.rect)

        if self.app.level_editor:
            # Iterate over all the possible entity spawn locations
            for entity, positions in self.app.level_handler.entity_locations.items():
                for position in positions:
                    x, y = tuple(position.split(';'))
                    x = int(x)
                    y = int(y)
                    player_x, player_y = tuple(self.app.world_position)
                    # Culling
                    if player_x - WINDOW_SIZE.x / 2 - 100 < x < player_x + WINDOW_SIZE.x / 2 + 100:
                        if player_y - WINDOW_SIZE.y / 2 - 100 < y < player_y + WINDOW_SIZE.y / 2 + 100:
                            # Get the location to render
                            x = x - self.app.world_position.x + WINDOW_SIZE.x / 2
                            y = y - self.app.world_position.y + WINDOW_SIZE.y / 2
                            # Choose colour of circle
                            if entity == '0':
                                colour = (255, 0, 0)
                            elif entity == '1':
                                colour = (0, 255, 0)
                            elif entity == '2':
                                colour = (0, 0, 255)
                            elif entity == '3':
                                colour = (255, 0, 255)
                            else:
                                colour = (255, 255, 255)
                            # Draw circle
                            pg.draw.circle(self.app.screen, colour, (x, y), 25) 
                            
# type: ignore