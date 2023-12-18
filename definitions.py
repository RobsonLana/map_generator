terrains = [
    'sea',              #  0
    'reef',             #  1
    'plain',            #  2
    'wood',             #  3
    'montain',          #  4
    'road',             #  5
    'bridge',           #  6
    'river',            #  7
    'river_waterfall',  #  8
    'pipe',             #  9
    'shoal',            # 10
    'hq',               # 11
    'city',             # 12
    'base',             # 13
    'airport',          # 14
    'port',             # 15
    'lab',              # 16
    'silo',             # 17
    'volcano',          # 18
    'missile',          # 19
    'fortress',         # 20
    'factory',          # 21
    'deathlaser',       # 22
    'cannon',           # 23
    'laser',            # 24
    'minicannon'        # 25
    'pipebreach',       # 26
    'deathlaser_entry', # 27
    'cannon_entry'      # 28
]

sea_indexes = [0, 1, 6, 9]

plain_indexes = [i for i in range(2, 29)]
del plain_indexes[4] # remove bridge
del plain_indexes[5] # remove waterfall
del plain_indexes[6] # remove shoal

shadow_indexes = [3, 4, 11, 13, 14, 15, 16]

building_indexes = [i for i in range(11, 18)]

structure_indexes = [i for i in range(18, 29)]

animated_terrains = [0, 1, 7, 10]
  #llldrrru
#0b00000000
  #cxcxcxcx

import numpy as np

validation_priority = [
    0,
    1,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    1,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0
]

def mask_rotation(mask, times = 1):
    return ((((mask << 8) | mask) >> int(8 - (2 * times))) & (1 << 8) -1)

def rotation_remover(bitmask, rule, target):
    bitmask = np.array([bitmask])
    rule = np.vectorize(mask_rotation)(rule, np.arange(4))
    target = np.vectorize(mask_rotation)(target, np.arange(4))

    matchings = np.bitwise_and(bitmask, rule) == rule
    combined_target = np.bitwise_or.reduce(target[matchings])

    bitmask = np.bitwise_and(bitmask, np.bitwise_not(combined_target))

    return int(bitmask[0])

