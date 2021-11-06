class Unit:
    def __init__(self, stats, level, UID):
        rarity_levels = {'dry': 9,
                         'moist': 19,
                         'juicy': 29,
                         'gushing': 39,
                         'summon': 1}
        self.UID = UID
        self.name = stats['name']
        self.rarity = [stats['rarity']]
        self.level = level
        self.base_attack = stats['attack']
        self.attack = calc_levelled_stat(self.base_attack, self.level, self.rarity)
        self.base_max_health = stats['max health']
        self.max_health = calc_levelled_stat(self.base_max_health, self.level, self.rarity)
        self.health = self.max_health
        self.ability_bits = stats['ability']
        self.level_max = rarity_levels[self.rarity]
        self.actions = ''
        self.this_turn = {'spent': False,
                          'hit': False,
                          'been hit': False,
                          'spit': False,
                          'damaged': False,
                          'move forward': False,
                          'move back': False,
                          'died': False,
                          'summon': False,
                          'summoned': True
                          }


def calc_levelled_stat(base_stat, level, rarity):
    multipliers = {'dry': 4,
                   'moist': 3,
                   'juicy': 2,
                   'gushing': 1}
    return int(base_stat * (level - 1) / multipliers[rarity] + base_stat)


class Team:
    def __init__(self, name):
        self.name = name
        self.roster = [[] for x in range(5)]
        self.selected = False
        self.ready = False
