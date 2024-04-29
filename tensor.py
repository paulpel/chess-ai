import numpy as np
import chess

class ChessTensor:
    def __init__(self):
        # 12 layers: One for each piece type for each color (6 types * 2 colors)
        self.tensor = np.zeros((12, 8, 8), dtype=bool)

    def piece_index(self, piece):
        """ Returns the index of the piece in the tensor. """
        piece_order = 'PRNBQKprnbqk'  # Order: White Pawn, Rook, Knight, Bishop, Queen, King, then Black
        return piece_order.index(piece)

    def parse_fen(self, fen):
        """ Parse a FEN string and update the tensor accordingly. """
        self.tensor.fill(0)  # Reset tensor
        board, _, _, _, _, _ = fen.split(" ")
        rows = board.split("/")
        for row_index, row in enumerate(rows):
            col_index = 0
            for char in row:
                if char.isdigit():
                    col_index += int(char)  # Empty squares
                else:
                    index = self.piece_index(char)
                    self.tensor[index][7 - row_index][col_index] = True
                    col_index += 1

    def get_tensor(self):
        """ Returns the tensor representation of the board. """
        return self.tensor

# Function to generate the full input tensor
def generate_full_input_tensor(board, history):
    # Initialize the full tensor
    full_tensor = np.zeros((110, 8, 8), dtype=int)  # 104 for pieces and IsRep, 4 for castling, 1 for isBlackMove, 1 for 50-move rule

    # Fill tensor for current and historical board states
    for i in range(8):
        current_board = history[i] if i < len(history) else board
        chess_tensor = ChessTensor()
        chess_tensor.parse_fen(current_board.fen())
        full_tensor[i * 13:(i + 1) * 13 - 1, :, :] = chess_tensor.get_tensor()  # Fill 12 layers, leave one layer for IsRep, which remains all zeros

    full_tensor[104, :, :] = board.has_kingside_castling_rights(chess.WHITE)
    full_tensor[105, :, :] = board.has_queenside_castling_rights(chess.WHITE)
    full_tensor[106, :, :] = board.has_kingside_castling_rights(chess.BLACK)
    full_tensor[107, :, :] = board.has_queenside_castling_rights(chess.BLACK)

    # IsBlackMove layer
    full_tensor[108, :, :] = int(board.turn == chess.BLACK)

    # 50-Move Rule layer (all zeros as specified)
    full_tensor[109, :, :] = 0

    return full_tensor

