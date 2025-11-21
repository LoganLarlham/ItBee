import pytest
import pexpect
import sys
import shutil
from pathlib import Path

# Skip if pexpect not installed (though we installed it)
pytest.importorskip("pexpect")

def test_cli_game_flow(tmp_path):
    """Test the full game flow via CLI."""
    # Set a custom home dir for the test to avoid messing with user's session
import sqlite3
from it_spelling_bee.letters import mask_of

def create_test_db(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.execute("CREATE TABLE words (clean_form TEXT, zipf REAL, mask INTEGER)")
    # Words that form a valid board with seed 12345
    # Seed 12345 -> [C] e s n i d f (based on test runs)
    # Need enough words to satisfy min-valid-words constraint
    words = ["dice", "fine", "scendi", "fendi", "dici", "cece", "ceci", "idi", 
             "sede", "sedi", "fede", "pieno", "piano", "decidono", "cedono"]
    for w in words:
        conn.execute("INSERT INTO words VALUES (?, ?, ?)", (w, 4.0, mask_of(w)))
    conn.commit()
    conn.close()

def test_cli_game_flow(tmp_path):
    # Setup environment
    env = {"HOME": str(tmp_path), "PYTHONPATH": "."}
    
    # Create minimal DB
    db_path = tmp_path / ".it_spelling_bee" / "lexicon.sqlite"
    create_test_db(db_path)
    
    # Run with a fixed seed and relaxed constraints
    # Seed 12345 -> Required: 'c', Others: 'e', 's', 'n', 'i', 'd', 'f'
    cmd = f"{sys.executable} -m it_spelling_bee.cli --seed 12345 --no-color --min-valid-words 1"
    
    child = pexpect.spawn(cmd, env=env, encoding="utf-8", timeout=5)
    
    # Expect prompt
    child.expect("> ")
    
    # 1. Guess a valid word
    child.sendline("dice")
    child.expect("OK")
    child.expect("> ")
    
    # 2. Guess an invalid word (missing required 'c')
    child.sendline("fine") 
    child.expect("missing required letter")
    child.expect("> ")
    
    # 3. Guess a word with invalid letters (must contain required 'c' to pass first check)
    child.sendline("cazz")
    child.expect("contains invalid letter")
    child.expect("> ")
    
    # 4. Check score
    child.sendline("score")
    child.expect("Found 1/")
    child.expect("> ")
    
    # 5. Quit
    child.sendline("quit")
    child.expect("Bye")
    child.wait()
    
    # 6. Verify persistence
    session_file = tmp_path / ".it_spelling_bee" / "session.json"
    assert session_file.exists()
    # Restart and verify session resumed
    # Must NOT pass --seed, otherwise session is ignored
    cmd_resume = f"{sys.executable} -m it_spelling_bee.cli --no-color --min-valid-words 1"
    child = pexpect.spawn(cmd_resume, env=env, encoding="utf-8", timeout=2)
    child.expect("Resuming saved session...")
    child.expect("> ")
    
    # Check list has 'dice' from previous session
    child.sendline("list")
    child.expect("dice")
    child.expect("> ")
    
    child.sendline("quit")
    child.wait()
