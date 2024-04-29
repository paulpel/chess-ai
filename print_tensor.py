# Assume the tensor shape is (110, 8, 8) where:
# - 104 layers are for 8 plies of board states (13 layers each)
# - 4 layers for castling rights
# - 1 layer for who's turn it is
# - 1 layer for the 50-move rule

def describe_and_print_tensor(tensor):
    piece_symbols = 'PRNBQKprnbqk'  # Order of pieces in the tensor layers
    descriptions = []
    
    # Generate descriptions for each of the 104 layers related to board states
    for ply in range(8):
        for i, symbol in enumerate(piece_symbols):
            descriptions.append(f"Ply {ply + 1}: {symbol} positions")
        descriptions.append(f"Ply {ply + 1}: IsRep layer (unused, always zeros)")

    # Castling rights
    descriptions.append("Castling rights: White kingside")
    descriptions.append("Castling rights: White queenside")
    descriptions.append("Castling rights: Black kingside")
    descriptions.append("Castling rights: Black queenside")
    
    # Current player turn
    descriptions.append("Current player turn (1 for Black, 0 for White)")
    
    # 50-move rule counter (assumed to be unused and set to zeros)
    descriptions.append("50-move rule counter (unused, always zeros)")
    descriptions.append("???")
    descriptions.append("???")
    assert len(descriptions) == 112, "Mismatch between descriptions and tensor layers."

    # Print each layer with its description
    for index, description in enumerate(descriptions):
        print(f"Layer {index + 1}: {description}")
        print(tensor[index])
        print()  # Add a newline for better readability between layers
