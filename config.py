

import os, sys, copy, random, math, time, pdb
import queue
import pygame
import math2d as m2d
import numpy as np
import scipy.spatial as scSpatial
from collections import defaultdict
from threading import Thread

#globals
GAME_ROOT = r"C:\Users\Toby\Documents\github\offworld\ZeldaClone"
scrsize=[1280.0, 960.0] #in pixels
aspRatio=scrsize[1]/scrsize[0]
screenTileWidth = 22 #turn pixels into tiles, number of tiles in the visible screen
screenTileHeight = int(screenTileWidth*aspRatio)
pixelsPerTileWidth = int(scrsize[0]/screenTileWidth)
pixelsPerTileHeight = int(scrsize[1]/screenTileHeight) #square Tiles
psuedoPixelsPerTileWidth = int(pixelsPerTileWidth/16) #16 psuedo-pixels per tile
psuedoPixelsPerTileHeight = int(pixelsPerTileHeight/16) 


# global data-stream for sensing and w/e
DATA = {}

# global queue for messages & commands
MESSAGES = queue.Queue()