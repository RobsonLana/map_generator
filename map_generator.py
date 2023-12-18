import hashlib
import json
import pickle
import re
import sys
from os.path import normpath


from PIL import Image
import numpy as np

from definitions import\
    bitmasks, rotation_remover, mask_rotation,\
    terrains,\
    sea_indexes, plain_indexes, shadow_indexes, building_indexes, structure_indexes,\
    animated_terrains,\
    validation_priority

adjacent_reorder = [0, 3, 6, 7, 8, 5, 2 ,1]

adjacent_bits = [
    0b10000000, 0b00000001, 0b00000010,
    0b01000000,             0b00000100,
    0b00100000, 0b00010000, 0b00001000
]

adjacent_relative_coordinates = np.array([
    (-1, -1), (-1, 0), (-1, 1),
    (0, -1), (0, 0), (0, 1),
    (1, -1), (1, 0), (1, 1)
])

variation_cache = {}
validation_cache = {}

countings = {
    'new_hashes': 0,
    'reused_hashes': 0
}

try:
    with open(normpath('./variation_cache.json'), 'r') as file:
        variation_cache = json.load(file)

    with open(normpath('./validation_cache.json'), 'r') as file:
        validation_cache = json.load(file)

except FileNotFoundError:
    0

def save_cache(cache, cache_name):
    with open(normpath(f'./{cache_name}_cache.json'), 'w') as file:
        return file.write(json.dumps(cache, indent = 2))

def adjacent_bitmasks_to_hash(bitmasks, group_bitmasks, inclusions = []):
    if len(inclusions) == 0:
        return None

    final_object = {}

    for inclusion in inclusions:
        mask = bitmasks.get(inclusion, group_bitmasks.get(inclusion, None))

        if mask != None:
            final_object[inclusion] = mask.tolist()

    final_object = tuple(final_object.items())

    return hashlib.sha256(pickle.dumps(final_object)).hexdigest()

vec_mask_rotation = np.vectorize(mask_rotation)

def find_variation(target_terrain, adjacent_bitmasks, adjacent_group_bitmasks):
    target_lookups = bitmasks[target_terrain].get('lookups', [])

    if len(target_lookups) == 0:
        return ""

    relations = bitmasks[target_terrain]['groups_relations'] + bitmasks[target_terrain]['targets_relations']
    bitmask_hash = adjacent_bitmasks_to_hash(adjacent_bitmasks, adjacent_group_bitmasks, relations)

    if str(target_terrain) not in variation_cache:
        variation_cache[str(target_terrain)] = {}

    if bitmask_hash in variation_cache[str(target_terrain)]:
        countings['reused_hashes'] += 1
        return variation_cache[str(target_terrain)][bitmask_hash]

    all_postfix = np.array([])
    all_matches = np.full((len(target_lookups), 4), False)

    for l, lookup in enumerate(target_lookups):
        nullated = False

        if 'nulled_by' in lookup:
            n, nulled_by = lookup['nulled_by']
            nullated = np.any(np.array(nulled_by) & np.array(all_matches[n]))

        if nullated:
            continue

        lookup_mask = 0b00000000

        target_groups = lookup.get('target_groups', [])
        targets = lookup.get('targets', [])

        if len(target_groups) > 0 :
            lookup_mask |= np.bitwise_or.reduce(np.vectorize(lambda a, g: a[g])(adjacent_group_bitmasks, target_groups))

        if len(targets) > 0:
            lookup_mask |= np.bitwise_or.reduce(np.vectorize(lambda a, t: a[t])(adjacent_bitmasks, targets))

        if 'rule' in lookup:
            lookup_mask = rotation_remover(lookup_mask, *lookup['rule'])

        masks = lookup['masks']

        for mask in masks:
            if type(masks[mask]) == str:
                if lookup_mask & mask == mask:
                    all_matches[l] |= True
                    all_postfix = np.append(all_postfix, masks[mask])

                continue

            mask_postfixs = np.array([])
            rotated_mask = np.vectorize(mask_rotation)(mask, np.arange(4))
            matchings = np.bitwise_and(np.array([lookup_mask]), rotated_mask) == rotated_mask
            all_matches[l] |= matchings

            mask_postfixs = np.append(mask_postfixs, np.array(masks[mask][0])[matchings])

            if len(mask_postfixs) > 0:
                all_postfix = np.append(all_postfix, masks[mask][1].join(mask_postfixs))


    final_postfix = "_".join(all_postfix)

    variation_cache[str(target_terrain)][bitmask_hash] = final_postfix
    countings['new_hashes'] += 1

    return final_postfix

