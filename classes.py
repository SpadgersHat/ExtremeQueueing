class Unit:
    def __init__(self, stats, level, UID):
        rarity_levels = {'dry': 9,
                         'moist': 19,
                         'juicy': 29,
                         'gushing': 39,
                         'summon': 1}
        self.UID = UID
        self.name = stats['name']
        self.attack = stats['attack']
        self.health = stats['max health']
        self.max_health = stats['max health']
        self.ability_bits = stats['ability']
        self.level = level
        self.level_max = rarity_levels[stats['rarity']]
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