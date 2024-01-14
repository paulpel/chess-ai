import numpy as np
import chess

class ChessTensor:
    def __init__(self):
        # 14 layers: 12 for pieces, 1 for castling rights, 1 for en passant
        self.tensor = np.zeros((14, 8, 8), dtype=bool)

    def piece_index(self, piece):
        """ Returns the index of the piece in the tensor. """
        piece_order = 'PRNBQKprnbqk'
        return piece_order.index(piece)

    def parse_fen(self, fen):
        """ Parse a FEN string and update the tensor accordingly. """
        self.tensor.fill(0)  # Reset tensor
        board, turn, castling, en_passant, _, _ = fen.split(" ")

        # Fill piece layers
        rows = board.split("/")
        for i, row in enumerate(rows):
            col = 0
            for char in row:
                if char.isdigit():
                    col += int(char)
                else:
                    index = self.piece_index(char)
                    self.tensor[index][7 - i][col] = True
                    col += 1

        # Fill castling rights layer
        castling_rights_layer = 12
        if 'K' in castling: self.tensor[castling_rights_layer][7][7] = True  # White king-side
        if 'Q' in castling: self.tensor[castling_rights_layer][7][0] = True  # White queen-side
        if 'k' in castling: self.tensor[castling_rights_layer][0][7] = True  # Black king-side
        if 'q' in castling: self.tensor[castling_rights_layer][0][0] = True  # Black queen-side

        # Fill en passant layer
        en_passant_layer = 13
        if en_passant != "-":
            file = ord(en_passant[0]) - ord('a')
            rank = 8 - int(en_passant[1])
            self.tensor[en_passant_layer][rank][file] = True

    def get_tensor(self):
        """ Returns the tensor representation of the board. """
        return self.tensor
