import argparse
import random
import sys
from pathlib import Path

from .config import Settings
from .lexicon.store import Lexicon
from .generator import generate_board
from .engine import Engine
from .letters import shuffle_letters
from .persistence import load_session, save_session

# ANSI Colors
class Colors:
    RESET = "\033[0m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"

def colorize(text: str, color: str, enabled: bool) -> str:
    if not enabled:
        return text
    return f"{color}{text}{Colors.RESET}"

def show_intro(use_colors: bool):
    title = """
                                                                                
                                                                      
 __  __   ___                               .--.      ,.--.           
|  |/  `.'   `.                             |__|     //    \          
|   .-.  .-.   '          .-,.--.           .--.     \\    |          
|  |  |  |  |  |    __    |  .-. |          |  |    __`'-)/           
|  |  |  |  |  | .:--.'.  | |  | |.--------.|  | .:--.'./'       _    
|  |  |  |  |  |/ |   \ | | |  | ||____    ||  |/ |   \ |      .' |   
|  |  |  |  |  |`" __ | | | |  '-     /   / |  |`" __ | |     .   | / 
|__|  |__|  |__| .'.''| | | |       .'   /  |__| .'.''| |   .'.'| |// 
                / /   | |_| |      /    /___    / /   | |_.'.'.-'  /  
                \ \._,\ '/|_|     |         |   \ \._,\ '/.'   \_.'   
                 `--'  `"         |_________|    `--'  `"             
                        _ _ _               _               
                       | | (_)             | |              
         ___ _ __   ___| | |_ _ __   __ _  | |__   ___  ___ 
        / __| '_ \ / _ \ | | | '_ \ / _` | | '_ \ / _ \/ _ \\
        \__ \ |_) |  __/ | | | | | | (_| | | |_) |  __/  __/
        |___/ .__/ \___|_|_|_|_| |_|\__, | |_.__/ \___|\___|
            | |                      __/ |                  
            |_|                     |___/                   
 
Italian Spelling Bee
=================="""
    print(colorize(title, Colors.CYAN, use_colors))
    print("""Create words using the given letters. Each word must:
- Be at least 4 letters long
- Use the center letter (shown in [brackets])
- Only use the given letters
- Letters can be used multiple times

Accented letters: input is normalized by removing diacritics (e.g. "è" -> "e").
So enter words without accents or they'll be treated as their base letters.

Commands during play:
  help     - Show this help message
  shuffle  - Shuffle the outer letters
  list     - Show found words
  score    - Show current score
  hint     - Get a hint (costs points!)
  giveup   - Show all possible words
  restart  - Start a new game
  quit     - Exit the game
""")

def show_rules():
    print("""
Game Rules:
- Words must be at least 4 letters long
- Words must contain the center letter
- Words can only use the given letters
- Letters can be used multiple times
- Common Italian words only

Scoring:
- 4 letters: 4 points
- 5 letters: 5 points
- 6 letters: 6 points
- 7+ letters: 7 points + bonus
- Using all 7 letters: +7 points bonus

Goal: Achieve 75% of total possible points
""")

def get_session_path(settings: Settings) -> Path:
    return settings.data_path / "session.json"

