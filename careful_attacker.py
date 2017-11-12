# Let's start by importing the Halite Starter Kit so we can interface with the Halite engine
import hlt
# Then let's import the logging module so we can print out information
import logging
from operator import attrgetter

# GAME START
# Here we define the bot's name as Settler and initialize the game, including communication with the Halite engine.
game = hlt.Game("CarefulAttackerV2")
# Then we print our start message to the logs
logging.info("Starting my Settler bot!")


def get_ship_command(ship, ships_len, planets_to_be_attacked, my_ship_ids, my_planets, turn):
    if ship.docking_status != ship.DockingStatus.UNDOCKED:
        # Skip this ship
        return None, None

    entities_by_distance = game_map.nearby_entities_by_distance(ship)
    sorted_list = sorted(
        entities_by_distance.items(), key=lambda value: value[0])
    _planets = []
    for element in sorted_list:
        for el in element[1]:
            if isinstance(el, hlt.entity.Planet):
                _planets.append(el)
    enemy_planet = None
    biggest_closes_planet = None
    my_planet = None
    if _planets:
        closest_planet = _planets[0]
        if closest_planet in my_planets and not closest_planet.is_full() and turn > 70:
            my_planet = closest_planet
        else:
            non_taken_planets = [planet for planet in _planets if not planet.is_owned()]
            three_closest_planets = non_taken_planets[:4]
            if three_closest_planets:
                biggest_closes_planet = max(three_closest_planets, key=attrgetter('radius'))
            else:
                enemy_planets = [planet for planet in _planets if planet not in my_planets][:3]
                if enemy_planets:
                    enemy_planet = min(enemy_planets, key=lambda x: len(x.all_docked_ships()))
    else:
        return None, None
    if biggest_closes_planet:
        if ship.can_dock(biggest_closes_planet):
            return ship.dock(biggest_closes_planet), None
        else:
            return ship.navigate(
                ship.closest_point_to(biggest_closes_planet),
                # non_taken_planet,
                game_map,
                speed=int(hlt.constants.MAX_SPEED),
                ignore_ships=False), biggest_closes_planet

    elif enemy_planet:
        docked_ships = enemy_planet.all_docked_ships()
        if docked_ships:
            docked_ship = docked_ships[0]
        else:
            docked_ship = enemy_planet
        return ship.navigate(
            ship.closest_point_to(docked_ship),
            game_map,
            speed=int(hlt.constants.MAX_SPEED),
            ignore_ships=True), None
    elif my_planet:
        if ship.can_dock(my_planet):
            return ship.dock(my_planet), None
        return ship.navigate(
            ship.closest_point_to(my_planet),
            game_map,
            speed=int(hlt.constants.MAX_SPEED),
            ignore_ships=False), None
    else:
        return None, None


def get_ship_coordinated_command(ship, enemy_planet):
    if not enemy_planet:
        return None, None
    docked_ships = enemy_planet.all_docked_ships()
    if docked_ships:
        docked_ship = docked_ships[0]
    else:
        docked_ship = enemy_planet
    if ship.can_dock(enemy_planet):
        return ship.dock(enemy_planet), enemy_planet
    return ship.navigate(
        ship.closest_point_to(docked_ship),
        game_map,
        speed=int(hlt.constants.MAX_SPEED),
        ignore_ships=True), None


class ProtectMission(object):
    def __init__(self, planet_to_protect, ship_id):
        self.planet_to_protect = planet_to_protect
        self.ship_id = ship_id

    def get_command(self, game_map, enemy_ships, ship):
        enemy_ship = min(
            enemy_ships,
            key=lambda x: self.planet_to_protect.calculate_distance_between(x))
        return ship.navigate(
            enemy_ship,
            game_map,
            speed=int(hlt.constants.MAX_SPEED),
            ignore_ships=True), None


class AttackMission(object):
    def __init__(self, planet_to_attack, ship_id):
        self.planet_to_attack = planet_to_attack
        self.ship_id = ship_id

    def get_command(self, game_map, enemy_ships, ship):
        docked_ships = self.planet_to_attack.all_docked_ships()
        if docked_ships:
            docked_ship = docked_ships[0]
        else:
            docked_ship = self.planet_to_attack
        if ship.can_dock(self.planet_to_attack):
            return ship.dock(self.planet_to_attack), self.planet_to_attack
        return ship.navigate(
            ship.closest_point_to(docked_ship),
            game_map,
            speed=int(hlt.constants.MAX_SPEED),
            ignore_ships=True), None

turn = 0
enemy_planets = []
missions = {}
while True:
    turn += 1
    # TURN START
    # Update the map for the new turn and get the latest version
    game_map = game.update_map()
    my_id = game_map.my_id
    i = 0

    # Here we define the set of commands to be sent to the Halite engine at the end of the turn
    command_queue = []
    # For every ship that I control
    all_me = game_map.get_me()
    total_ships = all_me.all_ships()
    planets_to_be_attacked = []
    my_ship_ids = [ship.id for ship in total_ships]
    planets = game_map.all_planets()
    my_planets = [p for p in planets if p.owner and p.owner.id == my_id]
    if turn % 3 == 0:
        enemy_planets = [p for p in planets if p not in my_planets]
    enemy_ships = []
    for player in game_map.all_players():
        if player.id == my_id:
            continue
        enemy_ships.extend(player.all_ships())
    enemy_planet = None
    try:
        enemy_planet = min(enemy_planets, key=lambda x: my_planets[0].calculate_distance_between(x))
    except:
        pass
    for ship in total_ships:
        logging.info('{} ship ID'.format(ship.id))
        # If the ship is docked
        if ship.docking_status != ship.DockingStatus.UNDOCKED:
            # Skip this ship
            continue
        if ship.id in missions.keys():
            ship_command = missions[ship.id].get_command(
                game_map, enemy_ships, ship)
        elif ship.id % 5 == 0 and ship.id not in missions.keys() and my_planets and turn > 70:
            missions[ship.id] = ProtectMission(my_planets[0], ship.id)
            ship_command = missions[ship.id].get_command(
                game_map, enemy_ships, ship)
        elif ship.id % 2 == 0 and ship.id not in missions.keys():
            entities_by_distance = game_map.nearby_entities_by_distance(ship)
            sorted_list = sorted(entities_by_distance.items(), key=lambda value: value[0])
            _planets = []
            for element in sorted_list:
                for el in element[1]:
                    if isinstance(el, hlt.entity.Planet):
                        _planets.append(el)
            non_taken_planets = [planet for planet in _planets if not planet.is_owned()]
            if non_taken_planets:
                missions[ship.id] = AttackMission(non_taken_planets[0], ship.id)
            else:
                missions[ship.id] = AttackMission(enemy_planets[0], ship.id)
            logging.info('brljaaaa')
            ship_command = missions[ship.id].get_command(
                game_map, enemy_ships, ship)

        elif turn < 150:
            if ship.id % 4 == 0 and enemy_planet:
                ship_command = get_ship_coordinated_command(ship, enemy_planet)
            else:
                ship_command = get_ship_command(
                    ship, len(my_ship_ids), planets_to_be_attacked, my_ship_ids, my_planets, turn)

        else:
            ship_command = get_ship_coordinated_command(ship, enemy_planet)
        if ship_command:
            if ship_command[1] and turn >= 5:
                planets_to_be_attacked.append(ship_command[1])
            if ship_command[0]:
                command_queue.append(ship_command[0])
            # Send our set of commands to the Halite engine for this turn
    logging.info(command_queue)
    game.send_command_queue(command_queue)
    # TURN END
# GAME END
