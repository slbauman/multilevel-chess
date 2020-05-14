from enum import Enum
from bitarray import bitarray

class Piece(Enum):

    """ A helper class for the Board class """

    # Enumeration values are used to encode and decode piece information.

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

    """ This class contains the logic to store and move pieces in a multi-level chess game """


    # The direction vectors used by queen, bishop, and rook movement.

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


    # The offset positions used by knight and king movement.

    MOVE_TAKE_OFFSET = {
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


    # The offset positions separated by moving and taking and by side used by pawns.

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

        """ Returns true if the index position is a valid position on the boards """

        return True if index >= 0 and index < 192 else False


    @staticmethod
    def vector_in_bounds(vector):

        """ Returns true if the list of X,Y,Z values represents a valid position on the boards """

        return True if (
            0 <= vector[0] < 8 and
            0 <= vector[1] < 8 and
            0 <= vector[2] < 3
            ) else False


    @staticmethod
    def index_to_vector(index):

        """ Converts index position to list containing X,Y,Z values """

        return [ index % 8, index // 8 % 8, index // (8 * 8) ]


    @staticmethod
    def vector_to_index(vector):

        """ Converts a list of X,Y,Z values to a index position value. eg.:  [ 7, 7, 2] -> 191 """

        return vector[0] % 8 + ((vector[1] % 8) * 8) + ((vector[2] % 8) * 8 * 8)


    @staticmethod
    def encode_piece(side, rank, state):

        """ Converts a piece's side, rank, and state information into an encoded byte value (0-255) """

        return (side.value + rank.value + state.value)


    @staticmethod
    def decode_piece(byte):

        """ Converts a encode piece byte value (0-255) to side, rank, and state enumeration values """

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

        """ Loads a saved board file in hex form and converts it to binary piece values """

        with open(file, "r") as f:
            board_data = f.readline()
        self.data = bytearray.fromhex(board_data)


    def get_piece(self, index):

        """ Returns the encoded piece byte value at the given index position """

        return None if not Board.index_in_bounds(index) else self.data[index]


    def set_piece(self, index, value):

        """ Sets the encoded piece byte value at the given index position """

        if self.index_in_bounds(index): self.data[index] = value


    def get_mask(self, index):

        """ Returns the mask bit for the given index. Used to determine if the index position is a legal move """

        return False if not Board.index_in_bounds(index) or self.current_mask == -1 \
        else self.masks[self.current_mask][index]


    def generate_move_mask(self, index):

        """ Generates a movement mask for a particular piece and returns it. """

        # A movement mask can be associated with any piece on the board and indicates all of the possible legal moves
        # that piece can make. All movement masks are then stored in memory (in the board.masks dictionary) while the
        # player is deciding their move. All movement masks are cleared after each move. They are generated in an
        # as-needed basis as the player moves the cursor over a piece without an associated movement mask.

        # Generate a new blank mask for this piece.
        new_mask = 192 * bitarray([False])

        # Get information from the board about the current piece.
        pos = Board.index_to_vector(index)
        piece = self.get_piece(index)
        side, rank, state = Board.decode_piece(piece)


        # Determines the movement rules to be used for the selected piece. 
        # There are three categories of basic movement types: Pawn, offset, and direction.
        #
        # Pawns have unique moving/taking rules as it's mirrored for each side and they have seperate move and attack
        # squares.
        #
        # Offset movement refers to how knights kings move. They move to a specific offset relative to their position.
        #
        # Direction movement refers to queen, rook, and bishop movement as they move/take along multiple directions.

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

        elif rank in Board.MOVE_TAKE_OFFSET:

            for offset in Board.MOVE_TAKE_OFFSET[rank]:

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

        """ Show the movement mask for a particular piece. """

        # If there is no piece at the selected index position, set the movement mask to -1, which results in a mask of 
        # all 0s.
        #
        # If there is a piece at the selected index but no mask exists, generate a new mask using gen_move_mask and add
        # it to the masks dictionary. The mask dictionary should be cleared after each move as it will need to be
        # updated.

        if self.get_piece(index) != Piece.EMPTY.value:
            if not index in self.masks:
                self.masks[index] = self.generate_move_mask(index)
            self.current_mask = index
        else:
            self.current_mask = -1


    def move_piece(self, from_pos, to_pos):

        """ Moves the current piece in 'from_pos' to 'to_pos' """

        # Gets the index values for the from and to positions
        from_index = Board.vector_to_index(from_pos)
        to_index = Board.vector_to_index(to_pos)

        # Proceeds with movement if from_index has a movement mask and the to_index is listed as a legal move in the
        # from_index movement mask.
        if from_index in self.masks and self.masks[from_index][to_index] == True:

            # Gets piece information
            piece = self.get_piece(from_index)
            rank, side, state = Board.decode_piece(piece)

            # Update state to normal if previously unmoved
            if state == Piece.UNMOVED: state = Piece.NORMAL

            # Encode the piece information
            updated_piece = Board.encode_piece(rank, side, state)

            # Update board data
            self.set_piece(from_index, Piece.EMPTY.value)
            self.set_piece(to_new, updated_piece)

            # Clear and reset movement masks for next turn
            self.masks.clear()
            self.current_mask = -1



class MultilevelChess:

    """ Class used for abstracting some of the game logic and interfacing with tmlchess.py """

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
