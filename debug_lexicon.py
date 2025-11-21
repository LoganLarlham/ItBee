from it_spelling_bee.lexicon.store import Lexicon
import sys

print(f"Python: {sys.executable}")
try:
    lex = Lexicon()
    print(f"Path: {lex.db_path}")
    print(f"Exists: {lex.db_path.exists()}")
    candidates = list(lex.iter_by_required('a'))
    print(f"Candidates for 'a': {len(candidates)}")
    if len(candidates) > 0:
        print(f"First candidate: {candidates[0]}")
except Exception as e:
    print(f"Error: {e}")
