import pygame
import chess
import os

# Initialize Pygame
pygame.init()

# Constants
BOARD_SIZE = 512  # Adjust as needed
SQUARE_SIZE = BOARD_SIZE // 8
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_SQUARE = (240, 217, 181)
DARK_SQUARE = (181, 136, 99)

WHITE_IS_HUMAN = True
BLACK_IS_HUMAN = True

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
    return images


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
                    col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE
                ),
            )


# Draw the pieces on the board
def draw_pieces(screen, images, board):
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            symbol = piece.symbol()
            if symbol.isupper():
                color = "w"
            else:
                color = "b"
            screen.blit(
                images[color + symbol.upper()],
                pygame.Rect(
                    (square % 8) * SQUARE_SIZE,
                    (square // 8) * SQUARE_SIZE,
                    SQUARE_SIZE,
                    SQUARE_SIZE,
                ),
            )

# Main function
def main():
    screen = pygame.display.set_mode((BOARD_SIZE, BOARD_SIZE))
    pygame.display.set_caption('Chess')
    clock = pygame.time.Clock()
    images = load_images()
    board = chess.Board()
    move_made = False  # Flag to check if a move was made

    selected_piece = None  # Track the selected piece
    valid_moves = []  # Track valid moves for the selected piece

    while True:
        human_turn = (board.turn and WHITE_IS_HUMAN) or (not board.turn and BLACK_IS_HUMAN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            if human_turn:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    selected_square = get_square_from_mouse(pygame.mouse.get_pos())
                    selected_piece = board.piece_at(selected_square)
                    if selected_piece and (selected_piece.color == board.turn):
                        valid_moves = [move for move in board.legal_moves if move.from_square == selected_square]
                elif event.type == pygame.MOUSEBUTTONUP:
                    target_square = get_square_from_mouse(pygame.mouse.get_pos())
                    move = chess.Move(selected_square, target_square)
                    if move in valid_moves:
                        board.push(move)
                        move_made = True
                        selected_piece = None
                        valid_moves = []

        # AI move
        if not human_turn and move_made:
            # AI move logic here
            pass

        if move_made:
            move_made = False

        draw_board(screen)
        draw_pieces(screen, images, board)

        clock.tick(FPS)
        pygame.display.flip()


if __name__ == "__main__":
    main()
