import lichess.api
import lichess.pgn
import chess.pgn
import random
import io

def get_random_games_from_player(username, num_games=100):
    """Fetch random games of a player from Lichess"""
    games = list(lichess.api.user_games(username, max=num_games))
    return random.sample(games, min(num_games, len(games)))


def extract_random_fens_from_pgn(pgn_text, player_color, num_positions=5):
    """Extract random FEN positions from a game's PGN where the specified player is on the move"""
    pgn = chess.pgn.read_game(io.StringIO(pgn_text))
    positions = []
    board = pgn.board()
    for move in pgn.mainline_moves():
        if (player_color == 'white' and board.turn) or (player_color == 'black' and not board.turn):
            # Create a copy of the board
            board_copy = board.copy()
            # Push the move onto the copied board
            board_copy.push(move)
            # Store the original position and the position after the move
            positions.append((board.fen(), board_copy.fen()))
        board.push(move)
    return random.sample(positions, min(num_positions, len(positions)))


def get_random_positions(username, player_color, num_games=100, num_positions_per_game=5):
    """Get random positions from a user's games"""
    games = get_random_games_from_player(username, num_games)
    all_positions = []
    for game in games:
        pgn_text = lichess.pgn.from_game(game)
        positions = extract_random_fens_from_pgn(pgn_text, player_color, num_positions_per_game)
        all_positions.extend(positions)
    return all_positions

# Sample usage
positions = get_random_positions('chesstacion', 'white', 200, 5)
for idx, position_pair in enumerate(positions):
    print(idx, "Before:", position_pair[0], "After:", position_pair[1])
