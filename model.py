import tensorflow as tf
from tensorflow.keras.layers import Input, Dense, Conv2D, Flatten, LSTM, Concatenate
from tensorflow.keras.models import Model
from sklearn.model_selection import train_test_split
from prep_data import extract_data_for_training, transform_data


def preprocess(N):
    # Transforming data
    white_data, black_data = extract_data_for_training('player_games.pgn')
    X_white, y_white = transform_data(white_data, N)
    X_black, y_black = transform_data(black_data, N)

    # Splitting into training and testing sets
    X_train_white, X_test_white, y_train_white, y_test_white = train_test_split(X_white, y_white, test_size=0.2, random_state=42)
    X_train_black, X_test_black, y_train_black, y_test_black = train_test_split(X_black, y_black, test_size=0.2, random_state=42)
    
    return (X_train_white, X_test_white, y_train_white, y_test_white), (X_train_black, X_test_black, y_train_black, y_test_black)


def build_model(num_possible_moves, N):
    # Assuming board states are transformed to 8x8x1 matrices and moves to 3xN arrays
    num_possible_moves = 5000  # This is a simplification

    # CNN for board state
    board_input = Input(shape=(8, 8, 1))  # Change dimensions based on your encoding
    cnn = Conv2D(64, kernel_size=3, activation='relu')(board_input)
    cnn = Conv2D(64, kernel_size=3, activation='relu')(cnn)
    cnn = Flatten()(cnn)

    # LSTM for move history
    move_input = Input(shape=(3, N))  # N depends on your move encoding
    lstm = LSTM(64)(move_input)

    # Concatenate and final dense layers
    combined = Concatenate()([cnn, lstm])
    dense = Dense(128, activation='relu')(combined)
    output = Dense(num_possible_moves, activation='softmax')(dense)  # num_possible_moves is the number of possible move outputs

    model = Model(inputs=[board_input, move_input], outputs=output)

    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    return model


if __name__ == "__main__":
    N = 3  # or the correct value based on your move encoding
    num_possible_moves = 5000  # Adjust based on actual number of possible moves

    (white_train, white_test, white_train_labels, white_test_labels), \
    (black_train, black_test, black_train_labels, black_test_labels) = preprocess(N)

    white_model = build_model(num_possible_moves, N)
    black_model = build_model(num_possible_moves, N)

    # Train models
    white_model.fit(white_train, white_train_labels, validation_data=(white_test, white_test_labels), epochs=10, batch_size=32)
    black_model.fit(black_train, black_train_labels, validation_data=(black_test, black_test_labels), epochs=10, batch_size=32)

    white_model.save('white_chess_model')
    black_model.save('black_chess_model')
