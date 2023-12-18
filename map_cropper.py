from pathlib import Path
import re
from os.path import normpath

from PIL import Image

def mkdir_if_not_exists(path):
    Path(path).mkdir(parents = True, exist_ok = True)

def symlink(src_file, link_path):
    link_path = Path(link_path).absolute()
    src_file = Path(src_file).absolute()
    if link_path.is_symlink():
        link_path.unlink()

    link_path.symlink_to(src_file)

def apply_transparency(tile, tt = (0, 0, 0)):
    tile = tile.convert('RGBA')
    pixels = tile.getdata()

    new_pixels = []

    for pixel in pixels:
        new_pixels.append((0, tt[0], tt[1], tt[2]) if pixel[:3] == tt else pixel)

    tile.putdata(new_pixels)

    return tile

def crop_image(image, corner_h, corner_v, t_rows, t_cols, border_h = 1, border_v = 1, tile_size = 16):
    tiles = []
    for col in range(t_cols):
        for row in range(t_rows):
            x = ((row * tile_size) + corner_h) + (row * border_h)
            y = ((col * tile_size) + corner_v) + (col * border_v)

            tile = image.crop((x, y, x + tile_size, y + tile_size))

            print(f'{row}_{col}: {x}, {y}')

            tile = apply_transparency(tile)

            tiles.append(tile)

    return tiles

def offset_coordinates(coordinate_sets, x_offset = 0, y_offset = 0):
    return [
        ((c[0][0] + x_offset, c[0][1] + y_offset, c[0][2], c[0][3]), c[1]) for c in coordinate_sets
    ]

# /Map the tiles using the cropping coordinates
# x, y = upper left corner of the selected area
# r, c = number of rows and columns
# hb, vb = Horizontal and vertical border size

terrain_clear = [
    #  x,     y,  c,  r   hb,vb
    ((  3,   14, 15,  4), (1, 1)),
    ((  3,   82,  1,  1), (1, 1)),
    ((292,   14,  5,  2), (1, 1)),
    ((275,   48,  6,  3), (1, 1)),
]

custom_woods_clear = [
    ((  0,    0,  3,  2), (1, 1))
]

custom_woods_fog = offset_coordinates(custom_woods_clear, 0, 34)

terrain_fog = offset_coordinates(terrain_clear, 376)

sea1_clear = [
    ((  3,  112, 22,  3), (1, 1)),
    ((  3,  163, 11,  1), (1, 1)),
    ((207,  163, 10,  1), (1, 1)),
]

sea1_fog = offset_coordinates(sea1_clear, 376)

sea2_clear = offset_coordinates(sea1_clear, 0, 70)
sea2_fog = offset_coordinates(sea1_clear, 376)

sea3_clear = offset_coordinates(sea2_clear, 0, 70)
sea3_fog = offset_coordinates(sea2_clear, 376)

sea4_clear = offset_coordinates(sea3_clear, 0, 70)
sea4_fog = offset_coordinates(sea3_clear, 376)

river1_clear = [
    ((  3,  420,  9,  8), (1, 1)),
    ((190,  420, 11,  8), (1, 1))
]

river1_fog = offset_coordinates(river1_clear, 376)

river2_clear = [
    ((  3,  575,  7,  8), (1, 1)),
    ((224,  575,  9,  8), (1, 1))
]

river2_fog = offset_coordinates(river2_clear, 376)

river3_clear = [
    ((  3,  730,  9,  8), (1, 1)),
    ((224,  730,  9,  8), (1, 1))
]

river3_fog = offset_coordinates(river3_clear, 376)

river4_clear = [
    ((  3,  885,  9,  8), (1, 1)),
    ((292,  885,  5,  8), (1, 1))
]

river4_fog = offset_coordinates(river4_clear, 376)

buildings_red_on = [
    ((  3, 1034,  6,  2), (1, 0)),
    ((105, 1050,  1,  1), (1, 1)),
    ((122, 1034,  3,  2), (1, 0))
]

buildings_red_off = offset_coordinates(buildings_red_on, 172)

buildings_blue_on = offset_coordinates(buildings_red_on, 0, 33)

buildings_blue_off = offset_coordinates(buildings_blue_on, 172)

buildings_yellow_on = offset_coordinates(buildings_blue_on, 0, 33)

buildings_yellow_off = offset_coordinates(buildings_yellow_on, 172)

buildings_green_on = offset_coordinates(buildings_yellow_on, 0, 33)

buildings_green_off = offset_coordinates(buildings_green_on, 172)

buildings_black_on = offset_coordinates(buildings_green_on, 0, 33)

buildings_black_off = offset_coordinates(buildings_black_on, 172)

buildings_neutral = [
    ((  3, 1212,  6, 2), (1, 0)),
    ((105, 1228,  1, 1), (1, 1)),
    ((122, 1212,  3, 2), (1, 0)),
    ((  3, 1245,  1, 2), (1, 0)),
    (( 20, 1261,  1, 1), (1, 1))
]

