from datetime import datetime
from os import environ as env, name as os_nm, path
from random import randint
import sqlite3
from subprocess import call as sp_call
from sys import exit as quit_game

from rich import print as rprint


home = str(env['HOME']) if os_nm == 'posix' else str(env['USERPROFILE'])
# Path to the high score database
hs_path = path.join(home, '.twentyfortyeight_hs.sqlite')


CREATE_TABLE_QUERY = """CREATE TABLE IF NOT EXISTS highscore (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player TEXT NOT NULL,
    score INTEGER NOT NULL,
    moves INTEGER NOT NULL,
    date DATE NOT NULL
);
"""

READ_HS_QUERY = "SELECT * FROM highscore LIMIT 10"


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
        self.pos = {(1, 1): 0, (1, 2): 0, (1, 3): 0, (1, 4): 0,
                    (2, 1): 0, (2, 2): 0, (2, 3): 0, (2, 4): 0,
                    (3, 1): 0, (3, 2): 0, (3, 3): 0, (3, 4): 0,
                    (4, 1): 0, (4, 2): 0, (4, 3): 0, (4, 4): 0}
        self.win = False
        self.game_over = False
        self.score = 0
        self.score_add = 0
        self.moves = 0

        # Generate starting positions for the two 2 tiles.
        pos_one, pos_two = self.gen_start_pos()
        self.pos[pos_one] = self.pos[pos_two] = 2

    def represent(self):
        """
        Visual representation of the game board and the score in command line.

        :return: the visual representation of the board in 4x4
        :rtype: str
        """
        # Colours of different tiles
        c = {
            ' ': '#ffffff',
            2: '#ffffff',
            4: '#fcf3f2',
            8: '#fce7e7',
            16: '#fcd6d3',
            32: '#eaaad9',
            64: '#d683c3',
            128: '#cb5ab0',
            256: '#c12d9f',
            512: '#ced1f6',
            1024: '#e7e6fb',
            2048: '#f3f4fd'
        }
        # List of tiles
        t = list()
        for value in self.pos.values():
            if value == 0:
                t.append(' ')
            else:
                t.append(value)
        for value in t:
            value = str(value)
        board_repr = f"""
        ---------------------------------
        | [{c[t[0]]}]{t[0]:>5}[/{c[t[0]]}] """ \
        f"""| [{c[t[1]]}]{t[1]:>5}[/{c[t[1]]}] """ \
        f"""| [{c[t[2]]}]{t[2]:>5}[/{c[t[2]]}] """ \
        f"""| [{c[t[3]]}]{t[3]:>5}[/{c[t[3]]}] |
        ---------------------------------
        | [{c[t[4]]}]{t[4]:>5}[/{c[t[4]]}] """ \
        f"""| [{c[t[5]]}]{t[5]:>5}[/{c[t[5]]}] """ \
        f"""| [{c[t[6]]}]{t[6]:>5}[/{c[t[6]]}] """ \
        f"""| [{c[t[7]]}]{t[7]:>5}[/{c[t[7]]}] |
        ---------------------------------
        | [{c[t[8]]}]{t[8]:>5}[/{c[t[8]]}] """ \
        f"""| [{c[t[9]]}]{t[9]:>5}[/{c[t[9]]}] """ \
        f"""| [{c[t[10]]}]{t[10]:>5}[/{c[t[10]]}] """ \
        f"""| [{c[t[11]]}]{t[11]:>5}[/{c[t[11]]}] |
        ---------------------------------
        | [{c[t[12]]}]{t[12]:>5}[/{c[t[12]]}] """ \
        f"""| [{c[t[13]]}]{t[13]:>5}[/{c[t[13]]}] """ \
        f"""| [{c[t[14]]}]{t[14]:>5}[/{c[t[14]]}] """ \
        f"""| [{c[t[15]]}]{t[15]:>5}[/{c[t[15]]}] |
        ---------------------------------
        Score: {self.score:> 10}
        """
        return board_repr

    def gen_start_pos(self):
        """
        Generate the starting position of the two "2" tiles.

        :return: two starting positions of the tiles
        :rtype: tuple, tuple
        """
        while True:
            one_x = randint(1, 4)
            one_y = randint(1, 4)
            two_x = randint(1, 4)
            two_y = randint(1, 4)
            pos_one = (one_x, one_y)
            pos_two = (two_x, two_y)
            if pos_one != pos_two:
                return pos_one, pos_two
            continue

    def get_empty_tiles(self):
        """
        Return a list of tiles that are empty.

        :return: a list of empty tiles
        :rtype: list
        """
        empty_tiles = list()
        for key in self.pos:
            if self.pos[key] == 0:
                empty_tiles.append(key)
        return empty_tiles

    def get_occupied_tiles(self):
        """
        Return a list of tiles that are not empty.

        :return: a list of occupied tiles
        :rtype: list
        """
        occupied_tiles = list()
        for key in self.pos:
            if self.pos[key] != 0:
                occupied_tiles.append(key)
        return occupied_tiles

    def gen_rand_tile(self):
        """
        Generate a tile of value 2 or 4 on random empty tiles
        """
        # Implying a 90% possibility of a tile value of 2 and 10% of 4.
        num_list = [2 for i in range(9)] + [4]
        empty_tiles = self.get_empty_tiles()
        rand_value = num_list[randint(0, len(num_list) - 1)]
        rand_tile_pos = empty_tiles[randint(0, len(empty_tiles) - 1)]
        self.pos[rand_tile_pos] = rand_value

    def move(self, direction):
        """
        Make a move in the given direction.

        :param str direction: direction in which to move indicated by WASD
        :return: the position after the move
        :rtype: dict
        """
        new_pos = dict()
        for key in self.pos:
            new_pos[key] = self.pos[key]
        if direction == 'w' or direction == 's':
            for col_num in range(1, 5):
                tiles = list()
                for key in self.pos:
                    if key[1] == col_num and self.pos[key] != 0:
                        tiles.append(self.pos[key])
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
                new_col = {(row, col_num): 0 for row in range(1, 5)}
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
                for key in self.pos:
                    if key[0] == row_num and self.pos[key] != 0:
                        tiles.append(self.pos[key])
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
                new_row = {(row_num, col): 0 for col in range(1, 5)}
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
            pl_name = input("Input your name on the leaderboard: ")
            today = datetime.today().strftime('%Y-%m-%d')
            connection = sqlite3.connect(hs_path)
            cursor = connection.cursor()
            query_tuple = (pl_name, self.score, self.moves, today,)
            cursor.execute("INSERT INTO highscore \
                           (player, score, moves, date) \
                           VALUES (?, ?, ?, ?);", query_tuple)
            connection.commit()
            quit_game()
        elif direction == 'hs':
            print(column_names())
            for record in show_hs():
                print(record)
            input("Press Enter to continue")
        return new_pos

    def move_is_valid(self, direction):
        """
        Check if a move is valid.

        :param str direction: direction in which to move indicated by WASD
        :return: whether the move is valid
        :rtype: bool
        """
        if direction not in ['w', 'a', 's', 'd']:
            return True
        old = self.pos
        new = self.move(direction)
        if old == new:
            return False
        return True

    def player_win(self):
        """
        Check if the player has won by reaching 2048 in any tile.

        :return: whether the player has won
        :rtype: bool
        """
        for key in self.pos:
            if self.pos[key] == 2048:
                sp_call('clear' if os_nm == 'posix' else 'cls', shell=False)
                print(self.represent())
                return True
        return False

    def is_game_over(self):
        """
        Check if the game is over with no valid moves.

        :return: whether the game is over
        :rtype: bool
        """
        for direction in ['w', 'a', 's', 'd']:
            if self.move_is_valid(direction) is True:
                return False
        return True

    def turn(self):
        """
        Make a turn in the game.

        This function will determine if the input direction is a valid move.
        If yes, it will update the board position self.pos, add the score to
        the total score, generate a random tile for the next move, and if
        needed, end the game by checking self.win and self.game_over
        """
        valid_move = False
        while valid_move is False:
            direction = input()
            if self.move_is_valid(direction) is False:
                print("Invalid move")
                continue
            else:
                valid_move = True
        self.pos = self.move(direction)
        self.score += self.score_add
        self.score_add = 0
        self.win = self.player_win()
        self.game_over = self.is_game_over()
        if direction in ['w', 'a', 's', 'd']:
            self.gen_rand_tile()
            self.moves += 1


