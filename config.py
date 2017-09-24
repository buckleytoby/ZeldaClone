

import os,sys,copy,random,queue,math,time,pdb
import pygame
import numpy as np
import scipy.spatial as scSpatial
from collections import defaultdict

#globals
scrsize=[640, 480] #in pixels
aspRatio=scrsize[1]/scrsize[0]
screenTileWidth = 40 #turn pixels into tiles, number of tiles in the visible screen
screenTileHeight = int(screenTileWidth*aspRatio)
pixelsPerTileWidth = int(scrsize[0]/screenTileWidth)
pixelsPerTileHeight = int(scrsize[1]/screenTileHeight) #square Tiles
psuedoPixelsPerTileWidth = int(pixelsPerTileWidth/16) #16 psuedo-pixels per tile
psuedoPixelsPerTileHeight = int(pixelsPerTileHeight/16) 