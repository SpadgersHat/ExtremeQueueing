from copy import deepcopy
from random import randint, shuffle
from time import sleep
from teams import npcs

import abilities
import classes
import dictionaries


def ability(ability_type, teams, team_no, unit_pos, bits, tokens, when):
    abilities_whuu = {'take place': abilities.take_place,
                      'heal': abilities.heal,
                      'adjust': abilities.adjust,
                      'spit': abilities.spit,
                      'summon': abilities.summon}
    if ability_type == 'none':
        return teams, tokens
    else:
        return abilities_whuu[ability_type](teams, team_no, unit_pos, bits, tokens, when[0])


def is_it_arrowhead(x, digit, team):
    if x == 1:
        if digit == 0:
            if team == 1:
                return "\|/"
            else:
                return "/|\\"
        elif team == 0:
            return " ^ "
        else:
            return " V"
    else:
        return f" | "


def recruit(roster, code, level, UID):
    newbie = classes.Unit(dictionaries.units[code-1], level, UID)
    roster.append(newbie)


def level_up(unit):
    unit.level += 1


def load_into_team(squad, selections):
    team = []
    for x in selections:
        team.append(deepcopy(squad[x]))
    return team


def attack(health, damage):
    health -= damage
    return health


def attr_string(old, new, team_no, unit_pos, stat):
    for x in range(len(old)):
        for y in range(len(old[x])):
            if new[team_no][unit_pos].UID == old[x][y].UID:
                return find_change_string(old[x][y], new[team_no][unit_pos], stat)
    if stat == 'attack':
        return f"{new[team_no][unit_pos].attack}"
    else:
        return f"{new[team_no][unit_pos].health}"


def find_change_string(old, new, stat):
    if stat == 'attack':
        if old.attack == new.attack:
            return f"{new.attack}"
        else:
            return f"{str(old.attack)}->{new.attack}"
    else:
        if old.health == new.health:
            return f"{new.health}"
        else:
            return f"{str(old.health)}->{new.health}"


def calc_scores_space(old, new):
    return 68 - (len(attr_string(old, new, 1, 0, 'health')) +
                 len(attr_string(old, new, 0, 0, 'health')))


def act(teams, triggers, this_turn):
    new_teams = deepcopy(teams)
    tokens = []
    tokens = base_attacks(new_teams[0][0], new_teams[1][0], tokens)
    new_teams, tokens = find_whenevers(tokens, triggers, new_teams, ['action', this_turn])
    new_teams = run_abilities(new_teams, triggers, ['action', this_turn], tokens)
    return new_teams


def base_attacks(unit1, unit2, tokens):
    order = [unit1, unit2]
    unit1.health = attack(unit1.health, unit2.attack)
    unit2.health = attack(unit2.health, unit1.attack)
    for x in range(2):
        order[x].actions += f'Hits for {order[x].attack}HP. '
        order[x].this_turn['hit'] = True
        order[x].this_turn['been hit'] = True
        tokens.append(['hit', order[x]])
        tokens.append(['been hit', order[x]])
    return tokens


def remove_deaths(teams):
    new_teams = []
    for x in teams:
        team = thin_out_zeros(x)
        new_teams.append(team)
    return new_teams


def thin_out_zeros(team):
    return [unit for unit in team if unit.health > 0]


def create_die_string(unit):
    unit.actions = 'Dies. '
    # unit.actions = unit.actions.rstrip(unit.actions[-1])


def check_for_wins(teams):
    for x in teams:
        if len(x) == 0:
            return True


def end_match(teams):
    print('\nThe match is over!')
    if len(teams[0]) == 0:
        if len(teams[1]) == 0:
            draw()
        else:
            loss()
    else:
        win()


def win():
    print('You win!')


def loss():
    print('You lose...')


def draw():
    print("It's a draw...")


def progress(prompt, key):
    while True:
        answer = input(prompt)
        if answer == key:
            return
        else:
            print('Nope.')


def reset_actions(teams):
    for x in teams:
        for y in x:
            y.actions = ''


def clear_turn_data(teams):
    for x in teams:
        for y in x:
            for key, value in y.this_turn.items():
                y.this_turn[key] = False


