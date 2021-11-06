from matchrunner import match
from dictionaries import units
from random import randint
from time import sleep
from classes import Team, calc_levelled_stat
from copy import deepcopy
from teams import npcs


def new_collection():
    collection = []
    for unit in range(len(units)):
        collection.append({'number': make_number_string(unit + 1),
                           'code': units[unit]['code'],
                           'name': units[unit]['name'],
                           'level': 0,
                           'rarity': units[unit]['rarity'],
                           'ability': units[unit]['ability']['string'],
                           'base stats': [units[unit]['attack'], units[unit]['max health']],
                           'selected': False})
    return collection


def make_number_string(number):
    string = '#'
    for x in range(3 - len(str(number))):
        string += '0'
    string += str(number)
    return string


def print_collection(collection):
    print(
        f'\n\nYour Collection:\n\nPals collected: {count_cards("all", True, collection)}/{count_cards("all", False, collection)}')
    print(f' Dry: {count_cards("dry", True, collection)}/{count_cards("dry", False, collection)}\n'
          f' Moist: {count_cards("moist", True, collection)}/{count_cards("moist", False, collection)}\n'
          f' Juicy: {count_cards("juicy", True, collection)}/{count_cards("juicy", False, collection)}\n'
          f' Gushing: {count_cards("gushing", True, collection)}/{count_cards("gushing", False, collection)}\n\n')
    answer = input('- See all pals (a)\n- See owned pals only (o)\n')
    while True:
        if answer == 'a':
            list_collection(False, False, collection)
            break
        elif answer == 'o':
            list_collection(True, False, collection)
            break
        else:
            print("That wasn't one of the options.")


def list_collection(owned, available, collection):
    if owned:
        if available:
            edited_collection = [x for x in collection if (x['level'] > 0 and not x['selected'])]
        else:
            edited_collection = [x for x in collection if x['level'] > 0]
        if len(edited_collection) == 0:
            if available:
                print("Oh no! You don't have any pals that aren't already in teams!")
            else:
                print("You don't have any pals yet!")
            return
    else:
        edited_collection = collection
    count = 0
    printed_count = 0
    choice = False
    while True:
        if printed_count == 10:
            if count == 10:
                count, printed_count, choice = move_options('left', count, available, collection)
            elif count == len(edited_collection):
                count, printed_count, choice = move_options('right', count, available, collection)
            else:
                count, printed_count, choice = move_options('both', count, available, collection)
        if (count == -100) or choice:
            return choice
        elif count < 1:
            count = 0
        try:
            if edited_collection[count]['level'] == 0:
                print(f'{edited_collection[count]["number"]}: ???\n\n')
                count += 1
                printed_count += 1
            else:
                print_pal(edited_collection[count])
                count += 1
                printed_count += 1
        except IndexError:
            if len(collection) > 10:
                count, printed_count, choice = move_options('right', count, available, collection)
            else:
                count, printed_count, choice = move_options('neither', count, available, collection)
                print(choice)
            if (count == -100) or choice:
                return choice


def print_pal(pal):
    current_stats = [calc_levelled_stat(pal["base stats"][0], pal["level"], pal["rarity"]),
                     calc_levelled_stat(pal["base stats"][1], pal["level"], pal["rarity"])]
    print(f'{pal["number"]}: {pal["name"]} '
          f'({capitalise(pal["rarity"])}, lvl.{pal["level"]})\n'
          f'      {current_stats[0]} | {current_stats[1]}    {pal["ability"]}\n')


def move_options(limit, count, available, collection):
    print('\n')
    while True:
        if available:
            print('- Select pal (enter their #)')
        if limit == 'left' or limit == 'both':
            print('- Next page (n)')
        if limit == 'both' or limit == 'right':
            print('- Previous page (p)')
        print('- Back to menu (b)')
        answer = input('\n')
        if answer == 'n' and (limit == 'left' or limit == 'both'):
            return count, 0, False
        elif answer == 'p' and (limit == 'both' or limit == 'right'):
            return count - 20, 0, False
        elif answer == 'b':
            return -100, 0, False
        elif available:
            formatted_answer = trim_to_number(answer)
            if formatted_answer:
                availables = [x for x in range(len(collection)) if
                              (not collection[x]['selected'] and collection[x]['level'] > 0)]
                if trim_to_number(answer)-1 in availables:
                    return 0, 0, formatted_answer
                else:
                    print('Not available')
            else:
                print('No.')

        else:
            print('Nope.')


def trim_to_number(string):
    new_string = ''
    digits = [str(x) for x in range(0, 10)]
    for x in string:
        if x in digits:
            new_string += x
    while new_string[0] == '0' and len(new_string) > 1:
        newer_string = ''
        for x in range(len(new_string)):
            if x == 0:
                pass
            else:
                newer_string += new_string[x]
        new_string = newer_string
    if new_string:
        return int(new_string)
    else:
        return False


