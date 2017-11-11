# Let's start by importing the Halite Starter Kit so we can interface with the Halite engine
import hlt
# Then let's import the logging module so we can print out information
import logging

# GAME START
# Here we define the bot's name as Settler and initialize the game, including communication with the Halite engine.
game = hlt.Game("Settler")
# Then we print our start message to the logs
logging.info("Starting my Settler bot!")


def get_ship_command(ship, ships_len):
    if ships_len < 20:
        if ship.docking_status != ship.DockingStatus.UNDOCKED:
            # Skip this ship
            return None

    # For each planet in the game (only non-destroyed planets are included)
    entities_by_distance = game_map.nearby_entities_by_distance(ship)
    logging.info(entities_by_distance)
    sorted_list = sorted(
        entities_by_distance.items(), key=lambda value: value[0])
    planets = []
    for element in sorted_list:
        for el in element[1]:
            if isinstance(el, hlt.entity.Planet):
                planets.append(el)
    if planets:
        try:
            non_taken_planet = next(
                planet for planet in planets if not planet.is_owned())
        except:
            # no more non_taken_planet
            non_taken_planet = next(
                planet for planet in planets)
    else:
        return None
    logging.info(non_taken_planet)
    if non_taken_planet:
        if ship.can_dock(non_taken_planet):
            return ship.dock(non_taken_planet)
        else:
            return ship.navigate(
                ship.closest_point_to(non_taken_planet),
                game_map,
                speed=int(hlt.constants.MAX_SPEED),
                ignore_ships=True)
    else:
        return None

while True:
    # TURN START
    # Update the map for the new turn and get the latest version
    game_map = game.update_map()

    # Here we define the set of commands to be sent to the Halite engine at the end of the turn
    command_queue = []
    # For every ship that I control
    total_ships = game_map.get_me().all_ships()
    for ship in total_ships:
        # If the ship is docked
        ship_command = get_ship_command(ship, len(total_ships))
        if ship_command:
            command_queue.append(ship_command)
            # Send our set of commands to the Halite engine for this turn
    game.send_command_queue(command_queue)
    # TURN END
# GAME END