bitmasks = [
    { # 0 sea
        "lookups": [
            {
                "masks": {
                    0b00000001: (['u', 'r', 'd', 'l'], ''),
                    0b00000010: (['c_ur', 'c_rd', 'c_dl', 'c_ul'], '_')
                },
                "target_groups": ['plain'],
                "rule": (0b00000001, 0b10000010)
            }
        ],
        "groups_relations": ['plain'],
        "targets_relations": []
    },
    { # 1 reef
        "validations": [
            {
                "masks": {
                    0b11111111: True
                },
                "substitution": 0,
                "target_groups": ['sea']
            }
        ],
        "groups_relations": ['plain'],
        "targets_relations": [],
        "substitution": 0
    },
    { # 2 plain
        "lookups": [
            {
                "masks": {
                    0b01000000: 'shadow'
                },
                "target_groups": ['shadow']
            },
            {
                "masks": {
                    0b00010000: 'montain'
                },
                "targets": [4],
            }
        ],
        "groups_relations": ['shadow'],
        "targets_relations": [4]
    },
    { # 3 wood
        "lookups": [
            {
                "masks": {
                    0b11000111: (['u', 'r', 'd', 'l'], ''),
                },
                "targets": [3]
            },
            {
                "masks": {
                    0b00000111: (['c_ur', 'c_rd', 'c_dl', 'c_ul'], '_')
                },
                "targets": [3],
                "nulled_by": ([0], [True, True, True, True])
            },
            {
                "masks": {
                    0b01000000: 'shadow'
                },
                "target_groups": ['shadow'],
                "nulled_by": ([0, 1], [[True, False, True, True], [False, False, True, True]]),
            }
        ],
        "groups_relations": ['shadow'],
        "targets_relations": [3]
    },
    { # 4 montain
        "lookups": [
            {
                "masks": {
                    0b00000001: 'big'
                },
                "targets": [2, 4]
            },
            {
                "masks": {
                    0b00010000: 'montain'
                },
                "targets": [4]
            }
        ],
        "groups_relations": [],
        "targets_relations": [2, 4]
    },
    { # 5 roads
        "lookups": [
            {
                "masks": {
                    0b01010101: 'urdl'
                },
                "targets": [5, 6]
            },
            {
                "masks": {
                    0b00010101: (['urd', 'rdl', 'udl', 'url'], '')
                },
                "targets": [5, 6],
                "rule": (0b00010101, 0b01000000),
                "nulled_by": ([0], [True, True, True, True])
            },
            {
                "masks": {
                    0b00000101: (['ur', 'rd', 'dl', 'ul'], '')
                },
                "targets": [5, 6],
                "rule": (0b00000101, 0b01010000),
                "nulled_by": ([0, 1], [True, True, True, True])
            },
            {
                "masks": {
                    0b00010001: (['v', 'h', '', ''], '')
                },
                "targets": [5, 6],
                "nulled_by": ([0, 1, 2], [True, True, True, True])
            },
            {
                "masks": {
                    0b00000001: (['v', 'h', 'v', 'h'], '')
                },
                "targets": [5, 6],
                "nulled_by": ([0, 1, 2, 3], [True, True, True, True])
            },
            {
                "masks": {
                    0b00000000: 'h'
                },
                "targets": [5, 6],
                "nulled_by": ([0, 1, 2, 3, 4], [True, True, True, True])
            },
            {
                "masks": {
                    0b01000000: 'shadow'
                },
                "target_groups": ['shadow'],
            }
        ],
        "groups_relations": ['shadow'],
        "targets_relations": [5, 6]
    },
    { # 6 bridge
        "lookups": [
            {
                "masks": {
                    0b00010001: (['v', 'h', '', ''], '')
                },
                "rule": (0b00010001, 0b01000100),
                "target_groups": ['plain'],
                "targets": [6]
            },
            {
                "masks": {
                    0b00000001: (['v', 'h', 'v', 'h'], '')
                },
                "target_groups": ['plain'],
                "rule": (0b00000001, 0b01010100),
                "targets": [6],
                "nulled_by": ([0], [True, True, True, True])
            },
            {
                "masks": {
                    0b00000000: 'h'
                },
                "target_groups": ['plain'],
                "targets": [6],
                "nulled_by": ([0, 1], [True, True, True, True])
            }
        ],
        "validations": [
            {
                "masks": {
                    0b00000001: True,
                },
                "target_groups": ['plain'],
                "targets": [6],
                "substitution": 0,
                "rotative": True
            },
            {
                "masks": {
                    0b01000100: True
                },
                "target_groups": ['sea'],
                "substitution": 0,
                "rotative": True
            },
            {
                "masks": {
                    0b01000100: False
                },
                "targets": [6],
                "substitution": 0,
                "rotative": True
            }
        ],
        "groups_relations": ['plain'],
        "targets_relations": [5, 6]
    },
    { # 7 river
        "lookups": [],
        "validaions": [],
        "groups_relations": [],
        "targets_relations": []
    },
    { # 8 waterfall
        "lookups": [],
        "validaions": [],
        "groups_relations": [],
        "targets_relations": []
    },
    { # 9 pipe
        "lookups": [],
        "validaions": [],
        "groups_relations": [],
        "targets_relations": []
    },
    { # 10 shoal
        "lookups": [
            {
                "masks": {
                    0b00000001: (['u', 'r', 'd', 'l'], '')
                },
                "target_groups": ['plain'],
                "rule": (0b00000001, 0b00010000)
            },
            {
                "masks": {
                    0b00000001: (['u', 'r', 'd', 'l'], '')
                },
                "targets": [10]
            },
            {
                "masks": {
                    0b00000000: 'u'
                },
                "targets": [0],
                "nulled_by": ([0, 1], [True, True, True, True])
            }
        ],
        "validations": [
            {
                "masks": {
                    0b00000001: True
                },
                "target_groups": ['plain'],
                "rotative": True,
                "substitution": 0
            },
            {
                "masks": {
                    0b00010000: False
                },
                "target_groups": ['plain'],
                "rotative": True,
                "substitution": 0,
                "condition": ([0], [True])
            },
            {
                "masks": {
                    0b00000100: True
                },
                "target_groups": ['sea'],
                "rotative": True,
                "substitution": 0,
                "condition": ([0, 1], [True, True])
            },
            {
                "masks": {
                    0b00001000: False
                },
                "target_groups": ['plain'],
                "rotative": True,
                "substitution": 0,
                "condition": ([2], [True])
            },
            {
                "masks": {
                    0b01000000: True
                },
                "target_groups": ['sea'],
                "rotative": True,
                "substitution": 0,
                "condition": ([0, 1], [True, True])
            },
            {
                "masks": {
                    0b00100000: False
                },
                "target_groups": ['plain'],
                "rotative": True,
                "substitution": 0,
                "condition": ([4], [True])
            },
        ],
        "groups_relations": ['plain', 'sea'],
        "targets_relations": [10]
    },
]

