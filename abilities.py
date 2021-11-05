from copy import deepcopy
import classes, dictionaries

move_strings = {-1: 'forward a spot',
                1: 'back a spot',
                999: 'to the back',
                0: 'to the front'}

def take_place(teams, team_no, unit_pos, bits, tokens, when):
    # Shuffles the pal(s) in position bits[2] back to the position in the
    # list bits[3]. Moves all others forward.
    new_tokens = []
    targets = create_targets(teams, team_no, unit_pos, bits['response'], tokens)
    old_spots = deepcopy(teams)
    #trigger_strings = {'': '',
                       #'hit': ' after attacking',
                       #'been hit': ' after being attacked'}
    if len(teams[team_no]) > 1:
        for x in targets:
            for y in range(2):
                for z in range(len(teams[y])):
                    if teams[y][z].UID == x.UID:
                        # Eliminating times where a relative movement (such as forward from the front) isn't possible.
                        if bits['response']['where']['type'] == 'relative' and \
                                ((z == 0 and bits['response']['where']['position'] < 0) or
                                 (teams[y][z] == teams[y][-1] and bits['response']['where']['position'] > 0)):
                            pass
                        else:
                            teams[y].pop(z)
                            if bits['response']['where']['type'] == 'absolute':
                                teams[y].insert(bits['response']['where']['position'], x)
                            elif bits['response']['where']['type'] == 'relative':
                                teams[y].insert(z + bits['response']['where']['position'], x)
                            x.actions += f"Shuffled {move_strings[bits['response']['where']['position']]}."
                            break
    for x in range(2):
        for y in range(max(len(teams[0]), len(teams[1]))):
            for z in range(len(old_spots[x])):
                try:
                    if teams[x][y].UID == old_spots[x][z].UID:
                        if y > z:
                            if teams[x][y] in targets:
                                new_tokens.append(['move back', teams[x][y]])
                        elif z > y:
                            if teams[x][y] in targets:
                                new_tokens.append(['move forward', teams[x][y]])
                        else:
                            pass
                except IndexError:
                    pass
    return teams, new_tokens


def heal(teams, team_no, unit_pos, bits, tokens, when):
    new_tokens = []
    # The unit heals units in targets by an ['increment'], or as much as is possible to achieve max health.
    targets = create_targets(teams, team_no, unit_pos, bits['response'], tokens)
    heal_strings = [f"for {bits['response']['how']['increment']}HP", 'to full health']
    try:
        for x in targets:
            if not ((x.health == x.max_health) or x.health <= 0):
                if bits['response']['who']['position']:
                    if not (unit_pos == 0 and bits['response']['who']['position'] < 0):
                        x.health += bits['response']['how']['increment']
                else:
                    x.health += bits['response']['how']['increment']
                if x.health >= x.max_health:
                    x.health = x.max_health
                    heal_string_choice = 1
                else:
                    heal_string_choice = 0
                teams[team_no][unit_pos].actions += \
                    f'Healed {x.name} {heal_strings[heal_string_choice]}. '
                x.actions += f'Healed {heal_strings[heal_string_choice]}. '
                # This token shows that healing has taken place, the position of the healer and the position of the unit healed.
                new_tokens.append(['heal', teams[team_no][unit_pos]])
                new_tokens.append(['healed', x])
    except IndexError:
        pass
    return teams, new_tokens


