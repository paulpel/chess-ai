import pygame
import chess
import os
from stockfish import Stockfish
import time
import random

# Adjust the path to your Stockfish executable
STOCKFISH_PATH = r"C:\Users\pawel\Desktop\Chess\stockfish\stockfish-windows-x86-64.exe"

stockfish = Stockfish(STOCKFISH_PATH)

# Initialize Pygame
pygame.init()

# Constants
BOARD_SIZE = 512  # Adjust as needed
SQUARE_SIZE = BOARD_SIZE // 8
FPS = 60

PANEL_WIDTH = 200  # Width of the side panel
OFFSET = 10
TOTAL_WIDTH = BOARD_SIZE + PANEL_WIDTH + OFFSET * 3
TOTAL_HEIGHT = BOARD_SIZE + OFFSET * 2

PIECES_PER_ROW = 4
GRID_CELL_SIZE = PANEL_WIDTH // PIECES_PER_ROW

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_SQUARE = (240, 217, 181)
DARK_SQUARE = (181, 136, 99)
BACKGROUND = (73, 57, 44)

WHITE_IS_HUMAN = True
BLACK_IS_HUMAN = False

dragging = False  # Flag to track if a piece is being dragged
dragged_piece = None  # Store the piece being dragged
dragged_piece_pos = (0, 0)  # Current position of the dragged piece
selected_square = None  # The starting square of the dragged piece
ai_fen_history = []


# Load images
def load_images():
    pieces = ["R", "N", "B", "Q", "K", "P"]
    colors = ["w", "b"]
    images = {}
    for piece in pieces:
        for color in colors:
            images[color + piece] = pygame.transform.scale(
                pygame.image.load(
                    os.path.join("images", f"{color}{piece.lower()}.png")
                ),
                (SQUARE_SIZE, SQUARE_SIZE),
            )
    small_images = {}
    for key, image in images.items():
        small_images[key] = pygame.transform.scale(
            image, (GRID_CELL_SIZE, GRID_CELL_SIZE)
        )
    return images, small_images


# Function to get square from mouse position
def get_square_from_mouse(pos):
    x, y = pos
    row = y // SQUARE_SIZE
    col = x // SQUARE_SIZE
    return chess.square(col, row)


# Draw the board
def draw_board(screen):
    colors = [LIGHT_SQUARE, DARK_SQUARE]
    for row in range(8):
        for col in range(8):
            color = colors[((row + col) % 2)]
            pygame.draw.rect(
                screen,
                color,
                pygame.Rect(
                    col * SQUARE_SIZE + OFFSET,
                    row * SQUARE_SIZE + OFFSET,
                    SQUARE_SIZE,
                    SQUARE_SIZE,
                ),
            )


