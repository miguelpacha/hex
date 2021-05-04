import numpy as np
from collections import defaultdict

class HexPlayer():
    def __init__(self, x, y, player):
        self.win = False
        self.board = np.zeros((x+2, y+2), dtype=np.int8)
        self.groups = defaultdict(list)
        self.available_group = 3
        if player == 'x':
            self.board[ 0] = 1
            self.board[-1] = 2
        elif player == 'y':
            self.board[:, 0] = 1
            self.board[:,-1] = 2
        else:
            raise Exception()
    
    def find_surrounding_groups(self, x, y):
        groups = set()
        for _x, _y in [ (x, y-1), (x+1, y-1), (x-1, y), (x+1, y), (x-1, y+1), (x, y+1) ]:
            group = self.board[_x, _y]
            if group != 0:
                groups.add(group)
        return sorted(groups)
    
    def add_point_to_group(self, x, y, to_group):
        self.groups[to_group].append((x,y))
        self.board[(x,y)] = to_group

    def merge_group(self, from_group, to_group):
        for x, y in self.groups[from_group]:
            self.add_point_to_group(x, y, to_group)

    def place_stone(self, x, y):
        found_groups = self.find_surrounding_groups(x, y)
        if len(found_groups) == 0:
            self.add_point_to_group(x, y, self.available_group)
            self.available_group += 1
        elif found_groups[:2]==[1,2]:
            self.win = True
        else:
            to_group = found_groups[0]
            self.add_point_to_group(x, y, to_group)
            for from_group in found_groups[1:]:
                self.merge_group(from_group, to_group)

class HexBoard:
    def __init__(self, x, y):
        self.board = np.zeros((x+2, y+2), dtype=np.int8)

        self.players = [None, HexPlayer(x, y, 'x'), HexPlayer(x, y, 'y')] # hacky: 1-based index
        self.board[[0,-1]] = 1
        self.board[:,[0,-1]] = 2
        self.winner = None

    def play(self, player_no, x, y):
        current_player = self.players[player_no]
        if self.board[x,y] != 0:
            raise Exception("Already occupied!")
        else:
            self.board[x,y] = player_no
            current_player.place_stone(x,y)
            if (current_player.win):
                self.winner = player_no


from itertools import cycle
class HexTextInterface:
    def __init__(self, x, y):
        self.game = HexBoard(x,y)
        self.player_cycle = cycle([1,2])
        while self.game.winner is None:
            self.loop()
        self.show()
        print(f"Player {self.game.winner} won!")
    
    def loop(self):
        self.show()
        player_no = next(self.player_cycle)
        play = input(f"Player #{player_no} to play: ")
        x, y = map(int, play.split(' '))
        self.game.play(player_no, x, y)
    
    def show(self):
        for k, line in enumerate(self.game.board):
            print( k*' '," ".join( str(x) if x!=0 else "." for x in line ))


HexTextInterface(4,4)

''' 
import sys
import pygame as pg
import pygame.locals as pl

class HexGUI:
    def __init__(self, x, y):
        self.game = HexBoard(5,5)
    def draw(self):
        DISPLAYSURF = pg.display.set_mode((600,300))
        pg.display.update()
        DISPLAYSURF.fill((255, 255, 255))
'''