
import pygame as pg

class Tile:

    def __init__(self, app, data):
        
        # data = [position, type, variation, rotation]
        pos_x, pos_y = tuple(data[0].split(';'))
        self.pos = pg.Vector2(float(pos_x), float(pos_y))
        self.tile_type = data[1]
        self.rotation = data[2]
        self.size = data[3]
        
        # Modify the tile surface
        self.surf = app.sprite_handler.tile_sprites[self.tile_type][0]
        if self.rotation != 0:
            self.surf = pg.transform.rotate(self.surf, self.rotation)
        if self.size != 1:
            self.surf = pg.transform.scale_by(self.surf, self.size)
        self.rect = self.surf.get_rect(center=self.pos)
    
