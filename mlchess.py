from enum import Enum
from bitarray import bitarray

class Piece(Enum):
    EMPTY           =   0

    WHITE           =   0
    BLACK           =   127

    KING            =   12
    QUEEN           =   24
    ROOK            =   36
    KNIGHT          =   48
    BISHOP          =   60
    PAWN            =   72

    UNMOVED         =   1
    NORMAL          =   2
    PROMOTED        =   3
    MOVED_DOUBLE    =   4
    IN_CHECK        =   5
    CHECK_MATE      =   6

    MOVE            =   254
    TAKE            =   255

class Board:

    MOVE_TAKE_DIRECTION = {
        Piece.QUEEN: [
            [-1, 0, 0], [ 1, 0, 0], [ 0, 0,-1], [ 0, 0, 1], [-1, 0,-1], [-1, 0, 1], [ 1, 0,-1], [ 1, 0, 1], [-1,-1, 0], 
            [ 1,-1, 0], [ 0,-1,-1], [ 0,-1, 1], [-1,-1,-1], [-1,-1, 1], [ 1,-1,-1], [ 1,-1, 1], [-1, 1, 0], [ 1, 1, 0], 
            [ 0, 1,-1], [ 0, 1, 1], [-1, 1,-1], [-1, 1, 1], [ 1, 1,-1], [ 1, 1, 1], [ 0, 1, 0], [ 0,-1, 0]
        ],
        Piece.BISHOP: [
            [-1,-1, 0], [-1, 1, 0], [ 1,-1, 0], [ 1, 1, 0], [-1,-1, 1], [-1, 1, 1], [ 1,-1, 1], [ 1, 1, 1], [-1,-1,-1], 
            [-1, 1,-1], [ 1,-1,-1], [ 1, 1,-1]
        ],
        Piece.ROOK: [
            [-1, 0, 0], [ 1, 0, 0], [ 0, 1, 0], [ 0,-1, 0], [ 0, 0,-1], [ 0, 0, 1], [-1, 0,-1], [ 1, 0,-1], [ 0, 1,-1], 
            [ 0,-1,-1], [-1, 0, 1], [ 1, 0, 1], [ 0, 1, 1], [ 0,-1, 1]
        ]
    }

    MOVE_TAKE_POINT = {
        Piece.KNIGHT: [
            [ 1,-2, 0], [ 2,-1, 0], [ 2, 1, 0], [ 1, 2, 0], [-1, 2, 0], [-2, 1, 0], [-2,-1, 0], [-1,-2, 0], [ 0,-2, 1], 
            [ 2, 0, 1], [ 0, 2, 1], [-2, 0, 1], [-1, 0, 2], [ 0,-1, 2], [ 1, 0, 2], [ 0, 1, 2], [ 0,-2,-1], [ 2, 0,-1], 
            [ 0, 2,-1], [-2, 0,-1], [-1, 0,-2], [ 0,-1,-2], [ 1, 0,-2], [ 0, 1,-2]
        ],
        Piece.KING: [
            [-1, 1, 1], [ 0, 1, 1], [ 1, 1, 1], [-1, 0, 1], [ 0, 0, 1], [ 1, 0, 1], [-1,-1, 1], [ 0,-1, 1], [ 1,-1, 1], 
            [-1, 1, 0], [ 0, 1, 0], [ 1, 1, 0], [-1, 0, 0], [ 1, 0, 0], [-1,-1, 0], [ 0,-1, 0], [ 1,-1, 0], [-1, 1,-1], 
            [ 0, 1,-1], [ 1, 1,-1], [-1, 0,-1], [ 0, 0,-1], [ 1, 0,-1], [-1,-1,-1], [ 0,-1,-1], [ 1,-1,-1]
        ]
    }

    PAWN = {
        Piece.WHITE: {
            Piece.MOVE: [
                [ 0, 1, 0], [ 0, 1, 1], [ 0, 1,-1], [ 0, 0, 1], [ 0, 0,-1]
            ],
            Piece.UNMOVED: [
                [ 0, 2, 0], [ 0, 2, 2], [ 0, 2,-2]
            ],
            Piece.TAKE: [
                [-1, 1,-1], [-1, 1, 0], [-1, 1, 1], [ 1, 1,-1], [ 1, 1, 0], [ 1, 1, 1]
            ]
        },
        Piece.BLACK: {
            Piece.MOVE: [
                [ 0,-1, 0], [ 0,-1, 1], [ 0,-1,-1], [ 0, 0, 1], [ 0, 0,-1]
            ],
            Piece.UNMOVED: [
                [ 0,-2, 0], [ 0,-2, 2], [ 0,-2,-2]
            ],
            Piece.TAKE: [
                [-1,-1,-1], [-1,-1, 0], [-1,-1, 1], [ 1,-1,-1], [ 1,-1, 0], [ 1,-1, 1]
            ]
        }
    }

    @staticmethod
    def index_in_bounds(index):
        return True if index >= 0 and index < 192 else False

    @staticmethod
    def vector_in_bounds(vector):
        return True if (
            0 <= vector[0] < 8 and
            0 <= vector[1] < 8 and
            0 <= vector[2] < 3
            ) else False

    @staticmethod
    def index_to_vector(index):
        return [ index % 8, index // 8 % 8, index // (8 * 8) ]

    @staticmethod
    def vector_to_index(vector):
        return vector[0] % 8 + ((vector[1] % 8) * 8) + ((vector[2] % 8) * 8 * 8)

    @staticmethod
    def encode_piece(side, rank, state):
        return (side.value + rank.value + state.value)

    @staticmethod
    def decode_piece(byte):
        side = Piece(byte // 127 * 127)
        rank = Piece((byte - side.value) // 12 * 12)
        state = Piece(byte - side.value - rank.value)
        return [side, rank, state]

    def __init__(self, start_file = None):
        self.data = bytearray(192)
        self.masks = {}
        self.current_mask = -1

        if start_file: self.load(start_file)

    def load(self, file):
        with open(file, "r") as f:
            board_data = f.readline()
        self.data = bytearray.fromhex(board_data)

    def get_piece(self, index):
        return None if not Board.index_in_bounds(index) else self.data[index]

    def set_piece(self, index, value):
        if self.index_in_bounds(index): self.data[index] = value

    def get_mask(self, index):
        return False if not Board.index_in_bounds(index) or self.current_mask == -1 \
        else self.masks[self.current_mask][index]

    def set_mask(self, mask_index, index, value):
        if not mask_index in self.masks:
            self.masks[mask_index] = 192 * bitarray([False])
        self.masks[mask_index][index] = value

    def gen_move_mask(self, index):

        new_mask = 192 * bitarray([False])

        pos = Board.index_to_vector(index)
        piece = self.get_piece(index)
        side, rank, state = Board.decode_piece(piece)

        if rank == Piece.PAWN:

            for move_or_take in Board.PAWN[side]:

                for offset in Board.PAWN[side][move_or_take]:

                    new_pos = [pos[i] + offset[i] for i in range(3)]
                    if Board.vector_in_bounds(new_pos):

                        new_index = Board.vector_to_index(new_pos)
                        new_piece = self.get_piece(new_index)
                        new_side, new_rank, new_state = Board.decode_piece(new_piece)

                        if move_or_take == Piece.TAKE:
                            if new_piece != Piece.EMPTY.value and new_side != side:
                                new_mask[new_index] = True

                        elif move_or_take == Piece.MOVE or move_or_take == state:
                            if new_piece == Piece.EMPTY.value:
                                new_mask[new_index] = True

        elif rank in Board.MOVE_TAKE_POINT:

            for offset in Board.MOVE_TAKE_POINT[rank]:

                new_pos = [pos[i] + offset[i] for i in range(3)]
                if Board.vector_in_bounds(new_pos):

                    new_index = Board.vector_to_index(new_pos)
                    new_piece = self.get_piece(new_index)
                    new_side, new_rank, new_state = Board.decode_piece(new_piece)
                    if (new_piece != Piece.EMPTY.value and new_side != side) or new_piece == Piece.EMPTY.value:

                            new_mask[new_index] = True

        elif rank in Board.MOVE_TAKE_DIRECTION:

            for direction in Board.MOVE_TAKE_DIRECTION[rank]:

                for distance in range(1,8):

                    extension = [direction[i] * distance for i in range(3)]
                    new_pos = [pos[i] + extension[i] for i in range(3)]
                    if Board.vector_in_bounds(new_pos):

                        new_index = Board.vector_to_index(new_pos)
                        new_piece = self.get_piece(new_index)
                        new_side, new_rank, new_state = Board.decode_piece(new_piece)

                        if new_piece != Piece.EMPTY.value:
                            if new_side != side:
                                new_mask[new_index] = True
                            break
                        else:
                            new_mask[new_index] = True

                    else:
                        break
        return new_mask

    def select_piece(self, index):
        if self.get_piece(index) != Piece.EMPTY.value:
            if not index in self.masks:
                self.masks[index] = self.gen_move_mask(index)
            self.current_mask = index
        else:
            self.current_mask = -1

    def move_piece(self, piece_pos, new_piece_pos):
        index = Board.vector_to_index(piece_pos)
        index_new = Board.vector_to_index(new_piece_pos)
        if index in self.masks and self.masks[index][index_new] == True:
            piece = self.get_piece(index)
            self.set_piece(index, Piece.EMPTY.value)
            self.set_piece(index_new, piece)
            self.masks.clear()
            self.current_mask = -1

class MultilevelChess:

    def __init__(self):
        self.board = Board("board_start.dat")
        self.old_select_pos =   [ 0, 0, 0]
        self.select_pos =       [ 0, 0, 0]
        self.selected = False

    def get_board_at(self, x, y, z):
        index = Board.vector_to_index([x,y,z])
        mask = self.board.get_mask(index)
        raw = self.board.get_piece(index)
        value = Board.decode_piece(raw)
        return [value[0].value // 127, (value[1].value // 12) - 1, mask]

    def get_select_pos(self):
        return self.select_pos

    def set_select_pos(self, value):
        if Board.vector_in_bounds(value):
            self.select_pos = value
            if not self.selected:
                self.board.select_piece(Board.vector_to_index(self.select_pos))

    def set_select(self, value):
        if not self.selected:
            if value:
                self.board.select_piece(Board.vector_to_index(self.select_pos))
                self.old_select_pos = self.select_pos
            else:
                self.current_mask = -1
            self.selected = True
        else:
            self.board.move_piece(self.old_select_pos, self.select_pos)
            self.selected = False
