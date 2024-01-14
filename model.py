import tensorflow as tf
from tensorflow.keras.models import Model
from sklearn.model_selection import train_test_split
from tensorflow.keras.layers import Input, Conv2D, Dense, Flatten, MaxPooling2D, Concatenate
from LichessAPI import get_games, get_games_as_a_set
from tensor import ChessTensor
import numpy as np


import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Conv2D, Dense, Flatten, MaxPooling2D, Concatenate, Lambda

def create_chess_cnn():
    # Define the input shape: 5 tensors each of shape (14, 8, 8)
    input_shape = (5, 14, 8, 8)

    # Input layer
    input_layer = Input(shape=input_shape)

    # Process each 8x8 board state separately
    conv_layers = []
    for i in range(5):
        # Extract the ith board state using a Lambda layer
        board_state = Lambda(lambda x: x[:, i, :, :, :])(input_layer)

        # First convolutional layer for this board state
        conv1 = Conv2D(32, (3, 3), activation='relu', padding='same')(board_state)
        pool1 = MaxPooling2D((2, 2))(conv1)

        # Second convolutional layer
        conv2 = Conv2D(64, (3, 3), activation='relu', padding='same')(pool1)
        pool2 = MaxPooling2D((2, 2))(conv2)

        # Flatten the output
        flatten = Flatten()(pool2)

        # Append the flattened output to the list
        conv_layers.append(flatten)

    # Concatenate the outputs from each board state
    concatenated = Concatenate()(conv_layers)

    # Dense layers
    dense1 = Dense(128, activation='relu')(concatenated)
    dense2 = Dense(64, activation='relu')(dense1)

    # Output layer
    output = Dense(1, activation='sigmoid')(dense2)

    # Create the model
    model = Model(inputs=input_layer, outputs=output)

    # Compile the model
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

    return model


if __name__ == "__main__":
    fen_games, colors = get_games("chesstacion", 100)
    fen_positions, target = get_games_as_a_set(fen_games, colors, 3)

    chess_tensor = ChessTensor()
    tensors = []
    for position in fen_positions:
        temp = []
        for board in position:
            chess_tensor.parse_fen(board)
            tensor = chess_tensor.get_tensor()
            temp.append(tensor)
        tensors.append(temp)
        # Convert each list of tensors into a single 4D tensor and stack them
    X = np.stack([np.stack(sample, axis=0) for sample in tensors])
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

