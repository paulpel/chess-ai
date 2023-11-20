import chess.pgn
import random
import io
import numpy as np
import torch
import requests


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


def get_random_games_from_player(username, num_games=100):
    url = f"https://lichess.org/api/games/user/{username}"
    params = {
        'max': num_games,
        'perfType': 'blitz',
        'pgnInJson': False
    }
    response = requests.get(url, params=params)

    if response.status_code != 200:
        print("Failed to fetch data: ", response.status_code)
        print(response.text)  # Print the response content
        return []

    pgn_data = response.text
    games = pgn_data.strip().split('\n\n\n')  # Split the PGN data into separate games

    # Randomly select games if more than num_games
    if len(games) > num_games:
        games = random.sample(games, num_games)

    annotated_games = []
    for game in games:
        game_lines = game.split('\n')
        color = 'white' if any('[White "{}"]'.format(username) in line for line in game_lines) else 'black'
        annotated_games.append((game, color))

    return annotated_games


def extract_all_fens_from_pgn(pgn_text):
    """Extract random FEN positions from a game's PGN where the specified player is on the move"""
    pgn = chess.pgn.read_game(io.StringIO(pgn_text))
    game_positions = []
    board = pgn.board()
    for move in pgn.mainline_moves():
        game_positions.append(board.fen())
        board.push(move)
    return game_positions


def get_games(username, num_games=100):
    """Get random positions from a user's games"""
    games = get_random_games_from_player(username, num_games)
    all_games = []
    colors = []
    for game in games:
        # print(game)
        pgn_text = game[0]
        player_color = game[1]
        positions = extract_all_fens_from_pgn(pgn_text)

        all_games.append(positions)
        colors.append(player_color)
        # print(player_color, positions)
    return all_games, colors


def generate_possible_fens_positions(fen):
    board = chess.Board(fen)
    fen_positions = []

    for move in board.legal_moves:
        board.push(move)  # Make the move
        fen_positions.append(board.fen())  # Get the FEN string for new board
        board.pop()  # Undo the move

    return fen_positions


def create_stacked_set_from_game(game, color, stack_size=2, add_other_legal_moves=True):
    """
    Create a list of stacked board representations from a game's FEN strings.

    :param game: List of FEN strings representing the game states.
    :param color: The color of a player
    :param stack_size: The number of consecutive positions to stack.
    :return: List of tensors, each containing 'stack_size' number of board states stacked along the channel dimension.
    """

    # Convert each FEN to its tensor representation
    # tensor_game = [ChessPositionRepresentation(fen).to_tensor() for fen in game]

    stacked_sets = []

    if color == 'white':
        skip_last_pos = 0
        if len(game) % 2 == 1:  # When white lost
            skip_last_pos = 1
        for i in range(0, len(game) - skip_last_pos, 2):
            # indexes = []
            stack = [game[i+1]]  # Result position
            # indexes.append(i+1)
            for j in range(stack_size - 1):
                index = max(i - 2*j, 0)  # Current and previous positions
                stack.append(game[index])
                # indexes.append(index)
            # Concatenate the selected tensors along the channel dimension
            # stacked_tensor = torch.cat(stack, dim=0)
            stacked_sets.append(stack)
            # print(color, indexes)
    elif color == 'black':
        skip_last_pos = 0
        if len(game) % 2 == 0:  # When black lost
            skip_last_pos = 1
        for i in range(1, len(game) - skip_last_pos, 2):
            # indexes = []
            stack = [game[i + 1]]  # Result position
            # indexes.append(i+1)
            for j in range(stack_size - 1):
                index = max(i - 2 * j, 0)  # Current and previous positions
                stack.append(game[index])
                # indexes.append(index)
            # Concatenate the selected tensors along the channel dimension
            # stacked_tensor = torch.cat(stack, dim=0)
            stacked_sets.append(stack)
            # print(color, indexes)
    print(len(stacked_sets))

    # Generating possible positions from every move if add_other_legal_moves = True
    if add_other_legal_moves:
        new_stacked_sets = []
        target_values = []
        for i, stacked_set in enumerate(stacked_sets):
            new_stacked_sets.append(stacked_set)
            target_values.append(1.0)

            possible_positions = generate_possible_fens_positions(stacked_set[1])
            short_possible_positions = random.sample(possible_positions, min(4, len(possible_positions)))
            for j in range(len(short_possible_positions)):
                # print(short_possible_positions[j], '\n', stacked_set[0], True if short_possible_positions[j] == stacked_set[0] else False)
                if short_possible_positions[j] != stacked_set[0]:
                    new_stacked_set = stacked_set.copy()
                    new_stacked_set[0] = short_possible_positions[j]

                    new_stacked_sets.append(new_stacked_set)
                    target_values.append(0.0)
                    # print(i, j, new_stacked_set)
        print(target_values)
        return new_stacked_sets
    return stacked_sets


def get_games_as_a_set(games, colors, previous_moves=3, add_other_legal_moves=True):
    """
    Returns list of a processed games - tensors of size 8x8x(14 times stack_size). It represents the board state (8x8).
    14 is the number of channel (2 are for pawns, 2 for rooks..., 1 for castling and 1 for en passant). The list is as follows:
    [move played by player, current pos, prevoius moves] The number of previous moves is indicated by previous_moves

    :param games: List of games. Game is list of positions in FEN notation.
    :param previous_moves: Number of moves done before current position
    :return: Processed games as list of tensors.
    """


    games_set = []
    for idx, game in enumerate(games):
        stacked_game = create_stacked_set_from_game(game,
                                                    colors[idx],
                                                    stack_size=previous_moves+2,
                                                    add_other_legal_moves=True)
        games_set.extend(stacked_game)
    return games_set


fen_games, colors = get_games('chesstacion', 100)
games = get_games_as_a_set(fen_games, colors, 3)