def print_turn(teams, new_teams):
    for x in range(len(new_teams[1]) - 1):
        digit = len(new_teams[1]) - x - 1
        now = new_teams[1][digit]
        then = ''
        for y in teams[1]:
            if y.UID == now.UID:
                then = y
        if not then:
            then = now
        attack_string = find_change_string(then, now, 'attack')
        health_string = find_change_string(then, now, 'health')
        print(
            f"{' ' * (92 - (len(now.name) + len(attack_string) + len(health_string)))}"
            f"{now.name} - "
            f"{attack_string}|{health_string} "
            f"{is_it_arrowhead(digit, 0, 1)}\n"
            f"{' ' * (96 - len(now.actions))}{now.actions} {is_it_arrowhead(digit, 1, 1)}")
    print(f"{' ' * 6}{new_teams[0][0].name.upper()}"
          f"{' ' * (85 - len(new_teams[1][0].name + new_teams[0][0].name))}{new_teams[1][0].name.upper()}\n"
          f"{' ' * 10}{attr_string(teams, new_teams, 0, 0, 'attack')}  |  "
          f"{attr_string(teams, new_teams, 0, 0, 'health')}"
          f"{' ' * (calc_scores_space(teams, new_teams))}"
          f"{attr_string(teams, new_teams, 1, 0, 'attack')}  |  \
{attr_string(teams, new_teams, 1, 0, 'health')}\n"
          f"{' ' * 6}{new_teams[0][0].actions}\
{' ' * (86 - (len(new_teams[1][0].actions) + len(new_teams[0][0].actions)))}"
          f"{new_teams[1][0].actions}\n")
    for x in range(1, len(new_teams[0])):
        print(
            f'{is_it_arrowhead(x, 1, 0)} {new_teams[0][x].name} - \
{attr_string(teams, new_teams, 0, x, "attack")}|'
            f'{attr_string(teams, new_teams, 0, x, "health")}\n'
            f'{is_it_arrowhead(x, 0, 0)} {new_teams[0][x].actions}')


def run_abilities(teams, triggers, when, tokens):
    try_again = True
    while try_again:
        #print('trying another run')
        #print(teams[0][3].this_turn['spent'])
        try_again = False
        for x in range(max(len(teams[0]), len(teams[1]))):
            for y in range(2):
                try:
                    # On summon/death phase, adds 'dies' to the actions of any dead units.
                    if when[0] == 'summondeath' and teams[y][x].this_turn['died'] and len(teams[y][x].actions) == 0:
                        create_die_string(teams[y][x])
                    if univ_checks(teams, y, x, when):
                        if who_checks(teams, y, x, when):
                            if what_checks(teams, y, x, when):
                                #print('sending to ability')
                                teams, tokens = do_ability(teams, y, x, triggers, tokens, when, False)
                                #print('i came back')
                                #print(teams[0][3].this_turn['spent'])
                                try_again = True
                except IndexError:
                    pass
    return teams


def univ_checks(teams, y, x, when):
    # Only select triggers that occur on this phase
    try:
        if teams[y][x].ability_bits['trigger']['when']['phase'] == when[0]:
            # Only select triggers that work every turn or only work this turn
            if not teams[y][x].ability_bits['trigger']['when']['turn'] \
                    or teams[y][x].ability_bits['trigger']['when']['turn'] == when[1]:
                # Filter out units that have already used their ability this turn.
                if not teams[y][x].this_turn['spent']:
                    return True
    except TypeError:
        pass
    return False


def who_checks(teams, y, x, when):
    if not teams[y][x].ability_bits['trigger']['who']:
        return True
    if teams[y][x].ability_bits['trigger']['who']['type'] == 'self':
        # Filter out abilities that work on self but trigger in a different queue position.
        if teams[y][x].ability_bits['trigger']['who']['position']:
            if teams[y][x].ability_bits['trigger']['who']['position'] != x:
                return False
    return True


