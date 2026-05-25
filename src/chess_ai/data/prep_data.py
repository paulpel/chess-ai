import chess
import chess.pgn
import requests


def download_games(player_id, max_games=100, filename="games.pgn"):
    url = f"https://lichess.org/api/games/user/{player_id}"
    params = {"max": max_games, "pgnInJson": False}
    response = requests.get(url, params=params)

    with open(filename, "w") as file:
        file.write(response.text)

    print(f"Games saved to {filename}")


def extract_data_for_training(filename):
    white_data, black_data = [], []
    with open(filename) as f:
        while True:
            game = chess.pgn.read_game(f)
            if game is None:
                break

            board = chess.Board()
            move_history = []

            for i, move in enumerate(game.mainline_moves()):
                if i >= 3:
                    if board.turn == chess.WHITE:
                        white_data.append((board.fen(), list(move_history), move.uci()))
                    else:
                        black_data.append((board.fen(), list(move_history), move.uci()))

                    move_history.append(move.uci())
                    move_history.pop(0)  # Keep only the last 3 moves

                board.push(move)

    return white_data, black_data


def fen_to_matrix(fen):
    """Convert the board part of a FEN string to an 8x8 matrix of signed ints.

    White pieces are positive, black pieces negative, empty squares 0.
    """
    piece_to_num = {
        "r": -5,
        "n": -4,
        "b": -3,
        "q": -2,
        "k": -1,
        "p": -6,
        "R": 5,
        "N": 4,
        "B": 3,
        "Q": 2,
        "K": 1,
        "P": 6,
        ".": 0,
    }

    board_fen = fen.split(" ")[0]
    matrix = []
    for row in board_fen.split("/"):
        matrix_row = []
        for char in row:
            if char.isdigit():
                matrix_row.extend([0] * int(char))
            else:
                matrix_row.append(piece_to_num[char])
        matrix.append(matrix_row)
    return matrix