def count_cards(what, collected, collection):
    count = 0
    for x in collection:
        if what == 'all':
            if collected:
                if x['level'] > 0:
                    count += 1
            else:
                count += 1
        else:
            if x['rarity'] == what:
                if collected:
                    if x['level'] > 0:
                        count += 1
                else:
                    count += 1
    return count


def capitalise(string):
    new_string = ''
    for x in range(len(string)):
        if x == 0:
            new_string += string[x].upper()
        else:
            new_string += string[x]
    return new_string


def open_pack(collection):
    pack = make_pack()
    for x in pack:
        collection[x]['level'] += 1
        if collection[x]['level'] == 1:
            print(f'Got {units[x]["name"]} ({capitalise(units[x]["rarity"])})! *NEW!*')
        else:
            print(
                f'Got {units[x]["name"]} ({capitalise(units[x]["rarity"])})! Bumped up to lvl.{collection[x]["level"]}')
    while True:
        answer = input('\n- Add to collection (press enter)')
        if answer == '':
            break
    return collection


def make_pack():
    dries = [x for x in range(len(units)) if units[x]['rarity'] == 'dry']
    moists = [x for x in range(len(units)) if units[x]['rarity'] == 'moist']
    juicies = [x for x in range(len(units)) if units[x]['rarity'] == 'juicy']
    gushings = [x for x in range(len(units)) if units[x]['rarity'] == 'gushing']
    pack = []
    # 4 dry cards
    for x in range(4):
        pack.append(dries[randint(0, len(dries) - 1)])
    # 1 dry or moist
    choice = randint(0, 1)
    if choice == 1:
        pack.append(moists[randint(0, len(moists) - 1)])
    else:
        pack.append(dries[randint(0, len(dries) - 1)])
    # 1 moist or juicy
    choice = randint(0, 5)
    if choice == 5:
        pack.append(juicies[randint(0, len(juicies) - 1)])
    else:
        pack.append(moists[randint(0, len(moists) - 1)])
    # 1 moist, juicy or gushing
    choice = randint(0, 5)
    if choice == 5:
        pack.append(gushings[randint(0, len(gushings) - 1)])
    elif choice > 1:
        pack.append(juicies[randint(0, len(juicies) - 1)])
    else:
        pack.append(moists[randint(0, len(moists) - 1)])
    return pack


def manage_teams(teams, collection):
    while True:
        print('\nHere are your teams:\n')
        for x in range(5):
            print(f'{x + 1}: {teams[x].name}')
        answer = input('\n- Select a team to view/edit its roster.\n- Back to menu (b)\n')
        if answer in [str(x) for x in range(1, 6)]:
            teams[int(answer) - 1] = display_team(teams[int(answer) - 1], collection)
        elif answer == 'b':
            return teams
        else:
            print("That isn't a valid team.")


def display_team(team, collection):
    if len(team.roster) == [[] for x in range(5)]:
        print("This team's empty, currently.")
    else:
        print_roster(team.name, team.roster)
    while True:
        answer = input(f"\nWhat would you like to do with {team.name}?\n\n- Edit roster (e)\n- Rename team (r)\n- "
                       f"Wipe team (w)\n- Back to menu (b)\n")
        if answer == 'e':
            team = edit_roster(team, collection)
        elif answer == 'r':
            team.name = rename_team()
        elif answer == 'w':
            team = wipe_team(team)
        elif answer == 'b':
            return team
        else:
            print('Try again.')


def print_roster(name, roster):
    print(f"Here's the roster for {name}:\n")
    for x in range(5):
        if not roster[x]:
            print(f'{x + 1}. Empty\n')
        else:
            print_pal(roster[x])


def edit_roster(team, collection):
    new_roster = deepcopy(team.roster)
    while True:
        print(f'Editing the roster for {team.name}.\n{filled_spots(new_roster)}/5 positions filled.\n')
        print_roster(team.name, new_roster)
        print('\n')
        if filled_spots(new_roster) > 0:
            print('- Remove a pal (r)')
        if filled_spots(new_roster) < 5:
            print('- Add a pal (a)')
        print('- Back to menu without saving team (b)')
        if filled_spots(new_roster) == 5:
            print('- Confirm team (c)')
        answer = input('\n')
        if answer == 'r':
            new_roster = remove_pal(new_roster)
        elif answer == 'a':
            new_roster, collection = add_pal(team, new_roster, collection)
        elif answer == 'b':
            return team
        elif answer == 'c':
            team.roster = new_roster
            team.ready = True
            return team


def filled_spots(roster):
    count = 0
    for x in roster:
        if x:
            count += 1
    return count


def remove_pal(roster):
    while True:
        answer = input('- Remove a pal from the team (enter position number)\n- Back (b)\n')
        if answer in [str(x) for x in range(1, 6)]:
            if roster[int(answer) - 1]:
                print(f'Booted {roster[int(answer) - 1]["name"]} from the team.\n')
                roster[int(answer) - 1]['selected'] = False
                roster[int(answer) - 1] = []
            else:
                print("There's nobody in that slot.")
        elif answer == 'b':
            return roster
        else:
            print("No, that's not a thing.")