# Draw the pieces on the board, skipping the dragged piece
def draw_pieces(screen, images, board):
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            # Check if this piece is being dragged
            if dragging and selected_square == square:
                continue  # Skip drawing this piece in its original position

            symbol = piece.symbol()
            if symbol.isupper():
                color = "w"
            else:
                color = "b"
            screen.blit(
                images[color + symbol.upper()],
                pygame.Rect(
                    (square % 8) * SQUARE_SIZE + OFFSET,
                    (square // 8) * SQUARE_SIZE + OFFSET,
                    SQUARE_SIZE,
                    SQUARE_SIZE,
                ),
            )


def get_captured_pieces(board):
    # Define the initial set of pieces for each player
    initial_pieces = {
        "w": [
            "R",
            "N",
            "B",
            "Q",
            "K",
            "B",
            "N",
            "R",
            "P",
            "P",
            "P",
            "P",
            "P",
            "P",
            "P",
            "P",
        ],
        "b": [
            "R",
            "N",
            "B",
            "Q",
            "K",
            "B",
            "N",
            "R",
            "P",
            "P",
            "P",
            "P",
            "P",
            "P",
            "P",
            "P",
        ],
    }

    current_pieces = {"w": [], "b": []}
    for piece in board.piece_map().values():
        color = "w" if piece.color == chess.WHITE else "b"
        current_pieces[color].append(piece.symbol().upper())

    captured_pieces = {"w": initial_pieces["w"].copy(), "b": initial_pieces["b"].copy()}
    for color in ["w", "b"]:
        for piece in current_pieces[color]:
            if piece in captured_pieces[color]:
                captured_pieces[color].remove(piece)

    return captured_pieces


def draw_panel(screen, board, images, player_times, turn):
    # Draw a background for the panel
    panel_bg = pygame.Rect(BOARD_SIZE + OFFSET * 2, 0 + OFFSET, PANEL_WIDTH, BOARD_SIZE)
    pygame.draw.rect(screen, LIGHT_SQUARE, panel_bg)

    # Display whose turn it is
    turn_text = "White's Turn" if turn else "Black's Turn"
    font = pygame.font.Font(None, 36)
    text = font.render(turn_text, True, BLACK)
    screen.blit(text, (BOARD_SIZE + 10 + OFFSET * 2, 20))

    captured_pieces = get_captured_pieces(board)

    # Display captured pieces in a grid for each player
    def draw_captured_pieces(y_offset, pieces, color):
        for i, piece in enumerate(pieces):
            row = i // PIECES_PER_ROW
            col = i % PIECES_PER_ROW
            x = BOARD_SIZE + OFFSET * 2 + col * GRID_CELL_SIZE
            y = y_offset + row * GRID_CELL_SIZE
            piece_image = images[color + piece.upper()]
            screen.blit(piece_image, (x, y))

    # White captured pieces
    draw_captured_pieces(60, captured_pieces["w"], "w")  # Adjust y_offset as needed

    # Black captured pieces
    draw_captured_pieces(
        BOARD_SIZE // 2, captured_pieces["b"], "b"
    )  # Adjust y_offset as needed


def generate_possible_fens(board):
    possible_fens = []
    for move in board.legal_moves:
        board_copy = board.copy(stack=False)
        board_copy.push(move)
        possible_fens.append(board_copy.fen())
    return possible_fens


# Main function
def main():
    global dragging, dragged_piece, dragged_piece_pos, selected_square, ai_fen_history
    screen = pygame.display.set_mode((TOTAL_WIDTH, TOTAL_HEIGHT))
    screen.fill(BACKGROUND)
    pygame.display.set_caption("Chess")
    clock = pygame.time.Clock()
    images, small_images = load_images()
    board = chess.Board()

    last_move_time = 0
    move_delay = 0.5  # 1 second delay between moves

    player_times = (0, 0)

    while True:
        current_time = time.time()
        human_turn = (board.turn and WHITE_IS_HUMAN) or (
            not board.turn and BLACK_IS_HUMAN
        )

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            if human_turn:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    selected_square = get_square_from_mouse(pygame.mouse.get_pos())
                    piece = board.piece_at(selected_square)
                    if piece and (piece.color == board.turn):
                        # Construct the key for the images dictionary
                        color = "w" if piece.color == chess.WHITE else "b"
                        piece_name = (
                            piece.symbol().upper()
                            if piece.color == chess.WHITE
                            else piece.symbol().lower()
                        )
                        image_key = color + piece_name.upper()
                        dragged_piece = images[
                            image_key
                        ]  # Use the correct key to fetch the image
                        dragged_piece_pos = pygame.mouse.get_pos()
                        dragging = True

                elif event.type == pygame.MOUSEBUTTONUP and dragging:
                    dragging = False
                    target_square = get_square_from_mouse(pygame.mouse.get_pos())
                    move = chess.Move(selected_square, target_square)
                    if move in board.legal_moves:
                        board.push(move)
                    selected_square = None
            if not human_turn and current_time - last_move_time > move_delay:
                stockfish.set_fen_position(board.fen())
                best_move = stockfish.get_best_move()
                while len(ai_fen_history) < 3:
                    ai_fen_history.insert(0, chess.Board().fen())

                # Generate possible FENs for the next AI moves
                possible_fens = generate_possible_fens(board)

                # Create a list for each possible move
                model_inputs = []
                for fen in possible_fens:
                    model_input = [fen, board.fen()] + ai_fen_history
                    model_inputs.append(model_input)
                print(model_inputs)
                # TODO: Use your model here to choose the best move
                # Example: best_move = your_model.choose_best_move(model_inputs)
                # For now, just making a random move as a placeholder
                best_move = random.choice(list(board.legal_moves))

                board.push(best_move)
                last_move_time = current_time

                # Update AI-specific FEN history
                ai_fen_history.append(board.fen())
                if len(ai_fen_history) > 3:  # Keep only the last 3 AI FEN states
                    ai_fen_history.pop(0)

        draw_board(screen)
        draw_pieces(screen, images, board)
        draw_panel(screen, board, small_images, player_times, board.turn)

        if dragging:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            screen.blit(
                dragged_piece, (mouse_x - SQUARE_SIZE // 2, mouse_y - SQUARE_SIZE // 2)
            )

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
