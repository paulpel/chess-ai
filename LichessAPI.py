import lichess.api
import lichess.pgn
import chess.pgn
import random
import io
import numpy as np
import torch


class ChessPositionRepresentation:
    def __init__(self, fen):
        # Initialize boards for each piece type
        self.white_pawns = np.zeros((8, 8), dtype=bool)
        self.white_rooks = np.zeros((8, 8), dtype=bool)
        self.white_knights = np.zeros((8, 8), dtype=bool)
        self.white_bishops = np.zeros((8, 8), dtype=bool)
        self.white_queens = np.zeros((8, 8), dtype=bool)
        self.white_king = np.zeros((8, 8), dtype=bool)

        self.black_pawns = np.zeros((8, 8), dtype=bool)
        self.black_rooks = np.zeros((8, 8), dtype=bool)
        self.black_knights = np.zeros((8, 8), dtype=bool)
        self.black_bishops = np.zeros((8, 8), dtype=bool)
        self.black_queens = np.zeros((8, 8), dtype=bool)
        self.black_king = np.zeros((8, 8), dtype=bool)

        self.en_passant = np.zeros((8,8), dtype=bool)
        self.castling_rights = np.zeros((8,8), dtype=bool)

        self.set_positions(fen)

    def set_positions(self, fen):
        # Parse the FEN string and update the boards
        board = chess.Board(fen)
        fen_parts = fen.split(' ')

        # Reset the boards to 0
        self.white_pawns.fill(0)
        self.white_rooks.fill(0)
        self.white_knights.fill(0)
        self.white_bishops.fill(0)
        self.white_queens.fill(0)
        self.white_king.fill(0)
        self.black_pawns.fill(0)
        self.black_rooks.fill(0)
        self.black_knights.fill(0)
        self.black_bishops.fill(0)
        self.black_queens.fill(0)
        self.black_king.fill(0)
        self.en_passant.fill(0)
        self.castling_rights.fill(0)

        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                # Convert chess square index to 2D array indices
                row, col = divmod(square, 8)
                # Set 1 in the corresponding board based on piece type and color
                if piece.color == chess.WHITE:
                    if piece.piece_type == chess.PAWN:
                        self.white_pawns[row, col] = 1
                    elif piece.piece_type == chess.ROOK:
                        self.white_rooks[row, col] = 1
                    elif piece.piece_type == chess.KNIGHT:
                        self.white_knights[row, col] = 1
                    elif piece.piece_type == chess.BISHOP:
                        self.white_bishops[row, col] = 1
                    elif piece.piece_type == chess.QUEEN:
                        self.white_queens[row, col] = 1
                    elif piece.piece_type == chess.KING:
                        self.white_king[row, col] = 1
                else:
                    if piece.piece_type == chess.PAWN:
                        self.black_pawns[row, col] = 1
                    elif piece.piece_type == chess.ROOK:
                        self.black_rooks[row, col] = 1
                    elif piece.piece_type == chess.KNIGHT:
                        self.black_knights[row, col] = 1
                    elif piece.piece_type == chess.BISHOP:
                        self.black_bishops[row, col] = 1
                    elif piece.piece_type == chess.QUEEN:
                        self.black_queens[row, col] = 1
                    elif piece.piece_type == chess.KING:
                        self.black_king[row, col] = 1

        if 'K' in fen_parts[2]:
            self.castling_rights[7, 7] = 1  # White king-side
        if 'Q' in fen_parts[2]:
            self.castling_rights[7, 0] = 1  # White queen-side
        if 'k' in fen_parts[2]:
            self.castling_rights[0, 7] = 1  # Black king-side
        if 'q' in fen_parts[2]:
            self.castling_rights[0, 0] = 1  # Black queen-side

        # Parse en passant square from FEN
        if fen_parts[3] != '-':
            ep_square = chess.parse_square(fen_parts[3])
            ep_row, ep_col = divmod(ep_square, 8)
            self.en_passant[ep_row, ep_col] = 1

    def to_tensor(self):
        # Stack the individual boards and convert to a PyTorch tensor
        all_boards = [
            self.white_pawns, self.white_rooks, self.white_knights, self.white_bishops, self.white_queens,
            self.white_king,
            self.black_pawns, self.black_rooks, self.black_knights, self.black_bishops, self.black_queens,
            self.black_king,
            self.en_passant, self.castling_rights
        ]
        stacked_boards = np.stack(all_boards, axis=0)
        return torch.from_numpy(stacked_boards)

# class NNChessGameStateRepresentation:
    

def get_random_games_from_player(username, num_games=100):
    """Fetch random games of a player from Lichess"""
    games = list(lichess.api.user_games(username, max=num_games))
    return random.sample(games, min(num_games, len(games)))


def extract_all_fens_from_pgn(pgn_text, player_color):
    """Extract random FEN positions from a game's PGN where the specified player is on the move"""
    pgn = chess.pgn.read_game(io.StringIO(pgn_text))
    game_positions = []
    board = pgn.board()
    for move in pgn.mainline_moves():
        if (player_color == 'white' and board.turn) or (player_color == 'black' and not board.turn):
            game_positions.append(board.fen())
        board.push(move)
    return game_positions


def get_all_positions(username, player_color, num_games=100):
    """Get random positions from a user's games"""
    games = get_random_games_from_player(username, num_games)
    all_games = []
    for game in games:
        pgn_text = lichess.pgn.from_game(game)
        positions = extract_all_fens_from_pgn(pgn_text, player_color)
        all_games.append(positions)
    return all_games


# Sample usage
positions = get_all_positions('chesstacion', 'white', 20)
for idx, position in enumerate(positions):
    print(idx, position)

# Example usage
fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
chess_position = ChessPositionRepresentation(fen)
tensor_representation = chess_position.to_tensor()

print(tensor_representation.shape)  # Should print: torch.Size([14, 8, 8])
