# 2D tiled map generator

This is a simple Python project to generate 2D tile maps procedurally.
The objective of this project is to replicate, or improve the procedural generation of maps observed on Intelligent Systems / Nintendo's Advance Wars 1 and 2 for GameBoy Advance.

## Warnings

This code is not yet tested on Windows; I will appreciate any feedback to improve the usage of this initial version of the project.

I am aware that the code is janky, it started as a experimentation and proof of concept, but is guaranteed to become a usable software, not only for map generation, but for screenshot imitation too, since it is been developed for bigger purposes.

## Framework

This project was written and tested with Python 3.7.16, you can install all the dependencies with this command:

```
pip3 install -r requirements.txt
```

## Assets

This project is configured to extract, organize and work with assets available at [The Sprites Resources](https://www.spriters-resource.com/game_boy_advance/advancewars2blackholerising/):

If you are unable to execute the bash script `get_original_assets.sh`, there are the links to get them:

- [Overworld Normal](https://www.spriters-resource.com/fullview/120364/)
- [Overworld Rain](https://www.spriters-resource.com/fullview/120363/)
- [Overworld Snow](https://www.spriters-resource.com/fullview/120362/)
- [Overworld Units](https://www.spriters-resource.com/fullview/11827/)

There are additional assets that I customized to make the implementation of tile variation selection easier. For the time beeing, these ones are mandatory:

- [Customized woods](https://catbox.moe/c/tdghl6)

The image cropping scripts will look for these files:

```
./original_assets
    overworld_normal.png
    overworld_snow.png
    overworld_rain.png
    overworld_units.png
    custom_woods_normal.png
    custom_woods_rain.png
    custom_woods_snow.png
```

Make sure to correctly move the assets into this specified location.

### Extracting assets

Run these two Python scripts to make the automatic extraction of assets:

```
$ python3 map_cropper.py
```

Expected output:
```
...
C: 37 T: 0 - Saving: ./assets/map/fog/snow/bh/bh_minicannon_left_top
C: 37 T: 1 - Saving: ./assets/map/fog/snow/bh/bh_minicannon_up_top
C: 37 T: 2 - Saving: ./assets/map/fog/snow/bh/bh_minicannon_right_top
C: 37 T: 3 - Saving: ./assets/map/fog/snow/bh/bh_minicannon_down_top
C: 37 T: 4 - Saving: ./assets/map/fog/snow/bh/bh_minicannon_left_bottom
C: 37 T: 5 - Saving: ./assets/map/fog/snow/bh/bh_minicannon_up_bottom
C: 37 T: 6 - Saving: ./assets/map/fog/snow/bh/bh_minicannon_right_bottom
C: 37 T: 7 - Saving: ./assets/map/fog/snow/bh/bh_minicannon_down_bottom
```
---
```
$ python3 unit_cropper.py
```

Expected output:
```
...
C: 144 T: 72 - Saving: ./assets/units/black/cruiser/black_cruiser_un_idle1
C: 144 T: 73 - Saving: ./assets/units/black/cruiser/black_cruiser_un_idle2
C: 144 T: 74 - Saving: ./assets/units/black/cruiser/black_cruiser_un_idle3
C: 144 T: 75 - Saving: ./assets/units/black/lander/black_lander_un_idle1
C: 144 T: 76 - Saving: ./assets/units/black/lander/black_lander_un_idle2
C: 144 T: 77 - Saving: ./assets/units/black/lander/black_lander_un_idle3
C: 144 T: 78 - Saving: ./assets/units/black/sub/black_sub_un_idle1
C: 144 T: 79 - Saving: ./assets/units/black/sub/black_sub_un_idle2
C: 144 T: 80 - Saving: ./assets/units/black/sub/black_sub_un_idle3
```

After the extraction, you may be able to generate maps of any size and weather.

## Map Generation

### Warnings

Please note that this project is incomplete and even inefficient in some aspects.

First, you may notice that the algorithm is only ready for a limited terrain range, in it's current state, you can generate maps with:

- Sea
- Reefs
- Plain
- Woods
- Montains
- Roads
- Bridges*

> *Bridges can be generated wrongly, the tile validation algorithm may be improved in the future to prevent strange formations. Also, bridges can mess with the roads in some cases, you will notice.

### Straight to action

Generate a map by running `python3 map_generator.py`.

The default configurations are set to generate a 15x10 map at normal weather.

![Normal Map](./ex_footage/normal_15x10.png)

### Customizations

The current state of the project is rudimentar, and if you are not familiar with programming language, it may be annoying to use the generator.

In the `map_generator.py` script, you wil find at the end the following line:

```
my_map = Map(15, 10, 'normal', terrain_range = [0, 1, 2, 3, 4, 5, 6])
```

The `Map` class receives the params:

- `size_x` - The size in tiles at x dimension
- `size_y` - The size in tiles at y dimension
- `weather` - The weather of the tiles (`normal`, `rain` or `snow` only)
- `map_terrain` - A numpy bidimensional array of integer numbers from 0 to 28 (for now, only up to 6). Leaving it empty will result in a map filled with sea
- `terrain_range` - A list of terrain index to be used on generation

terrain index is available on `definitions.py` alongside terrains lookups and validations.

Will can generate the map with the `random_generation` method:

```
temp_weights = np.array([1, 1, 1, 1, 1, 1, 1])
temp_weights = temp_weights / np.sum(temp_weights, axis = 0, keepdims = True)
my_map.random_generation(temp_weights)
```

This snippets is a example of how to pass selection weights for the random generator. You will prefer to define the terrain range in ascending order as so for the weights given to the method. If you want, for example to fill the map with more sea, you can send this weights:

```
temp_weights = np.array([1.5, 1, 1, 1, 1, 1, 1])
temp_weights = temp_weights / np.sum(temp_weights, axis = 0, keepdims = True)
my_map.random_generation(temp_weights)
```

And it will be normalized automatically with a higher value for `sea` (`0`) terrain. You can set the weight to 0 if you want to completely avoid a specific terrain (or remove it from the `terrain_range`).

To conclude the generating process, you may call `render` and / or `save` functions, respectively:

```
my_map.render()
my_map.save('./my_maps/map.png')

or

my_map.save()
```

And you will have a PNG image of the generated map.

## Caches, variations and validations

The map generator uses two json files to store variations and validations cache, with the help of adjacent hashes.

Adjacent Hashes is a hash generated from the adjacent terrains of a given coordinate. Each terrain has his own lookups against specific terrains (ex: Sea has lookups against plain terrains, that can be plains itself, woods, roads, etc.), and for each terrain that contain variations, a hash is generated to store the result of the variation finding algorithm or the validation process.

This cache can improve the rendering or validation process' speed up to 70%; the more variation you generate, the more cache will be available to skip repetitive calculations and this is applied to validation too.

## Variations

In the original game, some terrains has numberous variations, and those variations can be generated from the presence of specific adjacent terrains. A sea terrain can contain the border of plain terrains from any direction, without it, you would only be seeing floating squared plains.

The same process is applied to roads, the variation finding function will automatically connect any road terrain to form a single cohesive road.

Some minor details are also applied from this process, for example the shadows projected from woods, montains and buildings.

## Validation

The validation process is currently incomplete, but for reefs and bridges, it is correctly choosing whether or not you can place the specified terrain in a given coordinate. For example, you can only place a reef if the given coordinate doesn't contain any plain terrain in it's adjacent area of 3x3.

For future updates, this function will be able to automatically update the evaluation of terrains when you update a tile, giving more flexibility to the user when designing a map, just like the original game.

## Examples

 - 30x20 (size of Map Design) snow map with more woods:

 ```
 my_map = Map(30, 20, 'snow', terrain_range = [0, 1, 2, 3, 4, 5, 6])
 temp_weights = np.array([1, 1, 1, 1.5, 1, 1, 1])
 ```

 ![Snow Map](./ex_footage/snow_30x20.png)

 - 15x10 (Size of GameBoy Advance screen) rain map with more sea and reefs:

  ```
 my_map = Map(15, 10, 'rain', terrain_range = [0, 1, 2, 3, 4, 5, 6])
 temp_weights = np.array([1.3, 1.5, 1, 1, 1, 1, 1])
 ```

![Rain Map](./ex_footage/rain_15x10.png)