def adjust(teams, team_no, unit_pos, bits, tokens, when):
    new_tokens = []
    string_names = {'plus': ['boosted', 'boost', 'boosts', 'by'],
                    'minus': ['reduced', 'reduce', 'reduces', 'by'],
                    'divide': ['divided', 'divide', 'divides', 'by'],
                    'multiply': ['multiplied', 'multiply', 'multiplies', 'by'],
                    'become': ['changed', 'change', 'changes', 'to']}
    # Operates on the stat in ['stat'] by operation ['type'] by an ['increment'] to all valid targets.
    targets = create_targets(teams, team_no, unit_pos, bits['response'], tokens)
    for x in targets:
        if bits['response']['how']['stat'] == 'attack':
            x.attack = operate(x.attack, bits['response']['how']['type'], bits['response']['how']['increment'])
        elif bits['response']['how']['stat'] == 'health':
            x.health = operate(x.health, bits['response']['how']['type'], bits['response']['how']['increment'])
            x.max_health = operate(x.max_health, bits['response']['how']['type'], bits['response']['how']['increment'])
        elif bits['response']['how']['stat'] == 'both':
            x.attack = operate(x.attack, bits['response']['how']['type'], bits['response']['how']['increment'][0])
            x.health = operate(x.health, bits['response']['how']['type'], bits['response']['how']['increment'][1])
            x.max_health = operate(x.max_health, bits['response']['how']['type'],
                                   bits['response']['how']['increment'][1])
        if bits['response']['how']['stat'] == 'both':
            stats = ['attack', 'health']
        else:
            stats = [bits['response']['how']['stat']]
        for y in stats:
            new_tokens.append([y + string_names[bits['response']['how']['type']][0], x])
        new_tokens.append([string_names[bits['response']['how']['type']][1], teams[team_no][unit_pos]])
        if x.UID != teams[team_no][unit_pos].UID:
            if len(stats) == 1:
                x.actions += f" {stats[0].capitalize()} " \
                             f"{string_names[bits['response']['how']['type']][2]} \
{string_names[bits['response']['how']['type']][3]} {bits['response']['how']['increment']}. "
                teams[team_no][unit_pos].actions += f"{string_names[bits['response']['how']['type']][2].capitalize()} \
{x.name}'s {stats[0]}. "
            else:
                x.actions += f"Attack and health {string_names[bits['response']['how']['type']][0]} \
{string_names[bits['response']['how']['type']][3]} {bits['response']['how']['increment'][0]}|" \
f"{bits['response']['how']['increment'][1]}. "
                teams[team_no][unit_pos].actions += f"{string_names[bits['response']['how']['type']][2].capitalize()} \
{x.name}'s {stats[0]} and {stats[1]}. "
        else:
            if len(stats) == 1:
                teams[team_no][unit_pos].actions += f"{string_names[bits['response']['how']['type']][2].capitalize()} \
own {stats[0]} {string_names[bits['response']['how']['type']][3]} {bits['response']['how']['increment']}. "
            else:
                teams[team_no][unit_pos].actions += f"{string_names[bits['response']['how']['type']][2].capitalize()} \
own attack and health {string_names[bits['response']['how']['type']][3]} {bits['response']['how']['increment'][0]}|\
 {bits['response']['how']['increment'][1]}. "
    return teams, new_tokens


def operate(stat, operation, increment):
    if operation == 'plus':
        return int(stat + increment)
    elif operation == 'minus':
        return int(stat - increment)
    elif operation == 'multiply':
        return int(stat * increment)
    elif operation == 'divide':
        #ROUND UP!
        return int(stat / increment)
    elif operation == 'become':
        return increment


def spit(teams, team_no, unit_pos, bits, tokens, when):
    new_tokens = []
    targets = create_targets(teams, team_no, unit_pos, bits['response'], tokens)
    if bits['response']['how']['once'] and teams[team_no][unit_pos].this_turn['spit']:
        return teams, new_tokens
    if not targets:
        return teams, new_tokens
    for x in targets:
        x.health -= bits['response']['how']['increment']
        new_tokens.append(['been hit', x])
        new_tokens.append(['spat at', x])
        x.this_turn['been hit'] = True
        new_tokens.append(['hit', teams[team_no][unit_pos]])
        new_tokens.append(['spit', teams[team_no][unit_pos]])
        teams[team_no][unit_pos].this_turn['hit'] = True
        teams[team_no][unit_pos].this_turn['spit'] = True
        teams[team_no][unit_pos].actions += \
            f"Spits at {x.name}. "
        if bits['response']['how']['increment'] > 1:
            teams[team_no][unit_pos].actions = teams[team_no][unit_pos].actions.rstrip('. ')
            teams[team_no][unit_pos].actions += f" {bits['response']['how']['increment']} times. "
    return teams, new_tokens