walk = [
    # infantry, mech, tires, tread, ships, trans, air
    [0, 0, 0, 0, 1, 1, 1],
    [0, 0, 0, 0, 2, 2, 1],
    [1, 1, 2, 1, 0, 0, 1],
    [1, 1, 3, 2, 0, 0, 1],
    [2, 1, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 0, 0, 1],
    [1, 1, 1, 1, 0, 0, 1],
    [2, 1, 0, 0, 0, 0, 1],
    [0, 0, 0, 0, 0, 0, 0],
    [1, 1, 1, 1, 0, 1, 1],
    [1, 1, 1, 1, 0, 0, 1],
    [1, 1, 1, 1, 0, 0, 1],
    [1, 1, 1, 1, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 0, 0, 1],
    [1, 1, 1, 1, 0, 0, 1],
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0]
]

defense = [
    0, 1, 1, 2, 4, 0, 0, 0, 0, 0,
    4, 3, 3, 3, 3, 2,
    0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0
]

units = [
    'infantry', 'mech',
    'recon', 'tank', 'md_tank', 'neo_tank',
    'apc', 'artlry', 'rockets', 'a_air', 'missiles',
    'fighter', 'bomber', 'b_copter', 't_copter',
    'b_ship', 'cruiser', 'lander', 'sub'
]

movement = [
    (0, 3), (1, 2),
    (2, 8), (3, 6), (3, 5), (3, 6),
    (3, 6), (3, 5), (1, 5), (3, 6), (1, 4),
    (6, 9), (6, 7), (6, 6), (6, 6),
    (4, 5), (4, 6), (5, 6), (4, 5)
]

vision = [
    2, 2,
    5, 3, 1, 1,
    1, 1, 1, 2, 5,
    2, 2, 3, 2,
    2, 3, 1, 5
]

gas = [
    99, 70,
    80, 70, 50, 99,
    70, 50, 50, 60, 50,
    99, 99, 99, 99,
    99, 99, 99, 60
]

targets = [
    'infantry', 'vehicle',
    'copter', 'plane',
    'ship', 'sub'
]

weapons = [
    # Ammo, range, (targets, efficient)
    # 0 Infantry M Gun
    (0, (1, 1),
        ((0, 1, 2), (1, 0, 0))
    ),
    # 1 Bazooka
    (3, (1, 1),
        ((1), (1))
    ),
    # 2 Tank Cannon
    (9, (1, 1),
        ((1, 4, 5), (1, 0, 0))
    ),
    # 3 Md Tank Cannon
    (8, (1, 1),
        ((1, 4, 5), (1, 0, 0))
    ),
    # 4 Neo Tank New Cannon
    (9, (1, 1),
        ((1, 4, 5), (1, 0, 0))
    ),
    # 5 Artillery Cannon
    (9, (2, 3),
        ((0, 1, 4, 5), (1, 1, 0, 0))
    ),
    # 6 Rockets
    (6, (3, 5),
        ((0, 1, 4, 5), (1, 1, 1, 1))
    ),
    # 7 Vulcan
    (9, (1, 1),
        ((0, 1, 2, 3), (1, 0, 1, 1))
    ),
    # 8 Missiles
    (6, (3, 5),
        ((2, 3), (1, 1))
    ),
    # 9 Fighter Missiles
    (9, (1, 1),
        ((2, 3), (1, 1))
    ),
    # 10 Bombs
    (9, (1, 1),
        ((0, 1, 2, 3), (1, 1, 1, 1))
    ),
    # 11 Copter Missiles
    (6, (1, 1),
        ((1, 4, 5), (1, 1, 1))
    ),
    # 12 Copter M Gun
    (0, (1, 1),
        ((0, 1, 2), (1, 0, 1))
    ),
    # 13 B Ship Cannon
    (9, (2, 6),
        ((0, 1, 4, 5), (1, 1, 1, 1))
    ),
    # 14 Cruiser Missiles
    (9, (1, 1),
        ((5), (1))
    ),
    # 15 A-Air Gun
    (0, (1, 1),
        ((2, 3), (1, 1))
    ),
    # 16 Torps
    (6, (1, 1),
        ((4, 5), (1, 1))
    )
]

weapons_units = [
    (None, 0), (1, 0),
    (None, 0), (2, 0), (3, 0), (4, 0), (None, None), (5, None), (6, None), (7, None), (8, None),
    (9, None), (10, None), (11, 12), (None, None),
    (13, None), (14, 15), (None, None), (16, None)
]

