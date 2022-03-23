from os import walk
import pygame
from csv import reader
from settings import tile_size

def import_folder(path):
    surface_list = []
    for _,__,img_files in walk(path):
        for image in img_files:
            full_path = path + '/' + image
            image_surface = pygame.image.load(full_path).convert_alpha()
            surface_list.append(image_surface)

    return surface_list

def import_csv_layout(path):
    terrain_map = []
    with open(path) as map:
        level = reader(map, delimiter=',')
        for row in level:
            terrain_map.append(list(row))
        return terrain_map

# cut the tiles from the sprite sheet into an array of 64x64 tiles
def import_tiled_layout(path):
    surface = pygame.image.load(path).convert_alpha()
    tile_x = int(surface.get_size()[0]/tile_size)
    tile_y = int(surface.get_size()[1]/tile_size)
    cut_tiles = []
    for row in range(tile_y):
        for col in range(tile_x):
            x_pos = col*tile_size
            y_pos = row*tile_size
            new_surface = pygame.Surface((tile_size, tile_size))
            tile = pygame.Rect(x_pos, y_pos, tile_size, tile_size) # a 64x64 tile that is cut from the tiles sheet
            new_surface.blit(surface, (0,0), tile)
            cut_tiles.append(new_surface)
    return cut_tiles



