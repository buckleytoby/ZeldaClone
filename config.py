

import os, sys, copy, random, math, time, pdb, json
import queue
import pygame
import math2d as m2d
import numpy as np
import tkinter
import scipy.spatial as scSpatial
from collections import defaultdict
from threading import Thread
import threading
import pytiled_parser

# debugging
SOUND_ON = False

#globals
GAME_ROOT = r"C:\Users\Toby\Documents\github\offworld\ZeldaClone"
scrsize=[960.0, 720.0] #in pixels
aspRatio=scrsize[1]/scrsize[0]
screenTileWidth = 22 #turn pixels into tiles, number of tiles in the visible screen
screenTileHeight = int(screenTileWidth*aspRatio)
pixelsPerTileWidth = int(scrsize[0]/screenTileWidth)
pixelsPerTileHeight = int(scrsize[1]/screenTileHeight) #square Tiles
psuedoPixelsPerTileWidth = int(pixelsPerTileWidth/16) #16 psuedo-pixels per tile
psuedoPixelsPerTileHeight = int(pixelsPerTileHeight/16) 

TILE_SIZE = np.array([16.0, 16.0])

pixel_factor = np.array((pixelsPerTileWidth, pixelsPerTileHeight))


# global data-stream for sensing and w/e
"""
game_time
game_objects_ref
player_xy
screen_location - np array
"""
DATA = {}
DATA["game_time"] = 0.0

# global queue for messages & commands
MESSAGES = queue.Queue()