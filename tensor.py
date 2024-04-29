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


def generate_input_tensor(board, history):
    # Create base tensor with shape for 8 plies (current + 7 historical)
    tensor_shape = (6 * 2 + 1, 8, 8)  # 6 piece types * 2 colors + 1 repetition layer
    full_tensor = np.zeros((tensor_shape[0] * 8 + 6, 8, 8), dtype=int)  # Adding castling rights, isBlackMove, and 50moveRuleCounter

    # Fill tensor for current and historical board states
    for i in range(8):
        if i < len(history):
            current_board = history[i]
        else:
            current_board = board if i == 0 else chess.Board('8/8/8/8/8/8/8/8 w - - 0 1')  # Empty board for excess history

        chess_tensor = ChessTensor()
        chess_tensor.parse_fen(current_board.fen())
        board_tensor = chess_tensor.get_tensor()[:12, :, :]  # Ignore castling and en passant layers from ChessTensor

        # Stack the current board tensor in the correct position
        full_tensor[i * 13:(i + 1) * 13 - 1, :, :] = board_tensor  # Place piece info, skipping last repetition layer

    # Add castling rights
    castling = [0] * 4
    if board.has_kingside_castling_rights(chess.WHITE):
        castling[0] = 1
    if board.has_queenside_castling_rights(chess.WHITE):
        castling[1] = 1
    if board.has_kingside_castling_rights(chess.BLACK):
        castling[2] = 1
    if board.has_queenside_castling_rights(chess.BLACK):
        castling[3] = 1
    full_tensor[104:108, 0, 0] = castling

    # Add isBlackMove
    full_tensor[108, 0, 0] = int(board.turn == chess.BLACK)

    # Add 50-move rule counter (all zeros, as specified)
    full_tensor[109, :, :] = 0

    return full_tensor


def print_board(board):
    # Simple function to print the chess board
    print(board)


def print_tensor_slice(tensor, layer):
    # Print a specific slice of the tensor
    print("Tensor slice for layer {}:".format(layer))
    print(tensor[layer])


def visualize_tensor(tensor):
    # Function to visualize part of the tensor for quick inspection
    print("Visualizing initial layers of the tensor:")
    for i in range(12):  # Only visualize the first 12 layers (6 pieces x 2 colors)
        print_tensor_slice(tensor, i)


def main():
    # Initialize the chess board and history
    board = chess.Board()
    history = [board.copy() for _ in range(7)]  # Example historical data

    # Generate the tensor
    tensor = generate_input_tensor(board, history)

    # Test the tensor
    print("Tensor shape:", tensor.shape)
    print("Data type:", tensor.dtype)

    # Print the board
    print_board(board)

    # Visualize part of the tensor
    visualize_tensor(tensor)

    # Further checks could include specific game scenarios
    board.push_san("e4")
    history.append(board.copy())
    tensor_updated = generate_input_tensor(board, history[-8:])
    print("Updated board after move 'e4':")
    print_board(board)
    print("Visualizing updated tensor:")
    visualize_tensor(tensor_updated)


if __name__ == "__main__":
    main()

