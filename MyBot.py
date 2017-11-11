"""
Welcome to your first Halite-II bot!

This bot's name is Settler. It's purpose is simple (don't expect it to win complex games :) ):
1. Initialize game
2. If a ship is not docked and there are unowned planets
2.a. Try to Dock in the planet if close enough
2.b If not, go towards the planet

Note: Please do not place print statements here as they are used to communicate with the Halite engine. If you need
to log anything use the logging module.
"""
# Let's start by importing the Halite Starter Kit so we can interface with the Halite engine
import hlt
# Then let's import the logging module so we can print out information
import logging

# GAME START
# Here we define the bot's name as Settler and initialize the game, including communication with the Halite engine.
game = hlt.Game("Settler")
# Then we print our start message to the logs
logging.info("Starting my Settler bot!")

def get_ship_command(ship):
    if ship.docking_status != ship.DockingStatus.UNDOCKED:
        # Skip this ship
        return None

    # For each planet in the game (only non-destroyed planets are included)
    entities_by_distance = game_map.nearby_entities_by_distance(ship)
    planets = [planet for distance in entities_by_distance for planet in entities_by_distance[distance]]
    non_taken_planets = [p for p in planets if isinstance(p, hlt.entity.Planet) and not p.is_owned()]
    taken_planets = [p for p in planets if isinstance(p, hlt.entity.Planet) and p.is_owned()]
    if non_taken_planets:
        for non_taken_planet in non_taken_planets:
        # If we can dock, let's (try to) dock. If two ships try to dock at once, neither will be able to.
            if ship.can_dock(non_taken_planet):
                return ship.dock(non_taken_planet)
                break
            else:
                # If we can't dock, we move towards the closest empty point near this planet (by using closest_point_to)
                # with constant speed. Don't worry about pathfinding for now, as the command will do it for you.
                # We run this navigate command each turn until we arrive to get the latest move.
                # Here we move at half our maximum speed to better control the ships
                # In order to execute faster we also choose to ignore ship collision calculations during navigation.
                # This will mean that you have a higher probability of crashing into ships, but it also means you will
                # make move decisions much quicker. As your skill progresses and your moves turn more optimal you may
                # wish to turn that option off.
                return ship.navigate(
                    ship.closest_point_to(non_taken_planet),
                    game_map,
                    speed=int(hlt.constants.MAX_SPEED),
                    ignore_ships=True)
    else:
        for non_taken_planet in taken_planets:
        # If we can dock, let's (try to) dock. If two ships try to dock at once, neither will be able to.
            if ship.can_dock(non_taken_planet):
                return ship.dock(non_taken_planet)
            else:

                # If we can't dock, we move towards the closest empty point near this planet (by using closest_point_to)
                # with constant speed. Don't worry about pathfinding for now, as the command will do it for you.
                # We run this navigate command each turn until we arrive to get the latest move.
                # Here we move at half our maximum speed to better control the ships
                # In order to execute faster we also choose to ignore ship collision calculations during navigation.
                # This will mean that you have a higher probability of crashing into ships, but it also means you will
                # make move decisions much quicker. As your skill progresses and your moves turn more optimal you may
                # wish to turn that option off.
                navigate_command = ship.navigate(
                    ship.closest_point_to(non_taken_planet),
                    game_map,
                    speed=int(hlt.constants.MAX_SPEED/2),
                    ignore_ships=True)
                return navigate_command
while True:
    # TURN START
    # Update the map for the new turn and get the latest version
    game_map = game.update_map()

    # Here we define the set of commands to be sent to the Halite engine at the end of the turn
    command_queue = []
    # For every ship that I control
    for ship in game_map.get_me().all_ships():
        # If the ship is docked
        ship_command = get_ship_command(ship)
        if ship_command:
            command_queue.append(ship_command)
            # Send our set of commands to the Halite engine for this turn
    game.send_command_queue(command_queue)
    # TURN END
# GAME END