def tile_selection(target_terrain, adjacent_bitmasks, adjacent_group_bitmasks, weather, fog = False):
    variation = find_variation(target_terrain, adjacent_bitmasks, adjacent_group_bitmasks)

    variation = f'_{variation}' if variation != "" else ""

    terrain = terrains[target_terrain]
    animated = int(target_terrain in animated_terrains) or ""
    fog = 'fog' if fog else 'clear'
    return f'./assets/map/{fog}/{weather}/{terrain}/{terrain}{animated}{variation}.png'

import timeit

class Map:

    def __init__(
            self,
            size_x = 15,
            size_y = 10,
            weather = 'normal',
            map_terrain = None,
            terrain_range = [0, 2, 3, 4, 5]
    ):

        self.x = size_x if size_x >= 15 else 15
        self.x_total = self.x + 2
        self.y = size_y if size_y >= 10 else 10
        self.y_total = self.y + 2
        self.weather = weather

        self.map_terrain = np.full((self.y_total, self.x_total), 0)
        self.map_bitmasks = { 0: np.full((self.y_total, self.x_total), True) }
        self.map_bitmasks[0][1:self.y + 1, 1:self.x + 1] = np.full((self.y, self.x), False)
        self.map_evaluation = np.full((self.y_total, self.x_total), False)
        self.evaluated = np.full((self.y_total, self.x_total), False)

        self.group_bitmasks = {
            "sea": np.full((self.y_total, self.x_total), False),
            "plain": np.full((self.y_total, self.x_total), False),
            "shadow": np.full((self.y_total, self.x_total), False),
            "building": np.full((self.y_total, self.x_total), False),
            "structure": np.full((self.y_total, self.x_total), False),
        }

        self.terrain_range = terrain_range


        self.assets = {}
        self.render_index = [["" for x in range(0, self.x)] for y in range(0, self.y)]

        if map_terrain != None:
            self.map_terrain[:self.y, :self.x] = map_terrain

        self.update_metadata()

    def adjacent_cut(self, x, y):
        return np.array(self.map_terrain[y:y + 3, x:x + 3])

    def adjacent_bitmasks(self, x, y):
        cut_bitmasks = {}
        for terrain in self.map_bitmasks:
            cut_bitmasks[terrain] = np.packbits(self.map_bitmasks[terrain][y:y + 3, x:x + 3].flat[adjacent_reorder])[0]

        return cut_bitmasks

    def adjacent_group_bitmasks(self, x, y):
        cut_bitmasks = {}
        for group in self.group_bitmasks:
            cut_bitmasks[group] = np.packbits(self.group_bitmasks[group][y:y + 3, x:x + 3].flat[adjacent_reorder])[0]

        return cut_bitmasks

    def tile_evaluation(self, terrain, x, y):
        if not self.map_evaluation[y, x]:
            return True

        if self.evaluated[y, x]:
            #return True
            0

        cascate_evaluation = True
        self.evaluated[y, x] = True

        validations = bitmasks[terrain]['validations']
        relations = bitmasks[terrain]['groups_relations'] + bitmasks[terrain]['targets_relations']
        priority = validation_priority[terrain]

        adjacent_bitmasks = self.adjacent_bitmasks(x - 1, y - 1)
        adjacent_group_bitmasks = self.adjacent_group_bitmasks(x - 1, y - 1)

        bitmask_hash = adjacent_bitmasks_to_hash(adjacent_bitmasks, adjacent_group_bitmasks, relations)

        if str(terrain) not in validation_cache:
            validation_cache[str(terrain)] = {}

        cached_evaluation = validation_cache[str(terrain)].get(bitmask_hash, None)

        if cached_evaluation:
            if cached_evaluation != True:
                self.change_tile(cached_evaluation, x, y, cascate_evaluation)

            return True

        validations_matches = np.full(len(validations), True)
        validations_rotations = np.full(len(validations), 0)

        for v, validation in enumerate(validations):
            condition = validation.get('condition', None)
            condition_rotation = None

            if condition:
                condition_rotation = validations_rotations[condition[0][-1]]

                if np.any(validations_matches[condition[0]] != True ^ ~np.array(condition[1])):
                    validations_matches[v] = validations_matches[condition[0]][0]
                    continue

            validation_mask = np.array([0b00000000])

            target_groups = validation.get('target_groups', [])
            targets = validation.get('targets', [])

            if len(target_groups) > 0:
                validation_mask |= np.bitwise_or.reduce(np.vectorize(lambda a, g: a[g])(adjacent_group_bitmasks, target_groups))

            if len(targets) > 0:
                validation_mask |= np.bitwise_or.reduce(np.vectorize(lambda a, t: a[t])(adjacent_bitmasks, targets))

            masks = validation['masks']

            rotative = validation.get('rotative', False)
            rotation = np.arange((3 * rotative) + 1)
            masks_items = np.array(list(masks.items()))

            masks = masks_items[:, 0]
            positives = np.array(masks_items[:, 1], dtype = bool)

            positive_masks = np.full((len(masks[positives]), len(rotation)), 0b0000000)
            negative_masks = np.full((len(masks[~positives]), len(rotation)), 0b0000000)

            if len(masks[positives]) > 0:
                for m, mask in enumerate(masks[positives]):
                    positive_masks[m] = np.vectorize(mask_rotation)(mask, rotation)

            if len(masks[~positives]) > 0:
                for m, mask in enumerate(masks[~positives]):
                    negative_masks[m] = np.vectorize(mask_rotation)(mask, rotation)

            positive_match = np.vectorize(lambda m: np.bitwise_and(validation_mask, m) == m, otypes=[bool])(positive_masks)
            negative_match = np.vectorize(lambda m: np.bitwise_and(validation_mask, m) > 0, otypes=[bool])(negative_masks)

            match_rotation = np.where(positive_match[:] == True)[0]

            match_rotation = condition_rotation or match_rotation[0] if len(match_rotation) > 0 else 0

            validations_rotations[v] = match_rotation

            if type(positive_match) == np.array and len(positive_match) > 1:
                positive_match = positive_match[:, match_rotation]

            if type(negative_match) == np.array and len(negative_match) > 1:
                negative_match = negative_match[:, match_rotation]

            non_empty_positive = ~np.any(positive_masks == 0b00000000)
            non_empty_negative = ~np.any(negative_masks == 0b00000000)

            valid = positive_match if non_empty_positive else [False] & negative_match if non_empty_negative else [True]

            if len(valid) > 0 and not valid[:, match_rotation]:
                validations_matches[v] = validation['substitution']

        substitutions = np.where(validations_matches != True)[0]

        if len(substitutions) > 0:
            validation_cache[str(terrain)][bitmask_hash] = validations_matches[substitutions[-1]]
            self.change_tile(validations_matches[substitutions[-1]], x, y, cascate_evaluation)

        else:
            validation_cache[str(terrain)][bitmask_hash] = True
            # self.evaluated[y, x] = True

        return True

    def evaluate_map(self):
        y_i, x_i = np.where(self.map_evaluation == True)

        self.evaluated = np.full((self.y_total, self.x_total), False)

        for y, x in zip(y_i, x_i):
            terrain = self.map_terrain[y, x]
            self.tile_evaluation(terrain, x, y)

    def update_metadata(self):
        self.map_bitmasks = {t: (self.map_terrain == t) for t in self.terrain_range}

        self.group_bitmasks['sea'] = np.isin(self.map_terrain, sea_indexes)
        self.group_bitmasks['plain'] = np.isin(self.map_terrain, plain_indexes)
        self.group_bitmasks['shadow'] = np.isin(self.map_terrain, shadow_indexes)
        self.group_bitmasks['building'] = np.isin(self.map_terrain, building_indexes)
        self.group_bitmasks['structure'] = np.isin(self.map_terrain, structure_indexes)

        self.map_evaluation = np.vectorize(lambda t: 'validations' in bitmasks[t])(self.map_terrain)

    def update_tile_metadata(self, x, y):
        terrain = self.map_terrain[y, x]

        for t in self.terrain_range:
            self.map_bitmasks[t][y, x] = t == terrain

        self.group_bitmasks['sea'][y, x] = terrain in sea_indexes
        self.group_bitmasks['plain'][y, x] = terrain in plain_indexes
        self.group_bitmasks['shadow'][y, x] = terrain in shadow_indexes
        self.group_bitmasks['building'][y, x] = terrain in building_indexes
        self.group_bitmasks['structure'][y, x] = terrain in structure_indexes

        self.map_evaluation[y, x] = 'valdations' in bitmasks[terrain]

    def change_tile(self, terrain, x, y, cascate_evaluation = False):
        self.map_terrain[y, x] = terrain
        self.update_tile_metadata(x, y)
        self.evaluated[y, x] = False

        if cascate_evaluation:
            adjacent_terrains = self.adjacent_cut(x - 1, y - 1)
            at_shape = adjacent_terrains.shape
            ry, rx = np.meshgrid(np.arange(at_shape[0]), np.arange(at_shape[1]), indexing='ij')

            np.vectorize(
                lambda at, _ry, _rx: self.tile_evaluation(at, x - 1 + _rx, y - 1 + _ry)
            )(adjacent_terrains, ry, rx)

    def random_generation(self, weights):
        for y, map_x in enumerate(self.map_terrain[1:self.y + 1, 1:self.x + 1]):
            for x, terrain in enumerate(map_x):
                choices = sorted(zip(np.vectorize(lambda w: np.random.rand() * w)(temp_weights), self.terrain_range))[::-1]

                valid = self.change_tile(choices[0][1], x + 1, y + 1, cascate_evaluation = False)

        self.update_metadata()
        self.evaluate_map()

    def render(self):
        self.map_image = Image.new("RGBA", (self.x * 16, self.y * 16), (0, 0, 0, 1))

        for y, map_x in enumerate(self.map_terrain[1:self.y + 1, 1:self.x + 1]):
            for x, terrain in enumerate(map_x):
                adjacent_cut = self.adjacent_cut(x, y)
                adjacent_bitmasks = self.adjacent_bitmasks(x, y)
                adjacent_group_bitmasks = self.adjacent_group_bitmasks(x, y)

                tile = tile_selection(adjacent_cut[1, 1], adjacent_bitmasks, adjacent_group_bitmasks, self.weather, fog = False)

                if tile not in self.assets:
                    self.assets[tile] = Image.open(tile)

                self.render_index[y][x] = tile
                self.map_image.paste(self.assets[tile], (x * 16, y * 16), mask = self.assets[tile])

        print(countings)
        save_cache(variation_cache, 'variation')

    def save(self, destination = './map.png'):
        self.map_image.save(normpath(destination))


if __name__ == "__main__":
    # variation_cache["6"] = {} # This will clear the variation cache for specified terrain

    sys.setrecursionlimit(3000) # May need this configuration for bigger maps
    my_map = Map(15, 10, 'normal', terrain_range = [0, 1, 2, 3, 4, 5, 6])
    temp_weights = np.array([1, 1, 1, 1.5, 1, 1, 1])
    temp_weights = temp_weights / np.sum(temp_weights, axis = 0, keepdims = True)

    random_start = timeit.default_timer()
    my_map.random_generation(temp_weights)
    random_end = timeit.default_timer() - random_start

    render_start = timeit.default_timer()
    my_map.render()
    render_end = timeit.default_timer() - render_start
    my_map.save()

    print(f'random: {random_end} | render: {render_end}')
