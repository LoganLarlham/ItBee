import pytest
from unittest.mock import patch, Mock
from io import StringIO
import sys
from it_spelling_bee.cli import run
from it_spelling_bee.typing import Letters, WordEntry, GeneratedBoard
from it_spelling_bee.letters import mask_of

def make_mock_board():
    letters = Letters(required="a", others=("b", "c", "d", "e", "f", "g"))
    board_mask = mask_of("abcdefg")
    words = [
        WordEntry(text="able", zipf=5.0, mask=mask_of("able")),
        WordEntry(text="fade", zipf=4.5, mask=mask_of("fade")),
        WordEntry(text="abcdefg", zipf=4.0, mask=mask_of("abcdefg")),
    ]
    scores = {"able": 4, "fade": 5, "abcdefg": 10}
    return GeneratedBoard(
        letters=letters,
        words=words,
        scores=scores,
        total_points=19,
        threshold=15,
        mask=board_mask
    )

@pytest.fixture
def mock_generate(monkeypatch):
    def mock_gen(*args, **kwargs):
        return make_mock_board()
    monkeypatch.setattr("it_spelling_bee.cli.generate_board", mock_gen)

def test_cli_help(mock_generate):
    # Simulate 'help' command followed by 'quit'
    input_stream = StringIO("help\nquit\n")
    with patch("sys.stdin", input_stream), patch("sys.stdout", new_callable=StringIO) as output:
        run(["--seed", "42"])
        out = output.getvalue()
        assert "Commands: help, shuffle" in out
        assert "quit" in out

def test_cli_list_command(mock_generate):
    # Test 'list' showing found words
    input_stream = StringIO("able\nlist\nquit\n")
    with patch("sys.stdin", input_stream), patch("sys.stdout", new_callable=StringIO) as output:
        run(["--seed", "42"])
        out = output.getvalue()
        assert "Found:" in out
        assert "able" in out

def test_cli_score_command(mock_generate):
    # Test 'score' showing progress
    input_stream = StringIO("able\nscore\nquit\n")
    with patch("sys.stdin", input_stream), patch("sys.stdout", new_callable=StringIO) as output:
        run(["--seed", "42"])
        out = output.getvalue()
        assert "Found 1/3" in out
        assert "Score 4" in out

def test_cli_giveup_command(mock_generate):
    # Test 'giveup' showing all words
    input_stream = StringIO("giveup\n")
    with patch("sys.stdin", input_stream), patch("sys.stdout", new_callable=StringIO) as output:
        run(["--seed", "42"])
        out = output.getvalue()
        assert "All words:" in out
        assert "able" in out
        assert "fade" in out
        assert "abcdefg" in out

def test_cli_shuffle_command(mock_generate):
    # Test 'shuffle' changes letter display
    input_stream = StringIO("shuffle\nquit\n")
    with patch("sys.stdin", input_stream), patch("sys.stdout", new_callable=StringIO) as output:
        run(["--seed", "42"])
        out = output.getvalue()
        assert "[A]" in out  # Required letter should be capitalized
        # Note: Can't test exact shuffle order as it's random

def test_cli_invalid_word(mock_generate):
    # Test submitting invalid word
    input_stream = StringIO("xyz\nquit\n")
    with patch("sys.stdin", input_stream), patch("sys.stdout", new_callable=StringIO) as output:
        run(["--seed", "42"])
        out = output.getvalue()
        assert "not in solution" in out

def test_cli_duplicate_word(mock_generate):
    # Test submitting duplicate word
    input_stream = StringIO("able\nable\nquit\n")
    with patch("sys.stdin", input_stream), patch("sys.stdout", new_callable=StringIO) as output:
        run(["--seed", "42"])
        out = output.getvalue()
        assert "+4 OK" in out  # First submission
        assert "duplicate" in out  # Second submission