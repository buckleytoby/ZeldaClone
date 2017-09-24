

import os,sys,copy,random,queue,math,time,pdb
import pygame
import numpy as np

#globals
scrsize=[640, 480] #in pixels
aspRatio=scrsize[1]/scrsize[0]
numTilesWidth = 40 #turn pixels into tiles, number of tiles in the visible screen
numTilesHeight = int(numTilesWidth*aspRatio)
pixelsPerTileWidth = int(scrsize[0]/numTilesWidth)
pixelsPerTileHeight = int(scrsize[1]/numTilesHeight) #square Tiles
psuedoPixelsPerTileWidth = int(pixelsPerTileWidth/16) #16 psuedo-pixels per tile
psuedoPixelsPerTileHeight = int(pixelsPerTileHeight/16) 
