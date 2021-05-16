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
        self.x, self.y = x, y
        self.board = np.zeros((2, x, y), dtype=np.int8)
        self.players = [HexPlayer(x, y, 'x'), HexPlayer(x, y, 'y')] # hacky: 1-based index
        self.winner = None

    def play_safe(self, player_no, x, y):
        current_player = self.players[player_no]
        if (self.board[0, x, y] != 0) or (self.board[1, x, y] != 0):
            raise Exception("Already occupied!")
        else:
            self.board[player_no, x, y] = 1
            current_player.place_stone(x+1,y+1)
            if (current_player.win):
                self.winner = player_no
    
    def play(self, player_no, x, y):
        current_player = self.players[player_no]
        self.board[player_no, x, y] = 1
        current_player.place_stone(x+1,y+1)
        if (current_player.win):
            self.winner = player_no
    
    def generate_legal_moves(self):
        for i in range(self.x):
            for j in range(self.y):
                if ((0 == self.board[0, i, j]) and( 0 == self.board[1, i, j])):
                    yield (i, j)