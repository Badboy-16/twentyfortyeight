import os
import sys

from random import randint

class Board:


    def __init__(self):
        """
        Initialising the board. The position of the board is represented
        by a dictionary with 16 pairs of keys and values. The keys are 16
        tuples which stand for the coordinates of the tiles. For example,
        (2, 3) stands for the tile on the second row and the third column.
        The values stand for the numerical value of the tile displayed to
        the player. A zero in the value means the corresponding tile is
        empty.
        """

        self.position = {(1, 1): 0, (1, 2): 0, (1, 3): 0, (1, 4): 0,
                         (2, 1): 0, (2, 2): 0, (2, 3): 0, (2, 4): 0,
                         (3, 1): 0, (3, 2): 0, (3, 3): 0, (3, 4): 0,
                         (4, 1): 0, (4, 2): 0, (4, 3): 0, (4, 4): 0}
        self.win = False
        self.game_over = False
        self.score = 0
        self.score_add = 0

        # Generate starting positions for the two 2 tiles.
        pos_one, pos_two = self.gen_starting_pos()
        self.position[pos_one] = 2
        self.position[pos_two] = 2


    def __str__(self):
        """
        Visual representation of the game board and the score in command line.
        """

        tiles = list()
        for value in self.position.values():
            tiles.append(value)
        for value in tiles:
            value = str(value)
        board_repr = f"""
        {tiles[0]:>5} {tiles[1]:>5} {tiles[2]:>5} {tiles[3]:>5}

        {tiles[4]:>5} {tiles[5]:>5} {tiles[6]:>5} {tiles[7]:>5}

        {tiles[8]:>5} {tiles[9]:>5} {tiles[10]:>5} {tiles[11]:>5}

        {tiles[12]:>5} {tiles[13]:>5} {tiles[14]:>5} {tiles[15]:>5}

        Score: {self.score:> 10}
        """
        return board_repr


    def gen_starting_pos(self):
        """
        Generate the starting position of the two "2" tiles.
        """

        valid_pos = False
        while valid_pos == False:
            pos_one_x = randint(1, 4)
            pos_one_y = randint(1, 4)
            pos_two_x = randint(1, 4)
            pos_two_y = randint(1, 4)
            pos_one = (pos_one_x, pos_one_y)
            pos_two = (pos_two_x, pos_two_y)
            if pos_one != pos_two:
                return pos_one, pos_two
            else:
                continue


    def get_empty_tiles(self):

        """Return a list of tiles that are empty."""

        empty_tiles = list()
        for key in self.position:
            if self.position[key] == 0:
                empty_tiles.append(key)
        return empty_tiles


    def get_occupied_tiles(self):

        """Return a list of tiles that are not empty."""

        occupied_tiles = list()
        for key in self.position:
            if self.position[key] != 0:
                occupied_tiles.append(key)
        return occupied_tiles


    def gen_rand_tile(self):

        """Generate a tile of value 2 or 4 on random empty tiles"""

        # Implying a 90% possibility of a tile value of 2 and 10% of 4.
        num_list = [2 for i in range(9)] + [4]
        empty_tiles = self.get_empty_tiles()
        rand_value = num_list[randint(0, len(num_list) - 1)]
        rand_tile_pos = empty_tiles[randint(0, len(empty_tiles) - 1)]
        self.position[rand_tile_pos] = rand_value


    def move(self, direction):
        new_pos = dict()
        for key in self.position:
            new_pos[key] = self.position[key]
        if direction == 'w' or direction == 's':
            for col_num in range(1, 5):
                tiles = list()
                for key in self.position:
                    if key[1] == col_num and self.position[key] != 0:
                        tiles.append(self.position[key])

                index = 0
                while index < len(tiles) - 1:
                    if tiles[index] == tiles[index + 1]:
                        tiles[index + 1] = 0
                        tiles[index] *= 2
                        self.score_add = tiles[index]
                        index += 2
                    else:
                        index += 1

                rem_tiles = [tile for tile in tiles if tile != 0]

                new_col = {(1, col_num): 0,
                           (2, col_num): 0,
                           (3, col_num): 0,
                           (4, col_num): 0}

                if direction == 'w':
                    index = 0
                    for tile in rem_tiles:
                        new_col[(index + 1, col_num)] = rem_tiles[index]
                        index += 1
                elif direction == 's':
                    index = 5 - len(rem_tiles)
                    rem_index = 0
                    for tile in rem_tiles:
                        new_col[(index, col_num)] = rem_tiles[rem_index]
                        index += 1
                        rem_index += 1

                for key in new_col:
                    new_pos[key] = new_col[key]

        elif direction == 'a' or direction == 'd':
             for row_num in range(1, 5):
                tiles = list()
                for key in self.position:
                    if key[0] == row_num and self.position[key] != 0:
                        tiles.append(self.position[key])

                index = 0
                while index < len(tiles) - 1:
                    if tiles[index] == tiles[index + 1]:
                        tiles[index + 1] = 0
                        tiles[index] *= 2
                        self.score_add = tiles[index]
                        index += 2
                    else:
                        index += 1

                rem_tiles = [tile for tile in tiles if tile != 0]

                new_row = {(row_num, 1): 0,
                           (row_num, 2): 0,
                           (row_num, 3): 0,
                           (row_num, 4): 0}

                if direction == 'a':
                    index = 0
                    for tile in rem_tiles:
                        new_row[(row_num, index + 1)] = rem_tiles[index]
                        index += 1
                elif direction == 'd':
                    index = 5 - len(rem_tiles)
                    rem_index = 0
                    for tile in rem_tiles:
                        new_row[(row_num, index)] = rem_tiles[rem_index]
                        index += 1
                        rem_index += 1

                for key in new_row:
                    new_pos[key] = new_row[key]

        elif direction == 'exit':
            sys.exit()

        return new_pos


    def move_is_valid(self, direction):
        old = self.position
        new = self.move(direction)
        if old == new:
            return False
        else:
            return True


    def player_win(self):
        for key in self.position:
            if self.position[key] == 2048:
                return True
        return False

    def is_game_over(self):
        for direction in ['w', 'a', 's', 'd']:
            if self.move_is_valid(direction) == True:
                return False
        return True


    def turn(self):
        valid_move = False
        while valid_move == False:
            direction = input()
            if self.move_is_valid(direction) == False:
                print("Invalid move")
                continue
            else:
                valid_move = True
        self.position = self.move(direction)
        self.score += self.score_add
        self.score_add = 0
        self.gen_rand_tile()
        self.win = self.player_win()
        self.game_over = self.is_game_over()


def main():

    board = Board()
    while board.game_over == False and board.win == False:
        os.system('clear' if os.name == 'posix' else 'cls')
        print(board)
        board.turn()
    if board.game_over == True:
        print("Game over!")
    elif board.win == True:
        print("You win!")