def create_table():
    connection = sqlite3.connect(hs_path)
    cursor = connection.cursor()
    cursor.execute(CREATE_TABLE_QUERY)
    connection.commit()

def show_hs():
    connection = sqlite3.connect(hs_path)
    cursor = connection.cursor()
    cursor.execute(READ_HS_QUERY)
    hs = cursor.fetchall()
    return hs

def column_names():
    connection = sqlite3.connect(hs_path)
    cursor = connection.cursor()
    cursor.execute(READ_HS_QUERY)
    cursor.fetchall()
    col_names = [description[0] for description in cursor.description]
    return tuple(col_names)

def main():
    """
    Main loop of the game.
    """
    create_table()
    board = Board()
    while board.game_over is False and board.win is False:
        sp_call('clear' if os_nm == 'posix' else 'cls', shell=False)
        rprint(board.represent())
        board.turn()
    if board.game_over is True:
        print("Game over!")
    elif board.win is True:
        print("You win!")
    pl_name = input("Input your name on the leaderboard: ")
    today = datetime.today().strftime('%Y-%m-%d')
    connection = sqlite3.connect(hs_path)
    cursor = connection.cursor()
    query_tuple = (pl_name, self.score, self.moves, today,)
    cursor.execute("INSERT INTO highscore (player, score, moves, date) \
                   VALUES (?, ?, ?, ?);", query_tuple)
    connection.commit()