def what_checks(teams, y, x, when):
    # So far, no 'any' triggers use this function, but if they do it won't pass True here.
    if not teams[y][x].ability_bits['trigger']['what']:
        return True
    elif teams[y][x].ability_bits['trigger']['what'] == 'damaged':
        if teams[y][x].ability_bits['trigger']['who']['type'] == 'relative':
            target = teams[y + teams[y][x].ability_bits['trigger']['who']['team']] \
                [x + teams[y][x].ability_bits['trigger']['who']['position']]
            # Filter out any damage-triggered abilities where the relative pal isn't damaged.
            if target.health >= target.max_health:
                return False
            else:
                return True
        else:
            print("you're looking for damaged but in an absolute position.")
    # Returns true if the unit with a self ability has the trigger in this_turn
    elif teams[y][x].ability_bits['trigger']['who']['type'] == 'self' and \
            teams[y][x].this_turn[teams[y][x].ability_bits['trigger']['what']]:
        return True
    # Returns true if the unit in the intended position of an absolute ability has the trigger in this_turn
    elif teams[y][x].ability_bits['trigger']['who']['type'] == 'absolute' and \
            teams[y + teams[y][x].ability_bits['trigger']['who']['team']] \
                    [teams[y][x].ability_bits['trigger']['who']['position']].this_turn[teams[y] \
                    [x].ability_bits['trigger']['what']]:
        return True
    # Returns true if the unit in a relative position to the unit with an ability has the trigger in this_turn
    elif teams[y][x].ability_bits['trigger']['who']['type'] == 'relative' and \
            teams[y + teams[y][x].ability_bits['trigger']['who']['team']] \
                    [x + teams[y][x].ability_bits['trigger']['who']['position']].this_turn[teams[y] \
                    [x].ability_bits['trigger']['what']]:
        return True


def between_strings(teams):
    # Not being used, currently!
    strings = [[], []]
    for x in range(max(len(teams[0]), len(teams[1]))):
        for y in range(2):
            try:
                if len(teams[y][x].actions) > 0:
                    strings[y].append(teams[y][x].actions)
                else:
                    pass
            except IndexError:
                pass
    while len(strings[0]) != len(strings[1]):
        if len(strings[0]) < len(strings[1]):
            strings[0].append('')
        else:
            strings[1].append('')
    for x in range(len(strings[0])):
        print(strings[0][x])
        print(f"{' ' * (100 - len(strings[1][x]))}{strings[1][x]}")


def check_for_triggers(tokens, triggers):
    for x in triggers:
        for z in tokens:
            if x in z[0]:
                return z


def whenever(teams, triggers, trigger, tokens, when):
    new_tokens = []
    for x in range(2):
        for y in range(len(teams[x])):
            if teams[x][y].health > 0:
                if teams[x][y].ability_bits['trigger']:
                    if teams[x][y].ability_bits['trigger']['when']['phase'] == 'whenever':
                        try:
                            if teams[x][y].ability_bits['trigger']['what'] in trigger[0]:
                                #print('i got through the first barrier for')
                                #print(teams[x][y].name)
                                if teams[x][y].ability_bits['trigger']['who']['type'] == 'self':
                                    for z in tokens:
                                        # If you're in the triggers list and if you've triggered your own ability.
                                        if z[1].UID == teams[x][y].UID and z[0] == trigger[0]:
                                            if teams[x][y].ability_bits['trigger']['who']['position']:
                                                # For Minki, Checks if you're in the right position to trigger.
                                                if teams[x][y].ability_bits['trigger']['who']['position'] != y:
                                                    pass
                                            teams[x][y].this_turn['spent'] = False
                                            #print('Im about to do an ability for' + teams[x][y])
                                            teams, temp_tokens = do_ability(teams, x, y, triggers, tokens, when, True)
                                            for token in temp_tokens:
                                                new_tokens.append(token)
                                        else:
                                            pass
                                elif teams[x][y].ability_bits['trigger']['who']['type'] == 'any':
                                    # Filters out abilities triggered by members of the wrong triggering team.
                                    if teams[x][y].ability_bits['trigger']['who']['team'] != '' and \
                                            (trigger[1] not in teams[x + teams[x][y].ability_bits['trigger']['who']['team']]):
                                        # I think this is triggering any on the wrong team help
                                        pass
                                    else:
                                        teams[x][y].this_turn['spent'] = False
                                        #print('Im about to do an ability 2 for' + teams[x][y])
                                        teams, temp_tokens = do_ability(teams, x, y, triggers, tokens, when, True)
                                        for token in temp_tokens:
                                            new_tokens.append(token)
                                elif teams[x][y].ability_bits['trigger']['who']['type'] == 'relative':
                                    pass
                                    # There aren't any whenever abilities triggered by relative position yet, but there might be.
                        except TypeError:
                            #print('i got here')
                            pass
    #print('i left whenever')
    return teams, new_tokens


