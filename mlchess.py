"""

mlchess.py
Muli-level chess
Samuel Bauman 2020

"""

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
    CHECK_UNMOVED   =   5
    CHECK_NORMAL    =   6
    CHECKMATE       =   7

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

        """ Returns true if the index position is a valid position """

        return True if index >= 0 and index < 192 else False


    @staticmethod
    def vector_in_bounds(vector):

        """ Returns true if the list of X,Y,Z values represents a valid position """

        return 0 <= vector[0] < 8 and 0 <= vector[1] < 8 and 0 <= vector[2] < 3


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

        """ Converts an encoded piece byte value (0-255) to side, rank, and state enumeration values """

        side = Piece(byte // 127 * 127)
        rank = Piece((byte - side.value) // 12 * 12)
        state = Piece(byte - side.value - rank.value)
        return [side, rank, state]


    def __init__(self, start_file = None, start_turn = Piece.WHITE):

        self.data = bytearray(192)
        self.masks = {}
        self.current_mask = -1
        self.king = {}
        self.turn = start_turn

        if start_file: self.load(start_file)

    def load(self, file):

        """ Loads a saved board file in hex form and converts it to binary piece values """

        with open(file, "r") as f:
            board_data = f.readline()
        self.data = bytearray.fromhex(board_data)

        # Finds the white and black king piece index values from loaded game
        self.king[Piece.WHITE] = next(
            i for i in range(192) if Board.decode_piece(self.data[i])[:2] == [Piece.WHITE, Piece.KING]
        )
        self.king[Piece.BLACK] = next(
            i for i in range(192) if Board.decode_piece(self.data[i])[:2] == [Piece.BLACK, Piece.KING]
        )

    def get_piece(self, index):

        """ Returns the encoded piece byte value at the given index position """

        return Piece.EMPTY.value if not Board.index_in_bounds(index) else self.data[index]


    def set_piece(self, index, value):

        """ Sets the encoded piece byte value at the given index position """

        if self.index_in_bounds(index): self.data[index] = value

    def get_info(self, index):
        info = Board.decode_piece(self.get_piece(index))
        return {"side": info[0], "rank": info[1], "state": info[2]}

    def is_empty(self, index):

        """ Determines if the board is empty at the given index position """

        return True if self.get_piece(index) == Piece.EMPTY.value else False


    def get_mask(self, index):

        """ Returns the mask bit for the given index. Used to determine if the index position is a legal move """

        return False if not Board.index_in_bounds(index) or self.current_mask == -1 \
        else self.masks[self.current_mask][index]


    def generate_move_mask(self, index, test_piece = None):

        """ Generates a movement mask for a particular piece and returns it. """

        # A movement mask can be associated with any piece on the board and indicates all of the possible legal moves
        # that piece can make. All movement masks are then stored in memory (in the board.masks dictionary) while the
        # player is deciding their move. All movement masks are cleared after each move. They are generated on an
        # as-needed basis as the player moves the cursor over pieces without an associated movement mask.

        # Generate a new blank mask for this piece.
        new_mask = 192 * bitarray([False])

        # Get information from the board about the current piece.
        pos = Board.index_to_vector(index)
        piece = self.get_piece(index) if test_piece == None else test_piece
        side, rank, state = Board.decode_piece(piece)


        # Determines the movement rules to be used for the selected piece. 
        # There are three categories of basic movement types: Pawn, offset, and direction.
        #
        # Pawns have unique moving/taking rules as it's mirrored for each side and they have seperate move and attack
        # positions.
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

            # Castling logic
            if rank == Piece.KING and state == Piece.UNMOVED:
                rook_king_side  = Board.vector_to_index([ pos[0] - 3, pos[1], pos[2] ])
                king_side_1     = Board.vector_to_index([ pos[0] - 2, pos[1], pos[2] ])
                king_side_2     = Board.vector_to_index([ pos[0] - 1, pos[1], pos[2] ])
                queen_side_1    = Board.vector_to_index([ pos[0] + 1, pos[1], pos[2] ])
                queen_side_2    = Board.vector_to_index([ pos[0] + 2, pos[1], pos[2] ])
                queen_side_3    = Board.vector_to_index([ pos[0] + 3, pos[1], pos[2] ])
                rook_queen_side = Board.vector_to_index([ pos[0] + 4, pos[1], pos[2] ])

                # Check kingside castling
                if (self.is_empty(king_side_1) and self.is_empty(king_side_2) and
                    self.get_info(rook_king_side)["state"] == Piece.UNMOVED):
                    new_mask[king_side_1] = True

                # Check queenside castling
                if (self.is_empty(queen_side_1) and self.is_empty(queen_side_2) and self.is_empty(queen_side_3) and
                    self.get_info(rook_queen_side)["state"] == Piece.UNMOVED):
                    new_mask[queen_side_2] = True

        elif rank in Board.MOVE_TAKE_DIRECTION:

            for direction in Board.MOVE_TAKE_DIRECTION[rank]:

                for distance in range(1,8):

                    extension = [direction[i] * distance for i in range(3)]
                    new_pos = [pos[i] + extension[i] for i in range(3)]
                    if Board.vector_in_bounds(new_pos):

                        new_index = Board.vector_to_index(new_pos)
                        new_piece = self.get_piece(new_index)
                        new_side, new_rank, new_state = Board.decode_piece(new_piece)

                        if new_piece != Piece.EMPTY.value and new_side != side:
                            new_mask[new_index] = True
                            break
                        elif new_piece == Piece.EMPTY.value:
                            new_mask[new_index] = True
                        else:
                            break

                    else:
                        break

        # Iterates through all mask bits in the newly generated mask and removes all locations that would result in 
        # check for this player.
        if not test_piece:
            for i in range(192):
                if new_mask[i]:
                    check = self.move_results_in_check(side,index,i)
                    new_mask[i] = not check

        return new_mask


    def select_piece(self, index):

        """ Show the movement mask for a particular piece """

        # If there is no piece at the selected index position, set the movement mask to -1, which results in a mask of 
        # all 0s.
        #
        # If there is a piece at the selected index but no mask exists, generate a new mask using gen_move_mask and add
        # it to the masks dictionary. The mask dictionary should be cleared after each turn as it will need to be
        # updated.
        if self.get_piece(index) != Piece.EMPTY.value:
            if index not in self.masks:
                self.masks[index] = self.generate_move_mask(index)
            self.current_mask = index
        else:
            self.current_mask = -1


    def move_piece(self, from_pos, to_pos, update_turn = True, castle_move = False):

        """ Moves the current piece in 'from_pos' to 'to_pos'. Does not check for legality but assumes move is based
        on legal movement masks already generated. """

        # Gets the index values for the from and to positions.
        from_index = Board.vector_to_index(from_pos)
        to_index = Board.vector_to_index(to_pos)

        # Proceeds with movement if from_index has a movement mask and the to_index is listed as a legal move in the
        # from_index movement mask.
        if not castle_move and from_index not in self.masks:
            self.masks[from_index] = self.generate_move_mask(from_index)

        if castle_move or self.masks[from_index][to_index] == True:

            # Gets piece information.
            piece = self.get_piece(from_index)
            side, rank, state = Board.decode_piece(piece)

            # Update piece state to normal if previously unmoved or in check.
            if state in [Piece.UNMOVED, Piece.CHECK_UNMOVED, Piece.CHECK_NORMAL]:
                state = Piece.NORMAL

            # Update local king index variable.
            if rank == Piece.KING:
                self.king[side] = to_index
                # Check if move is a castle move and move rook accordingly.

                # Check king side castling.
                if to_pos[0] == from_pos[0] - 2:
                    rook_from = [from_pos[0] - 3, from_pos[1], from_pos[2]]
                    rook_to = [from_pos[0] - 1, from_pos[1], from_pos[2]]
                    self.move_piece(rook_from, rook_to, False, True)

                # Check queen side castling.
                elif to_pos[0] == from_pos[0] + 2:
                    rook_from = [from_pos[0] + 4, from_pos[1], from_pos[2]]
                    rook_to = [from_pos[0] + 1, from_pos[1], from_pos[2]]
                    self.move_piece(rook_from, rook_to, False, True)


            # Encode the piece information.
            updated_piece = Board.encode_piece(rank, side, state)

            # Update board data.
            self.set_piece(from_index, Piece.EMPTY.value)
            self.set_piece(to_index, updated_piece)

            # Clear and reset movement masks for next turn.
            self.masks.clear()
            self.current_mask = -1

            # Update the check/checkmate state of both kings after each move.
            for check_side in [Piece.WHITE, Piece.BLACK]:
                king_index = self.king[check_side]
                king_state = self.get_info(king_index)["state"]
                if self.move_results_in_check(check_side, king_index, king_index):

                    # Check_side's king is in check, now test if it is checkmate by testing if any pieces have legal
                    # moves left.
                    checkmate = True
                    for i in range(192):
                        if not self.is_empty(i) and self.get_info(i)["side"] == check_side:
                            if self.generate_move_mask(i).count() > 0:
                                checkmate = False
                                break

                    if checkmate:
                        new_check_state = Piece.CHECKMATE
                        self.turn = Piece.CHECKMATE
                    else:
                        new_check_state =\
                        Piece.CHECK_NORMAL if king_state in [Piece.NORMAL, Piece.CHECK_NORMAL] else Piece.CHECK_UNMOVED

                    # Finally, update king's state to checkmate or just check.
                    self.set_piece(king_index, Board.encode_piece(check_side, Piece.KING, new_check_state))

            # Change turn.
            if update_turn and not self.turn == Piece.CHECKMATE:
                self.turn = Piece.BLACK if self.turn == Piece.WHITE else Piece.WHITE

                ## To-do: Send turn to opponent player here in a socketserver game

    def move_results_in_check(self, king_side, from_index, to_index):

        """ Performs a temporary move to determine if that move would result in check """

        from_piece = self.get_piece(from_index)
        to_piece = self.get_piece(to_index)

        self.set_piece(from_index, Piece.EMPTY.value)
        self.set_piece(to_index, from_piece)

        result = False

        king_index = self.king[king_side]
        opponent_side = Piece.WHITE if king_side == Piece.BLACK else Piece.BLACK
        if king_index == from_index: king_index = to_index

        for test_rank in [Piece.PAWN, Piece.BISHOP, Piece.KNIGHT, Piece.ROOK, Piece.QUEEN, Piece.KING]:
            test_mask = self.generate_move_mask(
                king_index,
                Board.encode_piece(king_side, test_rank, Piece.NORMAL)
            )
            for index in range(192):
                if test_mask[index] and not self.is_empty(index):
                    if Board.decode_piece(self.get_piece(index))[:2] == [opponent_side, test_rank]:
                        result = True
                        break
            if result: break

        self.set_piece(from_index, from_piece)
        self.set_piece(to_index, to_piece)

        return result


class MultilevelChess:

    """ Class used for abstracting some of the game logic and interfacing with tmlchess.py. """

    def __init__(self, player_sides):
        self.board = Board("board_start.dat")
        self.old_select_pos =   [ 0, 0, 0]
        self.select_pos =       [ 0, 0, 0]
        self.selected = False
        self.sides = player_sides

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
        piece_side = Board.decode_piece(self.board.get_piece(Board.vector_to_index(self.select_pos)))[0]
        empty_piece = self.board.is_empty(Board.vector_to_index(self.select_pos))
        if not empty_piece and piece_side == self.board.turn and self.board.turn in self.sides:
            self.board.select_piece(Board.vector_to_index(self.select_pos))
            self.old_select_pos = self.select_pos
            self.selected = True
        elif self.board.turn in self.sides:
            self.board.move_piece(self.old_select_pos, self.select_pos, True)
            self.selected = False
        else:
            self.selected = False
