# Let's start by importing the Halite Starter Kit so we can interface with the Halite engine
import hlt
# Then let's import the logging module so we can print out information
import logging

# GAME START
# Here we define the bot's name as Settler and initialize the game, including communication with the Halite engine.
game = hlt.Game("CarefulAttackerV3")
# Then we print our start message to the logs
logging.info("Starting my Settler bot!")
import time


class ProtectMission(object):
    def __init__(self, planet_to_protect, ship_id):
        self.planet_to_protect = planet_to_protect
        self.ship_id = ship_id

    def get_command(self, game_map, ship, enemy_planet=None):
        return ship.navigate(
            ship.closest_point_to(self.planet_to_protect),
            game_map,
            speed=int(hlt.constants.MAX_SPEED),
            ignore_ships=True), None


class ColonizeMission(object):
    def __init__(self, planet_to_attack, ship_id):
        self.planet_to_attack = planet_to_attack
        self.ship_id = ship_id

    def get_command(self, game_map, ship, enemy_planet=None):
        docked_ships = self.planet_to_attack.all_docked_ships()
        if docked_ships:
            docked_ship = docked_ships[0]
        else:
            docked_ship = self.planet_to_attack
        if not docked_ships and ship.can_dock(self.planet_to_attack):
            return ship.dock(self.planet_to_attack), self.planet_to_attack
        return ship.navigate(
            ship.closest_point_to(docked_ship),
            game_map,
            speed=int(hlt.constants.MAX_SPEED),
            ignore_ships=False), None


class DockMission(object):
    def __init__(self, planet_to_attack, ship_id):
        self.planet_to_attack = planet_to_attack
        self.ship_id = ship_id

    def get_command(self, game_map, ship, enemy_planet=None):
        if self.planet_to_attack.is_full():
            self.planet_to_attack = enemy_planet
        if ship.can_dock(self.planet_to_attack):
            return ship.dock(self.planet_to_attack), self.planet_to_attack
        return ship.navigate(
            ship.closest_point_to(self.planet_to_attack),
            game_map,
            speed=int(hlt.constants.MAX_SPEED),
            ignore_ships=False), None


class AttackMission(object):
    def __init__(self, planet_to_attack, ship_id):
        logging.info('Attack mission ({}) -> {}'.format(ship_id, planet_to_attack))
        self.planet_to_attack = planet_to_attack
        self.ship_id = ship_id

    def get_command(self, game_map, ship, enemy_planet):
        docked_ships = self.planet_to_attack.all_docked_ships()
        if docked_ships:
            docked_ship = docked_ships[0]
        else:
            docked_ship = self.planet_to_attack
        if not docked_ships:
            return ship.dock(self.planet_to_attack), self.planet_to_attack
        docked_ship = self.planet_to_attack
        return ship.navigate(
            docked_ship,
            game_map,
            max_corrections=15,
            angular_step=5,
            speed=int(hlt.constants.MAX_SPEED),
            ignore_ships=False), None

turn = 0
missions = {}
while True:
    turn += 1
    # TURN START
    # Update the map for the new turn and get the latest version
    game_map = game.update_map()
    start = time.time()
    my_id = game_map.my_id
    command_queue = []
    all_me = game_map.get_me()
    total_ships = all_me.all_ships()
    planets_to_be_attacked = []
    planets = game_map.all_planets()
    my_planets = [p for p in planets if p.owner and p.owner.id == my_id]
    enemy_planets = [p for p in planets if p not in my_planets]
    enemy_planet = None
    closest_enemy_planets = planets
    try:
        my_planet = my_planets[turn % 3]
    except:
        my_planet = total_ships[0]
    unfilled_planets = [p for p in my_planets if not p.is_full()]
    if unfilled_planets:
        closest_unfilled = min(
            unfilled_planets,
            key=lambda x: my_planet.calculate_distance_between(x))
    else:
        closest_unfilled = None

    if my_planet:
        closest_enemy = min(
            enemy_planets,
            key=lambda x: my_planet.calculate_distance_between(x))

    if turn <= 2:
        for i, ship in enumerate(total_ships):
            closest_enemy_planets = sorted(
                closest_enemy_planets,
                key=lambda x: ship.calculate_distance_between(x))
            closest_enemy_planet = closest_enemy_planets[0]
            closest_enemy_planets.remove(closest_enemy_planet)
            missions[ship.id] = ColonizeMission(
                closest_enemy_planet, ship.id)
            ship_command = missions[ship.id].get_command(
                game_map, ship)
            if ship_command:
                if ship_command[0]:
                    command_queue.append(ship_command[0])
        game.send_command_queue(command_queue)
    else:
        for ship in total_ships:
            end_time = time.time() - start
            logging.info(end_time)
            if end_time >= 1.85:
                game.send_command_queue(command_queue)
                break
            # If the ship is docked
            if ship.docking_status != ship.DockingStatus.UNDOCKED:
                # Skip this ship
                continue
            if ship.id in missions.keys():
                ship_command = missions[ship.id].get_command(
                    game_map, ship, enemy_planets[turn % 3])
            elif ship.id % 50 == 0 and ship.id not in missions.keys() and my_planets:
                missions[ship.id] = ProtectMission(my_planets[0], ship.id)
                ship_command = missions[ship.id].get_command(
                    game_map, ship)
            elif ship.id % 4 == 0 and turn > 30:
                if closest_unfilled:
                    missions[ship.id] = DockMission(
                        closest_unfilled, ship.id)
                    ship_command = missions[ship.id].get_command(
                        game_map, ship, closest_unfilled)
                else:
                    missions[ship.id] = AttackMission(
                        closest_enemy, ship.id)
                    ship_command = missions[ship.id].get_command(
                        game_map, ship, closest_enemy)
            elif ship.id not in missions.keys():
                if closest_enemy:
                    missions[ship.id] = AttackMission(
                        closest_enemy, ship.id)
                else:
                    missions[ship.id] = AttackMission(enemy_planets[0], ship.id)
                ship_command = missions[ship.id].get_command(
                    game_map, ship, enemy_planets[0])
            if ship_command:
                if ship_command[0]:
                    command_queue.append(ship_command[0])
                # Send our set of commands to the Halite engine for this turn
        game.send_command_queue(command_queue)
    # TURN END
# GAME END
