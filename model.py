import tensorflow as tf
from tensorflow.keras.models import Model
from sklearn.model_selection import train_test_split
from tensorflow.keras import layers
from LichessAPI import get_games, get_games_as_a_set
from tensor import ChessTensor
import numpy as np


def create_chess_cnn():
    model = tf.keras.Sequential([
        # Convolutional layers with 'same' padding
        layers.Conv2D(32, (3, 3), activation='relu', padding='same', input_shape=(8, 8, 70)),
        layers.MaxPooling2D((2, 2)),
        layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
        layers.MaxPooling2D((2, 2)),

        # Flattening the output for the dense layer
        layers.Flatten(),

        # Dense layers
        layers.Dense(64, activation='relu'),
        layers.Dense(32, activation='relu'),

        # Output layer
        layers.Dense(1, activation='sigmoid')
    ])

    model.compile(optimizer='adam', loss='mse', metrics=['accuracy'])
    return model



if __name__ == "__main__":
    fen_games, colors = get_games("chesstacion", 100)
    fen_positions, target = get_games_as_a_set(fen_games, colors, 3)

    chess_tensor = ChessTensor()
    processed_tensors = []
    for position in fen_positions:
        temp = []
        for board in position:
            chess_tensor.parse_fen(board)
            tensor = chess_tensor.get_tensor().transpose(1, 2, 0)  # Reshaping here
            temp.append(tensor)
        concatenated = np.concatenate(temp, axis=2)  # Concatenating here
        processed_tensors.append(concatenated)
        # Convert each list of tensors into a single 4D tensor and stack them
    X = np.array(processed_tensors)
    y = np.array(target)  # Assuming 'target' is already a list of labels
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

    # Create the CNN model
    chess_cnn = create_chess_cnn()

    # Summary of the model
    chess_cnn.summary()
    # Train the model
    history = chess_cnn.fit(X_train, y_train, epochs=10, batch_size=32, validation_data=(X_val, y_val))
    model_path = "my_chess_model.h5"  # Change the path as needed
    chess_cnn.save(model_path)

