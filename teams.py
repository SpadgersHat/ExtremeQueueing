from dictionaries import units
from random import randint

npcs = {'Spitters': [[8, 1], [15, 1], [22, 1], [17, 1], [21,1]],
        'Shifters': [[0,1], [10,1], [5,1], [37,1], [7,1]],
        'Heal Everyone': [[1,1], [0,1], [36,1], [38,1], [5,1]],
        'Summoners': [[34,1], [35,1], [33,1], [39,1], [40,1]],
        'Bomb': [[42,1], [22,1], [21,1], [43,1], [17,1]],
        'random': [[randint(0, len(units)), 1] for x in range(5)]}