def run(argv=None):
    parser = argparse.ArgumentParser(prog="itbee", description="Italian Spelling Bee - A word puzzle game")
    parser.add_argument("--seed", type=int, default=None, help="use specific seed for board generation")
    parser.add_argument("--rules", action="store_true", help="show game rules and scoring")
    parser.add_argument("--hint", action="store_true", help="show a random unguessed word")
    parser.add_argument("--solution", action="store_true", help="show all possible words and exit")
    parser.add_argument("--new", action="store_true", help="force new board generation")
    parser.add_argument("--dumpboard", action="store_true", help="print board data in JSON format")
    parser.add_argument("--no-color", action="store_true", help="disable colored output")
    parser.add_argument("--min-valid-words", type=int, help="Minimum number of valid words required")
    
    args = parser.parse_args(argv)
    
    if args.rules:
        show_rules()
        return

    settings = Settings()
    if args.no_color:
        settings.use_colors = False
    if args.min_valid_words is not None:
        settings.min_valid_words = args.min_valid_words

    session_path = get_session_path(settings)
    session_data = None
    
    # Load session if exists and not forcing new/seed
    if not args.new and args.seed is None and session_path.exists():
        session_data = load_session(session_path)
        if session_data and "seed" in session_data:
            settings.seed = session_data["seed"]
            print(colorize("Resuming saved session...", Colors.YELLOW, settings.use_colors))

    # If user provided a seed use it; otherwise generate a stable seed value
    if args.seed is not None:
        settings.seed = args.seed
    if settings.seed is None:
        # create a random 32-bit seed and store it so --printseed can display it
        settings.seed = random.getrandbits(32)
        
    rng = random.Random(settings.seed)
    lex = Lexicon()
    board = generate_board(lex, settings, rng)
    engine = Engine(board)

    # Restore state if we loaded a session matching this seed
    if session_data and session_data.get("seed") == settings.seed:
        engine.restore_state(session_data)

    if args.dumpboard:
        print(engine.dump_board())
        return
        
    if args.solution:
        words = sorted([(len(w.text), w.text, board.scores[w.text]) for w in board.words])
        current_len = 0
        for length, word, score in words:
            if length != current_len:
                current_len = length
                print(f"\n{length} letters ({score}pts each):")
            print(f"  {word}")
        print(f"\nTotal words: {len(board.words)}")
        print(f"Total possible points: {board.total_points}")
        return

    # Show intro text before starting
    if not (args.hint or args.solution or args.dumpboard):
        show_intro(settings.use_colors)

    required = board.letters.required
    others = list(board.letters.others)
    
    def print_status():
        req_display = colorize(f"[{required.upper()}]", Colors.CYAN + Colors.BOLD, settings.use_colors)
        others_display = " ".join(others)
        print(f"{req_display}  {others_display}")
        p = engine.progress()
        print(f"Found {p['found']}/{len(board.words)}   Score {p['score']} / {board.total_points}   Goal {board.threshold}")

    print_status()

    if args.hint:
        hint, cost = engine.get_hint(settings.hint_cost)
        if hint:
            print(colorize(hint, Colors.YELLOW, settings.use_colors))
            if cost > 0:
                print(colorize(f"(-{cost} points)", Colors.RED, settings.use_colors))
        return

    while True:
        try:
            text = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye")
            return
        if not text:
            continue
        
        if text == "help":
            print("Commands: help, shuffle, hint, list, score, giveup, restart, printseed, quit")
            continue
            
        if text == "printseed":
            print(f"Board seed: {settings.seed} (0x{settings.seed:X})")
            continue
            
        if text == "hint":
            hint, cost = engine.get_hint(settings.hint_cost)
            if hint:
                print(colorize(hint, Colors.YELLOW, settings.use_colors))
                if cost > 0:
                    print(colorize(f"Hint penalty applied: -{cost} points", Colors.RED, settings.use_colors))
                    # Save after score change
                    save_session(session_path, {
                        "seed": settings.seed,
                        "found": list(engine.state.found),
                        "score": engine.state.score
                    })
            else:
                print("No more words to find!")
            continue
            
        if text == "shuffle":
            _, others = shuffle_letters(required, others, rng)
            others = list(others)
            print_status()
            continue
            
        if text == "list":
            print("Found:")
            for w in sorted(engine.state.found):
                print(colorize(w, Colors.GREEN, settings.use_colors))
            continue
            
        if text == "score":
            print_status()
            continue
            
        if text == "restart":
            print("Starting new game...")
            if session_path.exists():
                session_path.unlink()
            # Re-exec with --new
            # Or just return to main loop? Simpler to just exit and tell user to run again or wrap in a loop.
            # Let's wrap in a loop or just re-exec.
            # For now, let's just clear session and tell user to run again, or better:
            # We can't easily re-init everything in this structure without refactoring `run` to be a loop.
            # Let's just delete session and exit.
            print("Session cleared. Run 'itbee' again to start a new board.")
            return
            
        if text == "giveup":
            print("All words:")
            for e in board.words:
                print(f"{e.text} ({board.scores.get(e.text, 0)})")
            if session_path.exists():
                session_path.unlink()
            return
            
        if text == "quit":
            print("Bye")
            return

        ok, msg, pts = engine.guess(text)
        if ok:
            print(colorize(f"+{pts} OK", Colors.GREEN, settings.use_colors))
            # Save session
            save_session(session_path, {
                "seed": settings.seed,
                "found": list(engine.state.found),
                "score": engine.state.score
            })
        else:
            if msg == "duplicate":
                print(colorize(msg, Colors.YELLOW, settings.use_colors))
            else:
                print(colorize(msg, Colors.RED, settings.use_colors))
            
        # Update progress after each guess
        print_status()


if __name__ == "__main__":
    run()
