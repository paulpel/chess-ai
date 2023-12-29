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

dragging = False  # Flag to track if a piece is being dragged
dragged_piece = None  # Store the piece being dragged
dragged_piece_pos = (0, 0)  # Current position of the dragged piece
selected_square = None  # The starting square of the dragged piece


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
                    (square % 8) * SQUARE_SIZE,
                    (square // 8) * SQUARE_SIZE,
                    SQUARE_SIZE,
                    SQUARE_SIZE,
                ),
            )


# Main function
def main():
    global dragging, dragged_piece, dragged_piece_pos, selected_square
    screen = pygame.display.set_mode((BOARD_SIZE, BOARD_SIZE))
    pygame.display.set_caption('Chess')
    clock = pygame.time.Clock()
    images = load_images()
    board = chess.Board()

    while True:
        human_turn = (board.turn and WHITE_IS_HUMAN) or (not board.turn and BLACK_IS_HUMAN)

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
                        color = 'w' if piece.color == chess.WHITE else 'b'
                        piece_name = piece.symbol().upper() if piece.color == chess.WHITE else piece.symbol().lower()
                        image_key = color + piece_name.upper()
                        dragged_piece = images[image_key]  # Use the correct key to fetch the image
                        dragged_piece_pos = pygame.mouse.get_pos()
                        dragging = True

                elif event.type == pygame.MOUSEBUTTONUP and dragging:
                    dragging = False
                    target_square = get_square_from_mouse(pygame.mouse.get_pos())
                    move = chess.Move(selected_square, target_square)
                    if move in board.legal_moves:
                        board.push(move)
                    selected_square = None

        draw_board(screen)
        draw_pieces(screen, images, board)

        # Draw the dragged piece
        if dragging:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            screen.blit(dragged_piece, (mouse_x - SQUARE_SIZE // 2, mouse_y - SQUARE_SIZE // 2))

        clock.tick(FPS)
        pygame.display.flip()


if __name__ == "__main__":
    main()
