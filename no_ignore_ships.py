# Let's start by importing the Halite Starter Kit so we can interface with the Halite engine
import hlt
# Then let's import the logging module so we can print out information
import logging

# GAME START
# Here we define the bot's name as Settler and initialize the game, including communication with the Halite engine.
game = hlt.Game("SmarterAttacker")
# Then we print our start message to the logs
logging.info("Starting my Settler bot!")


def get_ship_command(ship, ships_len, planets_to_be_attacked, my_ship_ids, my_planets):
    if ship.docking_status != ship.DockingStatus.UNDOCKED:
        # Skip this ship
        return None, None

    # For each planet in the game (only non-destroyed planets are included)
    entities_by_distance = game_map.nearby_entities_by_distance(ship)
    sorted_list = sorted(
        entities_by_distance.items(), key=lambda value: value[0])
    _planets = []
    for element in sorted_list:
        for el in element[1]:
            if isinstance(el, hlt.entity.Planet):
                _planets.append(el)
    enemy_planet = None
    non_taken_planet = None
    if _planets:
        closest_planet = _planets[0]
        if closest_planet in my_planets and not closest_planet.is_full():
            non_taken_planet = closest_planet
        else:
            try:
                non_taken_planet = next(
                    planet for planet in _planets if not planet.is_owned() and planet not in planets_to_be_attacked)
            except:
                try:
                    non_taken_planet = next(planet for planet in _planets if not planet.is_full() and planet in my_planets)
                except:
                    try:
                        # no more non_taken_planet; start attacking
                        enemy_planet = next(
                            planet for planet in _planets if planet not in my_planets)
                    except:
                        pass
    else:
        return None, None
    if non_taken_planet:
        if ship.can_dock(non_taken_planet):
            return ship.dock(non_taken_planet), None
        else:
            return ship.navigate(
                ship.closest_point_to(non_taken_planet),
                # non_taken_planet,
                game_map,
                speed=int(hlt.constants.MAX_SPEED),
                ignore_ships=True), non_taken_planet

    elif enemy_planet:
        return ship.navigate(
            enemy_planet,
            game_map,
            speed=int(hlt.constants.MAX_SPEED),
            ignore_ships=True), None
    else:
        return None, None


while True:
    # TURN START
    # Update the map for the new turn and get the latest version
    game_map = game.update_map()
    my_id = game_map.my_id

    # Here we define the set of commands to be sent to the Halite engine at the end of the turn
    command_queue = []
    # For every ship that I control
    all_me = game_map.get_me()
    total_ships = all_me.all_ships()
    planets_to_be_attacked = []
    my_ship_ids = [ship.id for ship in total_ships]
    planets = game_map.all_planets()
    my_planets = [p for p in planets if p.owner and p.owner.id == my_id]
    for ship in total_ships:
        # If the ship is docked
        ship_command = get_ship_command(ship, len(my_ship_ids), planets_to_be_attacked, my_ship_ids, my_planets)
        if ship_command:
            if ship_command[1]:
                planets_to_be_attacked.append(ship_command[1])
            if ship_command[0]:
                command_queue.append(ship_command[0])
            # Send our set of commands to the Halite engine for this turn
    game.send_command_queue(command_queue)
    # TURN END
# GAME END