def add_pal(team, roster, collection):
    while True:
        print("Let's find some pals to add to your team...")
        choice = list_collection(True, True, collection)
        if choice:
            position = pick_position(roster, collection, choice-1, team)
            if position:
                roster[position - 1] = collection[choice-1]
                # What if the name changes
                collection[choice]['selected'] = team.name
                print(f"Adding {collection[choice-1]['name']} to your team.")
        while True:
            answer = input('- Add another (a)\n- Back (b)\n')
            if answer == 'a':
                break
            elif answer == 'b':
                return roster, collection


def pick_position(roster, collection, choice, team):
    print_roster(team.name, roster)
    print(f"\nIn what position will you place {collection[choice]['name']}?")
    availables = [str(x) for x in range(1, 6)]
    while True:
        answer = input('- Your choice (type a position number)\n')
        if answer in availables:
            if roster[int(answer) - 1]:
                while True:
                    answer2 = input(f'{roster[int(answer) - 1]["name"]} is already in that spot.\n'
                                    f'Do you want to replace them?\n- Replace (r)\n- Back (b)\n')
                    if answer2 == 'r':
                        roster[int(answer) - 1]['selected'] = False
                        return int(answer)
                    elif answer2 == 'b':
                        break
            else:
                return int(answer)
        else:
            print("That isn't a position in the team.")


def rename_team():
    while True:
        answer = input('What name would you like to give to this team?\n')
        print(f'Are you sure you want to call this team {answer}? (y/n)')
        while True:
            answer2 = input('\n')
            if answer2 == 'y':
                print(f'Great. {answer} it is.\nReturning to team')
                return answer
            elif answer2 == 'n':
                break
            else:
                print("This one's a closed question.")


def wipe_team(team):
    print('Wiping a team will clear its name and roster, and the pals will be available for selection on your other '
          'teams.\n Are you sure you want to wipe this team? (y/n)')
    while True:
        answer = input('\n')
        if answer == 'y':
            team.name = 'New Team'
            for x in team.roster:
                x['selected'] = False
            team.roster = []
            team.ready = False
            print('Team cleared!\nReturning to menu...')
            return team
        elif answer == 'n':
            print('Returning to menu...')
            return team
        else:
            print('No.')


def setup_match(teams):
    opponent = choose_opponent()
    team = choose_team(teams)
    if not team:
        [print('I returned!')]
        return
    match([teams[team-1].name, flatten_team(teams[team-1]), opponent, npcs[opponent]])


def choose_opponent():
    while True:
        answer = input('\nWho would you like to face?\n1. Spitters\n2. Shifters\n3. Healers\n'
                       '4. Summoners\n5. Bomb\n6. Random Team\n')
        if answer == '1':
            return 'Spitters'
        elif answer == '2':
            return 'Shifters'
        elif answer == '3':
            return 'Heal Everyone'
        elif answer == '4':
            return 'Summoners'
        elif answer == '5':
            return 'Bomb'
        elif answer == '6':
            return 'random'
        else:
            print('Try another number, Ike.')


def choose_team(teams):
    if count_valid_teams(teams) == 0:
        print('You have no confirmed teams! Go back and manage your teams before heading into a fight.')
        return False
    while True:
        print('Here are your teams:')
        for x in range(5):
            if teams[x].ready:
                print(f'{x + 1}: {teams[x].name}')
        answer = input('\nWhich of your teams do you want to send to compete?\n')
        if answer in [str(x + 1) for x in range(len(teams)) if teams[x].ready]:
            return int(answer)
        else:
            print("That's not a valid team.")


def count_valid_teams(teams):
    count = 0
    for x in teams:
        if x.ready:
            count += 1
    return count


def flatten_team(team):
    flat_team = []
    for x in team.roster:
        flat_team.append([x['code'], x['level']])
    return flat_team


def autofill(team, collection):
    for x in range(5):
        team.roster[x] = collection[randint(0, len(collection)-1)]
    print(team.roster)
    team.name = 'Autofill Team'
    team.ready = True
    print("There's a random team ready for you in slot 1.")
    return team


def new_game():
    print('New game! You have a fresh, empty collection.\n')
    collection = new_collection()
    teams = [Team('New Team') for x in range(5)]
    while True:
        answer = input('- View your pal collection (v)\n- Open a pack (o)\n- Manage teams (m)\n'
                       '- Autofill a team (a)\n- Fight! (f)\n')
        if answer == 'o':
            collection = open_pack(collection)
        elif answer == 'm':
            teams = manage_teams(teams, collection)
        elif answer == 'v':
            print_collection(collection)
        elif answer == 'a':
            teams[0] = autofill(teams[0], collection)
        elif answer == 'f':
            setup_match(teams)
        else:
            print("That's not an option.")


new_game()


# Change either of these team names to anything in the 'teams' file. You can add new teams on the 'teams' file and play
# them here, or just write 'random' (lower case) to make a random team play in either position.
# match(['Bomb', 'Heal Everyone'])
