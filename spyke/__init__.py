import sys, os
oldOut = sys.stdout
sys.stdout = open(os.devnull, 'w')
import pygame
sys.stdout = oldOut