import numpy as np
import chess

class ChessTensor:
    def __init__(self):
        self.tensor = np.zeros((12, 8, 8), dtype=bool)  # 12 layers: one for each piece type and color

    def piece_index(self, piece):
        piece_order = 'PRNBQKprnbqk'  # Order: White Pawn, Rook, Knight, Bishop, Queen, King, then Black
        return piece_order.index(piece)

    def parse_fen(self, fen):
        self.tensor.fill(0)  # Reset tensor before updating
        board, _, _, _, _, _ = fen.split(" ")
        rows = board.split("/")
        for row_index, row in enumerate(rows):
            col_index = 0
            for char in row:
                if char.isdigit():
                    col_index += int(char)  # Skip empty squares
                else:
                    index = self.piece_index(char)
                    self.tensor[index][row_index][col_index] = True
                    col_index += 1

    def get_tensor(self):
        return self.tensor

def generate_full_input_tensor(board, history):
    # print(len(history))
    full_tensor = np.zeros((112, 8, 8), dtype=int)

    # Initialize and fill tensor for current and historical board states
    history_length = len(history)
    total_plies = 8  # We consider the current board and up to 7 past states

    for i in range(total_plies):
        chess_tensor = ChessTensor()
        if i == 0:
            # Current board state
            chess_tensor.parse_fen(board.fen())
        elif i <= history_length:
            # Historical board states that exist
            chess_tensor.parse_fen(history[-i].fen())
        else:
            # For non-existent past states, the tensor remains zero filled
            pass
        full_tensor[i * 13:(i + 1) * 13 - 1, :, :] = chess_tensor.get_tensor()

    # Castling and game state layers
    full_tensor[104, :, :] = board.has_kingside_castling_rights(chess.WHITE)
    full_tensor[105, :, :] = board.has_queenside_castling_rights(chess.WHITE)
    full_tensor[106, :, :] = board.has_kingside_castling_rights(chess.BLACK)
    full_tensor[107, :, :] = board.has_queenside_castling_rights(chess.BLACK)
    full_tensor[108, :, :] = int(board.turn == chess.BLACK)  # IsBlackMove layer
    full_tensor[109, :, :] = 0  # 50-Move Rule Counter
    full_tensor[110, :, :] = 0  # ???
    full_tensor[111, :, :] = 1 # ???

    return full_tensor