def do_ability(teams, team_index, unit_index, triggers, tokens, when, send_back):
    #print('doing ability for' + teams[team_index][unit_index].name)
    if not teams[team_index][unit_index].this_turn['spent']:
        #print('not spent')
        yer_man = teams[team_index][unit_index]
        #print(yer_man.name)
        teams, new_tokens = ability(teams[team_index][unit_index].ability_bits['response']
                                    ['what'], teams, team_index, unit_index,
                                    teams[team_index][unit_index].ability_bits, tokens,
                                    when)
        yer_man.this_turn['spent'] = True
        #print(new_tokens)
        teams, new_tokens = find_whenevers(new_tokens, triggers, teams, when)
    else:
        #Hey, listen, this is just because otherwise the earlier if does nothing. Is it all redundant? Who knows.
        new_tokens = tokens
    #print('i returned from do ability')
    return teams, new_tokens


def find_whenevers(new_tokens, triggers, teams, when):
    while len(new_tokens) > 0:
        if check_for_triggers(new_tokens, triggers):
            trigger = check_for_triggers(new_tokens, triggers)
            use_tokens = [token for token in new_tokens if token[0] == trigger[0]]
            new_tokens = [token for token in new_tokens if token[0] != trigger[0]]
            teams, newer_tokens = whenever(teams, triggers, trigger, use_tokens, when)
            for x in newer_tokens:
                new_tokens.append(x)
        else:
            break
    return teams, new_tokens


def fill_teams(teams):
    UID = 0
    squads = [[], []]
    for x in range(2):
        for y in range(5):
            UID += 1
            recruit(squads[x], teams[x][y][0], randint(1, 3), UID)
    return squads


def find_triggers(teams):
    triggers = []
    for x in range(len(teams)):
        for y in teams[x]:
            try:
                if y.ability_bits['trigger']['when']['phase'] == 'whenever':
                    triggers.append(y.ability_bits['trigger']['what'])
            except IndexError:
                pass
            except TypeError:
                pass
    return triggers


def no_news(teams):
    for x in teams:
        for y in x:
            if len(y.actions) > 0:
                return False
    return True


def make_negative_health_zero(teams):
    for x in teams:
        for y in x:
            if y.health < 0:
                y.health = 0


def match(team_inputs):
    teams = fill_teams([team_inputs[1], team_inputs[3]])
    this_turn = 1
    triggers = find_triggers(teams)
    phases = ['summondeath', 'action', 'summondeath', 'between', 'summondeath']
    while True:
        for x in range(5):
            phase = phases[x]
            phase_strings = ['P R E - M A T C H   B E W R A N G L E M E N T S',
                             'A C T I O N   P H A S E', 'S U M M O N / D E A T H   A L E R T',
                             'B E T W E E N   T U R N S', 'S U M M O N / D E A T H   A L E R T']
            reset_actions(teams)
            old_teams = deepcopy(teams)
            if phase == 'action':
                new_teams = act(teams, triggers, this_turn)
            else:
                new_teams = run_abilities(teams, triggers, [phase, this_turn], [])
            make_negative_health_zero(new_teams)
            abilities.update_deaths(new_teams)
            if (x != 1) and no_news(new_teams):
                pass
            else:
                print(f'\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nT U R N   {this_turn}:\n')
                print(f'                    --> {phase_strings[x]} <--\n')
                print_turn(old_teams, new_teams)
                progress('\n- Progress (Enter)\n', '')
            if phase == 'summondeath':
                new_teams = remove_deaths(new_teams)
                triggers = find_triggers(new_teams)
                if check_for_wins(new_teams):
                    end_match(new_teams)
                    sleep(1)
                    return
            teams = deepcopy(new_teams)
        clear_turn_data(teams)
        this_turn += 1

