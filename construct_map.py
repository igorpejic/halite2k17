from cocos.rect import Rect
from quad_tree_map import QuadTree

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
def draw_rectangles(img, quad_tree):
    draw_rect(img, quad_tree)
import random
random.seed()

def draw_rect(img, node):
    for node in node.nodes:
        if node.nodes:
            draw_rect(img, node)
        else:
            cv2.rectangle(img, (int(node.x), int(node.y)), (int(node.x + node.width), int(node.y + node.height)), (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), 1)
            cv2.imshow('a', img)
            cv2.waitKey(0)

with open('game_map.pkl', 'rb') as game_map:
    game_map = pickle.load(game_map)

all_planets = game_map.all_planets()
img = np.zeros((840, 880, 3), np.uint8)
for p in all_planets:
    cv2.circle(img, (int(p.x), int(p.y)), int(p.radius), (255, 0, 0), 2)
cv2.imshow('a', img)
cv2.waitKey(0)

# print(all_planets)
blockers = get_planets_as_rects(all_planets)
minimum_size = 32
quad_tree = QuadTree(0, 0, game_map.width, game_map.height, blockers, 1)
# print(game_map.width, game_map.height, 'aaa')
# print(quad_tree.nodes)
draw_rectangles(img, quad_tree)

# import sys;sys.exit()
for p in all_planets:
    trip = quad_tree.find_path((0, 0), (p.x, p.y), p.radius )
    # cv2.imshow('a', img)
    # cv2.waitKey(0)
    if trip is None:
        # already in the block; just thrust towards
        angle = self.calculate_angle_between(target)
    if trip == 1:
        # forbidden zone
        pass
        print('bbb')
    print(trip)
