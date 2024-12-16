
import json
import pygame as pg
from chunk import Chunk # type: ignore
from config import WINDOW_SIZE
from tile import Tile

class Level_handler:

    def __init__(self, app):
        # Create pointer to the FlingingGorilla class
        self.app = app
        # Declare some variables
        self.current_level = None
        self.data = None
        self.entity_locations = dict()
        # Selected tile settings
        self.selected_rotation = 0
        self.selected_size = 1
        self.add_tiles = True
        self.selected_tile = 0
        self.selected_layer = 0
        self.add_entities = False
        self.selected_entity = 0

    def load_level(self, name):
        self.current_level = name
        # Level file will be called level_1.json and level_2.json
        with open(f'levels/{name}.json', 'r') as file:
            # Will read all the data from a file with a name matching the one passed in
            raw_data = json.load(file)
            self.entity_locations = raw_data['entity_locations']
            self.level_bounds = raw_data['bounds']
        self.level_rect = pg.Rect(
            self.level_bounds['left'],
            self.level_bounds['up'],
            self.level_bounds['right'] - self.level_bounds['left'],
            self.level_bounds['down'] - self.level_bounds['up'])

        # raw_data is a dictionary of chunks that each have list of tiles in them
        self.data = dict()
        for chunk, chunk_data in raw_data['level'].items():
            # Will create a chunk object for each chunk in the level data
            self.data[chunk] = Chunk(self.app, chunk, chunk_data)

    def save_level(self, name, bounds):
        # Iterate over the level and save data to a dictionary
        level = dict()
        for chunk_pos, chunk in self.data.items():
            level[chunk_pos] = dict()
            for layer, tile_list in chunk.data.items():
                level[chunk_pos][layer] = []
                for tile in tile_list:
                    tile_pos = f'{int(tile.pos.x)};{int(tile.pos.y)}'
                    tile_data = [tile_pos, tile.tile_type, tile.rotation, tile.size]
                    level[chunk_pos][layer].append(tile_data)
        # Write data to a json file
        level_whole = {'level': level, 'entity_locations': self.entity_locations, 'bounds': bounds}
        with open(f'levels/{name}.json', 'w') as file:
            print('hello')
            json.dump(level_whole, file)

    def render(self):
        self.render_background()
        # Iterate over all the chunks in the level
        for position, chunk in self.data.items():
            x, y = position.split(';')
            x = int(x) * 640
            y = int(y) * 640
            player_x, player_y = tuple(self.app.world_position)
            # Cull the chunks so chunks offscreen are not rendered
            if player_x - WINDOW_SIZE.x / 2 - 750 < x < player_x + WINDOW_SIZE.x / 2 + 110:
                if player_y - WINDOW_SIZE.y / 2 - 750 < y < player_y + WINDOW_SIZE.y / 2 + 110:
                    chunk.render()

        if self.app.level_editor:
            # Calculate the corners for the level bounds
            up = self.level_bounds['up']
            left = self.level_bounds['left']
            down = self.level_bounds['down']
            right = self.level_bounds['right']
            top_left = pg.Vector2(left, up) - self.app.world_position + WINDOW_SIZE / 2
            top_right = pg.Vector2(right, up) - self.app.world_position + WINDOW_SIZE / 2
            bottom_left = pg.Vector2(left, down) - self.app.world_position + WINDOW_SIZE / 2
            bottom_right = pg.Vector2(right, down) - self.app.world_position + WINDOW_SIZE / 2
            points = [top_left, top_right, bottom_right, bottom_left]
            # Render the level bounds
            pg.draw.lines(self.app.screen, (255, 0, 0), True, points, 2)

    def editor(self):
        # Input
        if self.app.keys[pg.K_q]:
            self.selected_rotation += 1 * 60 * self.app.dt
        if self.app.keys[pg.K_e]:
            self.selected_rotation -= 1 * 60 * self.app.dt
        if self.app.keys[pg.K_w]:
            self.selected_size += 0.01 * 60 * self.app.dt
        if self.app.keys[pg.K_s]:
            self.selected_size -= 0.01 * 60 * self.app.dt
            
        # Print current level creation settings
        if self.app.keys[pg.K_o]:
            print(f'---\nrotation: {self.selected_rotation}')
            print(f'size: {self.selected_size}')
            print(f'tile: {self.selected_tile}')
            print(f'layer: {self.selected_layer}')
            print(f'entity: {self.selected_entity}')
            print(f'add tiles?: {self.add_tiles}')
            print(f'add entities?: {self.add_entities}')
        
        # Choose what mode to edit the level
        if self.add_entities:
            self.place_entities()
        else:
            self.place_tiles()

    def place_tiles(self):
        # If the mouse has been clicked and you want to create tiles
        if self.app.mouse_click[0] and self.add_tiles and -1 < self.selected_tile < 7:
            # Find where to put new tile
            mouse_pos = self.app.mouse_pos + self.app.player.pos - WINDOW_SIZE / 2
            chunk_pos = f'{int(mouse_pos.x // 640)};{int(mouse_pos.y // 640)}'
            if chunk_pos not in self.data:
                self.data[chunk_pos] = Chunk(self.app, chunk_pos, dict())
            # Get the data from the cunk that the tile is in
            current_data = self.data[chunk_pos].data
            tile_pos = f'{int(mouse_pos.x)};{int(mouse_pos.y)}'
            tile_type = f'tile_{self.selected_tile}'
            tile_data = [tile_pos, tile_type, self.selected_rotation, round(self.selected_size, 2)]
            if str(self.selected_layer) not in current_data:
                current_data[str(self.selected_layer)] = []
            # Write the tile data to the chunk
            current_data[str(self.selected_layer)].append(Tile(self.app, tile_data))

        elif self.app.mouse_click[0] and not self.add_tiles:
            # Find the targeted chunk
            mouse_pos = self.app.mouse_pos + self.app.player.pos - WINDOW_SIZE / 2
            chunk_pos = f'{int(mouse_pos.x // 640)};{int(mouse_pos.y // 640)}'
            if chunk_pos in self.data:
                for layer, tiles in self.data[chunk_pos].data.items():
                    # List for storing all tiles to be deleted
                    deleted_tiles = []
                    for index, tile in enumerate(tiles):
                        if tile.pos.distance_to(mouse_pos) <= 50:
                            deleted_tiles.append(index)
                    # Delete all the tiles in a order that will not throw errors
                    for index in sorted(deleted_tiles, reverse=True):
                        tiles.pop(index)

    def place_entities(self):
        if self.app.mouse_click[0] and self.add_tiles and -1 < self.selected_entity < 5:
            # Find where to put new entity
            mouse_pos = self.app.mouse_pos + self.app.player.pos - WINDOW_SIZE / 2
            if str(self.selected_entity) not in self.entity_locations.keys():
                self.entity_locations[str(self.selected_entity)] = []
            entity_pos = f'{int(mouse_pos.x)};{int(mouse_pos.y)}'
            self.entity_locations[str(self.selected_entity)].append(entity_pos)

        elif self.app.mouse_click[0] and not self.add_tiles:
            mouse_pos = self.app.mouse_pos + self.app.player.pos - WINDOW_SIZE / 2
            for entity, positions in self.entity_locations.items():
                # List for storing all entities to delete
                deleted_entities = []
                for index, position in enumerate(positions):
                    x, y = tuple(position.split(';'))
                    if pg.Vector2(int(x), int(y)).distance_to(mouse_pos) <= 50:
                        deleted_entities.append(index)
                # Delete all the entities in a order that will not throw errors
                for index in sorted(deleted_entities, reverse=True):
                    self.entity_locations[str(self.selected_entity)].pop(index)

    def render_background(self):
        self.app.screen.blit(self.app.sprite_handler.background_sprites['main_menu'], (0, 0))


                    

                            
