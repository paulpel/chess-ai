"""Regression tests for the from-scratch chess engine (`chess_ai.engine.app`).

These pin down two bugs that previously slipped through silently:

* the rook branch of ``is_king_attacked`` only matched queens, so checks
  delivered by a rook along a rank/file went undetected;
* a pawn's double step computed the en-passant target row as
  ``from_row + to_row / 2`` (a float, and the wrong square) instead of the
  integer midpoint.
"""

from chess_ai.engine.app import Chess


def _empty_board() -> list[list[str]]:
    return [["." for _ in range(8)] for _ in range(8)]


def test_rook_gives_check() -> None:
    game = Chess()
    board = _empty_board()
    board[4][4] = "K"  # our (white) king
    board[4][0] = "r"  # enemy rook on the same rank, clear path between
    assert game.is_king_attacked(board, "K") is True


def test_blocked_rook_does_not_give_check() -> None:
    game = Chess()
    board = _empty_board()
    board[4][4] = "K"
    board[4][0] = "r"
    board[4][2] = "P"  # our own pawn blocks the rook's line
    assert game.is_king_attacked(board, "K") is False


def test_en_passant_target_is_integer_midpoint() -> None:
    game = Chess()
    game.board = _empty_board()
    game.board[6][3] = "P"
    game.move((6, 3, 4, 3))  # white pawn double step
    assert game.en_passant_target == (3, 5)
    assert isinstance(game.en_passant_target[1], int)
