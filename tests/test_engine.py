from it_spelling_bee.typing import Letters, WordEntry, GeneratedBoard
from it_spelling_bee.engine import Engine, GameState
from it_spelling_bee.letters import mask_of


def make_test_board():
    letters = Letters(required="a", others=("b", "c", "d", "e", "f", "g"))
    board_mask = mask_of("abcdefg")
    words = [
        WordEntry(text="abc", zipf=5.0, mask=mask_of("abc")),
        WordEntry(text="ade", zipf=6.0, mask=mask_of("ade")),
        WordEntry(text="abcdefg", zipf=4.0, mask=mask_of("abcdefg")),  # pangram
    ]
    scores = {"abc": 5, "ade": 4, "abcdefg": 10}
    return GeneratedBoard(
        letters=letters, 
        words=words, 
        scores=scores, 
        total_points=19, 
        threshold=15, 
        mask=board_mask
    )

def test_engine_basic_flow():
    board = make_test_board()
    eng = Engine(board)
    
    # Valid guess
    ok, msg, pts = eng.guess("abc")
    assert ok and pts == 5
    assert msg == "ok"
    
    # Duplicate guess
    ok, msg, pts = eng.guess("abc")
    assert not ok and msg == "duplicate"
    assert pts is None
    
    # Invalid guess
    ok, msg, pts = eng.guess("zzz")
    # missing the required letter should be reported explicitly
    assert not ok and msg == "missing required letter"
    assert pts is None

def test_engine_progress_tracking():
    board = make_test_board()
    eng = Engine(board)
    
    # Initial state
    p = eng.progress()
    assert p["found"] == 0
    assert p["total_words"] == 3
    assert p["score"] == 0
    assert p["threshold"] == 15
    assert p["total_points"] == 19
    
    # After one word
    eng.guess("abc")
    p = eng.progress()
    assert p["found"] == 1
    assert p["score"] == 5
    
    # After pangram
    eng.guess("abcdefg")
    p = eng.progress()
    assert p["found"] == 2
    assert p["score"] == 15  # 5 + 10

def test_engine_win_condition():
    board = make_test_board()
    eng = Engine(board)
    
    assert not eng.is_won()  # Start: not won
    
    eng.guess("abc")  # +5 points
    assert not eng.is_won()  # 5 < 15 threshold
    
    eng.guess("abcdefg")  # +10 points
    assert eng.is_won()  # 15 >= 15 threshold

def test_engine_game_state():
    board = make_test_board()
    state = GameState(board=board)
    
    assert state.found == set()
    assert state.score == 0
    
    # Test state updates
    state.found.add("abc")
    state.score += 5
    assert "abc" in state.found
    assert state.score == 5
