from pathlib import Path
import re
from os.path import normpath

from PIL import Image

unit_b_size = 16
unit_m_size = 24

def mkdir_if_not_exists(path):
    Path(path).mkdir(parents = True, exist_ok = True)

def apply_transparency(tile, tt = (255, 127, 255)):
    tile = tile.convert('RGBA')
    pixels = tile.getdata()

    new_pixels = []

    for pixel in pixels:
        new_pixels.append((0, 0, 0, 0) if pixel[:3] == tt else pixel)

    tile.putdata(new_pixels)

    return tile

def crop_image(image, corner_h, corner_v, t_rows, t_cols, size, border_h = 1, border_v = 1):
    tiles = []
    for col in range(t_cols):
        for row in range(t_rows):
            x = ((row * size) + corner_h) + (row * border_h)
            y = ((col * size) + corner_v) + (col * border_v)

            tile = image.crop((x, y, x + size, y + size))

            print(f'{row}_{col}: {x}, {y}')

            tile = apply_transparency(tile)

            tiles.append(tile)

    return tiles

def offset_coordinate(c, x_offset = 0, y_offset = 0):
    return ((c[0][0] + x_offset, c[0][1] + y_offset, c[0][2], c[0][3]), c[1], c[2])


def offset_coordinates(coordinate_sets, x_offset = 0, y_offset = 0):
    return [
        offset_coordinate(c, x_offset, y_offset) for c in coordinate_sets
    ]

red = [
    ((  3, 104,  3, 27), unit_b_size, (1, 3)),
    (( 56, 104,  3,  3), unit_m_size, (1, 1)),
]

red += [
    offset_coordinate(red[1],  77,   0),
    offset_coordinate(red[1], 154,   0),
    ((287, 104,  2,  3), unit_m_size, (1, 1))
]

red += [
    offset_coordinate(red[1],   0,  77),
    offset_coordinate(red[1],  77,  77),
    offset_coordinate(red[1], 154,  77),
    offset_coordinate(red[4],   0,  77),
    offset_coordinate(red[1],   0, 154),
    offset_coordinate(red[1],  77, 154),
    offset_coordinate(red[1], 154, 154),
    offset_coordinate(red[4],   0, 154),
    offset_coordinate(red[1],   0, 231),
    offset_coordinate(red[1],  77, 231),
    offset_coordinate(red[1], 154, 231),
    offset_coordinate(red[4],   0, 231),
    offset_coordinate(red[1],   0, 308),
    offset_coordinate(red[1],  77, 308),
    offset_coordinate(red[1], 154, 308),
    offset_coordinate(red[4],   0, 308),
    offset_coordinate(red[1],   0, 385),
    offset_coordinate(red[1],  77, 385),
    offset_coordinate(red[1], 154, 385),
    offset_coordinate(red[4],   0, 385),
    offset_coordinate(red[1],   0, 462),
    offset_coordinate(red[1],  77, 462),
    offset_coordinate(red[1], 154, 462),
    offset_coordinate(red[0], 336,   0)
]

blue = offset_coordinates(red,   389,    0)
green = offset_coordinates(red,    0,  568)
yellow = offset_coordinates(red, 389,  568)
black = offset_coordinates(red,    0, 1136)

from tile_destinations import unit_destination as destination

units = Image.open('./original_assets/overworld_units.png')

all_units = red + blue + green + yellow + black

checked_paths = []

for c, coordinates in enumerate(all_units):
    tiles = crop_image(units, *coordinates[0], coordinates[1], *coordinates[2])
    for t, tile in enumerate(tiles):
        matches = re.match(r"^([^_]*)(_(os|bm|ge|yc|bh))?_(.*(?=_move|_un)|.*)_.*$", destination[c][t])
        _destination = matches[0]
        color = matches[1]
        unit = matches[4]

        destination_dir = normpath(f'./assets/units/{color}/{unit}')
        destination_path = normpath(f'{destination_dir}/{_destination}')

        if destination_dir not in checked_paths:
            mkdir_if_not_exists(destination_dir)

        print(f'C: {c} T: {t} - Saving: {destination_path}')
        tile.save(destination_path + '.png')
