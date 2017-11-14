from cocos.rect import Rect
from map import QuadTree

def get_planets_as_rects(all_planets):
    '''
    returns (x1, y1, x2, y2)
    '''
    rects = []
    for planet in all_planets:
        rects.append(
            Rect(planet.x - planet.radius,
                 planet.y - planet.radius,
                 planet.radius * 2,
                 planet.radius * 2
                 ))
    return rects


import pickle
turn = 0
missions = {}

import cv2
import numpy as np
def draw_rectangles(quad_tree):
    img = np.zeros((840, 880, 3), np.uint8)
    draw_rect(img, quad_tree)
    cv2.circle(img, (100, 90), 3, (255, 0, 0), 3)
    cv2.imshow('a', img)
    cv2.waitKey(0)

def draw_rect(img, node):
    for node in node.nodes:
        if node.nodes:
            draw_rect(img, node)
        else:
            cv2.rectangle(img, (node.x, node.y), (node.x + node.width, node.y + node.height), (0, 255, 0), 3)

with open('game_map.pkl', 'rb') as game_map:
    game_map = pickle.load(game_map)

all_planets = game_map.all_planets()
# print(all_planets)
blockers = get_planets_as_rects(all_planets)
minimum_size = 32
quad_tree = QuadTree(0, 0, game_map.width, game_map.height, blockers, 1)
# print(game_map.width, game_map.height, 'aaa')
# print(quad_tree.nodes)
trip = quad_tree.find_path((0, 0), (100, 10))
draw_rectangles(quad_tree)

# import sys;sys.exit()
print(trip)
for i in range(240):
    print(i)
    img = np
    trip = quad_tree.find_path((0, 0), (100, i))
    if trip is None:
        # already in the block; just thrust towards
        pass
    if trip == 1:
        # forbidden zone
        pass

    
