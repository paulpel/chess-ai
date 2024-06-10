import pygame
import chess
import os
import time
from tensor import generate_full_input_tensor
import numpy as np
from maia_model_test import load_model
from print_tensor import describe_and_print_tensor
from maia.tf2.policy_index import policy_index

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

# Define your custom colors
SELECTED_ITEM_COLOR = (255, 194, 226)  # Gold color for selected items
NON_SELECTED_ITEM_COLOR = (244, 255, 253)  # Sky blue color for non-selected items

# Global variables to store player settings
play_mode = "AI"  # Other option is 'Human'
player_color = "White"  # Other option is 'Black'
ai_board_history = []

loaded_ai_model = load_model('maia\\tf2\\mymodel2.h5')

dragging = False  # Flag to track if a piece is being dragged
dragged_piece = None  # Store the piece being dragged
dragged_piece_pos = (0, 0)  # Current position of the dragged piece
selected_square = None  # The starting square of the dragged piece
# Load the pre-trained model
# chess_cnn = load_model("my_chess_model.h5")

# # Ensure that your model is compiled after loading (you can use the same compile parameters)
# chess_cnn.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])


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
    row = 7 - (y // SQUARE_SIZE)
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
                    (7 - square // 8) * SQUARE_SIZE + OFFSET,
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


def generate_possible_boards_with_moves(board):
    possible_boards = []
    moves = []
    for move in board.legal_moves:
        board_copy = board.copy(stack=False)
        board_copy.push(move)
        possible_boards.append(board_copy)
        moves.append(move)
    return possible_boards, moves


def choose_best_move(model, model_inputs):
    predictions = model.predict(model_inputs)
    best_move_index = np.argmax(predictions)  # Choose the move with the highest score
    return best_move_index


def generate_move_with_promotion(from_square, to_square, promotion_piece):
    # Creates a chess move with the specified promotion piece
    return chess.Move(from_square, to_square, promotion=promotion_piece)


def show_promotion_gui(screen, color):
    panel_width, panel_height = 280, 80  # Increased size for better visibility
    panel_x = (BOARD_SIZE - panel_width) // 2
    panel_y = (BOARD_SIZE - panel_height) // 2

    # Highlight the background to make it more distinct
    background_color = (100, 100, 100)  # A darker shade to contrast with the options
    pygame.draw.rect(
        screen, background_color, [panel_x, panel_y, panel_width, panel_height]
    )

    # Adding an instruction text above the options
    font = pygame.font.Font(None, 32)
    text = font.render("Choose Promotion:", True, WHITE)
    text_rect = text.get_rect(center=(panel_x + panel_width // 2, panel_y - 20))
    screen.blit(text, text_rect)

    options = ["Q", "R", "B", "N"]  # Promotion options
    option_positions = []
    images, _ = load_images()  # Assuming this function returns the images
    option_gap = 10  # Gap between options for better spacing
    option_width = (panel_width - (len(options) + 1) * option_gap) // len(options)
    for i, option in enumerate(options):
        img = images[color + option]
        img_x = panel_x + i * (option_width + option_gap) + option_gap
        img_y = panel_y + (panel_height - img.get_height()) // 2  # Vertically center
        screen.blit(img, (img_x, img_y))
        option_positions.append((img_x, img_y, img.get_width(), img.get_height()))

    pygame.display.flip()
    return option_positions  # Return positions to enable click detection


def get_promotion_choice(option_positions, mouse_x, mouse_y):
    for i, (x, y, width, height) in enumerate(option_positions):
        if x <= mouse_x <= x + width and y <= mouse_y <= y + height:
            return [chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT][i]
    return None


def check_game_state(board):
    if board.is_checkmate():
        return "checkmate"
    elif (
        board.is_stalemate()
        or board.is_insufficient_material()
        or board.can_claim_fifty_moves()
        or board.can_claim_threefold_repetition()
    ):
        return "draw"
    return "ongoing"


def display_endgame_message(screen, game_state):
    font = pygame.font.Font(None, 48)
    if game_state == "checkmate":
        text = "Checkmate!"
    elif game_state == "draw":
        text = "Draw!"
    else:
        return  # No need to display anything if the game is ongoing

    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect(center=(TOTAL_WIDTH // 2, TOTAL_HEIGHT // 2))
    screen.blit(text_surface, text_rect)
    pygame.display.flip()
    # Give some time to see the message before closing or resetting the game
    time.sleep(5)


def load_background():
    background_image = pygame.image.load("bg.png")
    # Optionally scale the image to fit your screen size
    background_image = pygame.transform.scale(
        background_image, (TOTAL_WIDTH, TOTAL_HEIGHT)
    )
    return background_image


def draw_text_with_shadow(screen, text, font, color, shadow_color, position):
    text_surface = font.render(text, True, color)
    shadow_surface = font.render(text, True, shadow_color)
    x, y = position
    # Position the shadow slightly offset from the text's position
    shadow_position = (x + 2, y + 2)  # Adjust the offset to your liking

    # Draw the shadow first
    screen.blit(shadow_surface, shadow_position)
    # Then draw the text
    screen.blit(text_surface, position)



def show_menu(screen, font, background_image):
    menu_items = ['Play', 'Options', 'Quit']
    selected_index = 0

    def draw_menu():
        screen.blit(background_image, (0, 0))  # Draw the background image
        
        for index, item in enumerate(menu_items):
            if index == selected_index:
                color = SELECTED_ITEM_COLOR  # White for selected item
                shadow_color = (50, 50, 50)  # Dark grey for shadow
            else:
                color = NON_SELECTED_ITEM_COLOR  # Light grey for non-selected items
                shadow_color = (0, 0, 0)  # Black for shadow
            
            # Central position for the text
            x = TOTAL_WIDTH // 2
            y = 150 + index * 50
            # Adjust text alignment if necessary
            text_surface = font.render(item, True, color)
            text_rect = text_surface.get_rect(center=(x, y))
            
            draw_text_with_shadow(screen, item, font, color, shadow_color, text_rect.topleft)

        pygame.display.flip()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'Quit'
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_index = (selected_index - 1) % len(menu_items)
                elif event.key == pygame.K_DOWN:
                    selected_index = (selected_index + 1) % len(menu_items)
                elif event.key == pygame.K_RETURN:
                    return menu_items[selected_index]

        draw_menu()

    return 'Quit'


def show_options(screen, font, background_image):
    global play_mode, player_color
    options_menu = ["Play Mode: " + play_mode, "Player Color: " + player_color, "Back"]
    selected_index = 0

    def draw_options():
        screen.blit(background_image, (0, 0))  # Draw the background image
        for index, option in enumerate(options_menu):
            if index == selected_index:
                color = SELECTED_ITEM_COLOR  # White for selected item
                shadow_color = (50, 50, 50)  # Dark grey for shadow
            else:
                color = NON_SELECTED_ITEM_COLOR  # Light grey for non-selected items
                shadow_color = (0, 0, 0)  # Black for shadow

            # Central position for the text
            x = TOTAL_WIDTH // 2
            y = 150 + index * 50
            # Adjust text alignment if necessary
            text_surface = font.render(option, True, color)
            text_rect = text_surface.get_rect(center=(x, y))

            draw_text_with_shadow(screen, option, font, color, shadow_color, text_rect.topleft)

        pygame.display.flip()

    running = True
    while running:
        draw_options()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return "Quit"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_index = (selected_index - 1) % len(options_menu)
                elif event.key == pygame.K_DOWN:
                    selected_index = (selected_index + 1) % len(options_menu)
                elif event.key == pygame.K_RETURN:
                    if selected_index == 0:  # Toggle Play Mode
                        play_mode = "AI" if play_mode == "Human" else "Human"
                        options_menu[selected_index] = "Play Mode: " + play_mode
                    elif selected_index == 1:  # Toggle Player Color
                        player_color = "White" if player_color == "Black" else "Black"
                        options_menu[selected_index] = "Player Color: " + player_color
                    elif selected_index == 2:  # Return to main menu
                        return

        pygame.time.wait(100)


def make_move(board, move):
    board.push(move)
    tensor = generate_full_input_tensor(board, ai_board_history[-7:])
    ai_board_history.append(board.copy())
    # describe_and_print_tensor(tensor)


def main():
    global dragging, dragged_piece, dragged_piece_pos, selected_square, play_mode, player_color
    screen = pygame.display.set_mode((TOTAL_WIDTH, TOTAL_HEIGHT))
    pygame.display.set_caption("Chess")
    font = pygame.font.Font(None, 36)
    background_image = (
        load_background()
    )  # Ensure this function loads your background image correctly

    while True:
        menu_selection = show_menu(screen, font, background_image)
        if menu_selection == "Quit":
            pygame.quit()
            break
        elif menu_selection == "Play":
            # Function to start the game
            start_game(play_mode, player_color)
        elif menu_selection == "Options":
            # Function to show options, now with background
            show_options(screen, font, background_image)

        # Redisplay menu after coming back from other screens
        menu_selection = show_menu(screen, font, background_image)


def start_game(mode, color):
    # Initialize game setup based on selected mode and color
    # Set AI or human player settings based on 'mode' and 'color'
    global ai_board_history, WHITE_IS_HUMAN, BLACK_IS_HUMAN
    if mode == "AI":
        if color == "White":
            WHITE_IS_HUMAN = True
            BLACK_IS_HUMAN = False
        else:
            WHITE_IS_HUMAN = False
            BLACK_IS_HUMAN = True
    else:
        WHITE_IS_HUMAN = True
        BLACK_IS_HUMAN = True
    global dragging, dragged_piece, dragged_piece_pos, selected_square
    pygame.init()
    screen = pygame.display.set_mode((TOTAL_WIDTH, TOTAL_HEIGHT))
    font = pygame.font.Font(None, 36)  # Use the same font for the menu

    background_image = load_background()
    menu_selection = show_menu(screen, font, background_image)
    if menu_selection == "Quit":
        pygame.quit()
        return
    elif menu_selection == "Play":
        # Proceed to the main game loop
        pass  # Here the rest of your main game loop starts
    elif menu_selection == "History":
        # You would add your history handling here
        pass
    elif menu_selection == "Options":
        # Options handling can be added here
        pass
    screen = pygame.display.set_mode((TOTAL_WIDTH, TOTAL_HEIGHT))
    screen.fill(BACKGROUND)
    pygame.display.set_caption("Chess")
    clock = pygame.time.Clock()
    images, small_images = load_images()
    board = chess.Board()
    ai_board_history.append(board.copy())

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

                if event.type == pygame.MOUSEBUTTONUP and dragging:
                    dragging = False
                    to_square = get_square_from_mouse(pygame.mouse.get_pos())
                    piece = board.piece_at(selected_square)
                    if (
                        piece
                        and piece.piece_type == chess.PAWN
                        and (
                            to_square in chess.SQUARES[0:8]
                            or to_square in chess.SQUARES[56:64]
                        )
                    ):
                        # Pawn reaches promotion rank
                        color = "w" if piece.color == chess.WHITE else "b"
                        option_positions = show_promotion_gui(screen, color)
                        promotion_piece = None
                        while promotion_piece is None:
                            for event in pygame.event.get():
                                if event.type == pygame.MOUSEBUTTONDOWN:
                                    mouse_x, mouse_y = pygame.mouse.get_pos()
                                    promotion_piece = get_promotion_choice(
                                        option_positions, mouse_x, mouse_y
                                    )
                                    if promotion_piece:
                                        move = generate_move_with_promotion(
                                            selected_square, to_square, promotion_piece
                                        )
                                        if move in board.legal_moves:
                                            make_move(board, move)
                                        break
                    else:
                        move = chess.Move(selected_square, to_square)
                        if move in board.legal_moves:
                            make_move(board, move)
                    selected_square = None
                    # After a move is made, either by a human or the AI
                    game_state = check_game_state(board)
                    if game_state != "ongoing":
                        display_endgame_message(screen, game_state)
                        pygame.time.wait(5000)  # Wait for 5000 milliseconds = 5 seconds
                        break  # This exits the main game loop

            if not human_turn and current_time - last_move_time > move_delay:

                # # METODA WYKORZYSTUJĄCA VALUE HEAD
                # possible_boards, moves = generate_possible_boards_with_moves(board)
                # print(moves)
                # input_tensors = [generate_full_input_tensor(candidate_board, ai_board_history[-7:]) for candidate_board in possible_boards]
                # input_array = np.array(input_tensors, dtype=float).reshape((len(input_tensors), 112, 64))

                # predictions = loaded_ai_model.predict(input_array)
                # best_board = possible_boards[np.argmax(predictions[1],axis=0)[0]]
                # print(best_board)
                # best_move = moves[np.argmax(predictions[1],axis=0)[0]]
                # print(best_move, type(best_move))

                # make_move(board, best_move)


                # METODA WYKORZYSTUJĄCA POLICY HEAD
                possible_boards, moves = generate_possible_boards_with_moves(board)
                print(moves)
                moves_indices = np.array([policy_index.index(move.uci()) for move in moves])
                input_tensor = generate_full_input_tensor(board, ai_board_history[-7:])
                input_array = np.array([input_tensor], dtype=float).reshape((1, 112, 64))
                prediction = loaded_ai_model.predict(input_array)
                print(prediction[0][0])
                best_move = moves[np.argmin(prediction[0][0][moves_indices])]
                print(best_move, type(best_move))

                make_move(board, best_move)

                                # After a move is made, either by a human or the AI
                game_state = check_game_state(board)
                if game_state != "ongoing":
                    display_endgame_message(screen, game_state)
                    pygame.time.wait(5000)  # Wait for 5000 milliseconds = 5 seconds
                    break  # This exits the main game loop

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