def summon(teams, team_no, unit_pos, bits, tokens, when):
    new_tokens = []
    UID = find_new_UID(teams)
    if bits['response']['how']['type'] == 'relative':
        if not ((bits['response']['how']['position'] < 0 and teams[team_no][unit_pos] == 0) or
                (bits['response']['how']['position'] > 0 and teams[team_no][unit_pos] == len(teams[team_no]))):
            for x in dictionaries.units:
                if dictionaries.units[x]['name'] == teams[team_no + bits['response']['how']['team']]\
                        [unit_pos + bits['response']['how']['position']].name:
                    try:
                        newbie = classes.Unit(dictionaries.units[x], bits['response']['how']['level'], UID)
                    except IndexError:
                        return teams, new_tokens
    elif bits['response']['how']['type'] == 'code':
        newbie = classes.Unit(dictionaries.summons[bits['response']['how']['code']], bits['response']['how']['level'],
                              UID)
    teams[team_no][unit_pos].actions += f"Summons {newbie.name} " \
                                        f"{move_strings[bits['response']['who']['position']]} of the queue. "
    if bits['response']['who']['type'] == 'absolute':
        teams[team_no + bits['response']['who']['team']].insert(bits['response']['who']['position'], newbie)
    elif bits['response']['who']['type'] == 'relative':
        teams[team_no + bits['response']['who']['team']].insert(unit_pos + bits['response']['who']['position'], newbie)
    new_tokens.append(['summoned', newbie])
    new_tokens.append(['summon', teams[team_no][unit_pos]])
    newbie.actions += 'Joins the queue. '
    return teams, new_tokens


def find_new_UID(teams):
    used_digits = []
    for x in range(len(teams)):
        for y in teams[x]:
            if y.UID < 0:
                used_digits.append(y.UID)
    UID = -1
    while True:
        if UID in used_digits:
            UID -= 1
        else: return UID


def create_targets(teams, team_no, unit_pos, response, tokens):
    try:
        if response['who']['type'] == 'relative':
            return [teams[team_no + response['who']['team']][unit_pos + response['who']['position']]]
        elif response['who']['type'] == 'absolute':
            return [teams[team_no + response['who']['team']][response['who']['position']]]
    except IndexError:
        return
    if response['who']['type'] == 'self':
        return [teams[team_no][unit_pos]]
    elif response['who']['type'] == 'locate':
        # find the stat and judgment specified and return the bloke.
        return [find_most(teams[team_no + response['who']['team']], response)]
    elif response['who']['type'] == 'any':
        targets = []
        for x in tokens:
            if response['who']['team'] == 'any':
                for y in range(2):
                    if (x[0] != response['who']['action']) or x[1] not in teams[team_no - y]:
                        pass
                    else:
                        targets.append(x[1])
            else:
                if (x[0] != response['who']['action']) or x[1] not in teams[team_no + response['who']['team']]:
                    pass
                else:
                    targets.append(x[1])
        print('targets')
        print(targets)
        return targets
    elif response['who']['type'] == 'all':
        return teams[team_no + response['who']['team']]


def find_most(team, response):
    if response['who']['stat'] == 'health':
        compare_list = [[x for x in team], [x.health for x in team]]
    elif response['who']['stat'] == 'attack':
        compare_list = [[x for x in team], [x.attack for x in team]]
    for x in range(len(compare_list[1])):
        if response['who']['rule'] == 'min':
            if compare_list[1][x] == min(compare_list[1]):
                return compare_list[0][x]
        elif response['who']['rule'] == 'max':
            if compare_list[1][x] == max(compare_list[1]):
                return compare_list[0][x]


def update_deaths(teams):
    for x in teams:
        for y in x:
            if y.health == 0:
                y.this_turn['died'] = True