buildings_fog = offset_coordinates(buildings_neutral, 172)

smoke = [
    ((  3, 1291,  4, 1), (1, 1))
]

volcano = [
    ((150, 1291,  4, 4), (0, 0)),
    ((215, 1291,  4, 4), (0, 0)),
    ((280, 1291,  4, 4), (0, 0))
]

bh_off = [
    ((347, 1163,  4, 4), (0, 0)),
    ((412, 1163,  4, 4), (0, 0)),
    ((477, 1163,  3, 4), (0, 0)),
    ((526, 1179,  3, 3), (0, 0)),
    ((575, 1179,  3, 3), (0, 0)),
    ((624, 1179,  3, 3), (0, 0)),
    ((673, 1195,  1, 2), (0, 0)),
]

bh_on = offset_coordinates(bh_off, 0, -129) + [
    ((347, 1101,  3, 3), (0, 0)),
    ((396, 1117,  4, 2), (1, 0))
]

bh_fog = offset_coordinates(bh_on, 0, 207)

normal_coordinates = \
    terrain_clear +\
    sea1_clear +\
    sea2_clear +\
    sea3_clear +\
    sea4_clear +\
    river1_clear +\
    river2_clear +\
    river3_clear +\
    river4_clear +\
    buildings_red_on + buildings_red_off +\
    buildings_blue_on + buildings_blue_off +\
    buildings_yellow_on + buildings_yellow_off +\
    buildings_green_on + buildings_green_off +\
    buildings_black_on + buildings_black_off +\
    buildings_neutral + smoke +\
    volcano + bh_on + bh_off

fog_index_match = [i for i in range(0, 24)] +\
    [i for i in range(54, 59)] +\
    [i for i in range(63, 72)]

fog_coordinates =\
    terrain_fog +\
    sea1_fog +\
    sea2_fog +\
    sea3_fog +\
    sea4_fog +\
    river1_fog +\
    river2_fog +\
    river3_fog +\
    river4_fog +\
    buildings_fog +\
    bh_fog

excludents = {
    'snow': [i for i in range(59, 79)],
    'rain': [i for i in range(24, 79)],
    'normal': []
}

map_sets = {}
woods_sets = {}

map_sets['normal'] = Image.open('./original_assets/overworld_normal.png')
woods_sets['normal'] = Image.open('./original_assets/custom_woods_normal.png')

map_sets['rain'] = Image.open('./original_assets/overworld_rain.png')
woods_sets['rain'] = Image.open('./original_assets/custom_woods_rain.png')

map_sets['snow'] = Image.open('./original_assets/overworld_snow.png')
woods_sets['snow'] = Image.open('./original_assets/custom_woods_snow.png')

from tile_destinations import map_destination as destination, custom_woods_destination as cw_destination

checked_paths = []

def save_tile(set_name, destination_name, tile, fog = 'clear'):
    destination_dir = normpath(f'./assets/map/{fog}/{set_name}/{re.match(r"^[^_0-9]*", destination_name)[0]}')

    destination_path = normpath(f'{destination_dir}/{destination_name}')

    if '*' not in destination_name:
        if destination_dir not in checked_paths:
            mkdir_if_not_exists(destination_dir)

        if c in excludents[set_name]:
            symlink(destination_path.replace(set_name, 'normal') + '.png', destination_path + '.png')

        else:
            print(destination_path)
            tile.save(destination_path + '.png')

for set_name, map_set in map_sets.items():
    for c, coordinates in enumerate(normal_coordinates):
        tiles = crop_image(map_set, *coordinates[0], *coordinates[1])

        for t, tile in enumerate(tiles):
            print(f'C: {c} T: {t} - Saving: ', end = '')
            save_tile(set_name, destination[c][t], tile)

    for c, coordinates in enumerate(custom_woods_clear):
        tiles = crop_image(woods_sets[set_name], *coordinates[0], *coordinates[1])

        for t, tile in enumerate(tiles):
            print(f'C: {c} T: {t} - Saving: ', end = '')
            save_tile(set_name, cw_destination[c][t], tile)


    for c, coordinates in enumerate(fog_coordinates):
        tiles = crop_image(map_set, *coordinates[0], *coordinates[1])
        for t, tile in enumerate(tiles):
            print(f'C: {c} T: {t} - Saving: ', end = '')
            save_tile(set_name, destination[fog_index_match[c]][t], tile, fog = 'fog')


    for c, coordinates in enumerate(custom_woods_fog):
        tiles = crop_image(woods_sets[set_name], *coordinates[0], *coordinates[1])

        for t, tile in enumerate(tiles):
            print(f'C: {c} T: {t} - Saving: ', end = '')
            save_tile(set_name, cw_destination[c][t], tile, fog = 'fog')
