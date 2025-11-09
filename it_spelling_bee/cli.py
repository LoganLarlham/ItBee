import argparse
import random
import sys

from .config import Settings
from .lexicon.store import Lexicon
from .generator import generate_board
from .engine import Engine
from .letters import shuffle_letters


def show_intro():
    print("""
                                                                                
                                                                      
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
==================
Create words using the given letters. Each word must:
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
  giveup   - Show all possible words
    quit     - Exit the game
    printseed - Print the current game's seed (decimal and hex)
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

def run(argv=None):
    parser = argparse.ArgumentParser(prog="itbee", description="Italian Spelling Bee - A word puzzle game")
    parser.add_argument("--seed", type=int, default=None, help="use specific seed for board generation")
    parser.add_argument("--rules", action="store_true", help="show game rules and scoring")
    parser.add_argument("--hint", action="store_true", help="show a random unguessed word")
    parser.add_argument("--solution", action="store_true", help="show all possible words and exit")
    parser.add_argument("--new", action="store_true", help="force new board generation")
    parser.add_argument("--dumpboard", action="store_true", help="print board data in JSON format")
    
    args = parser.parse_args(argv)
    
    if args.rules:
        show_rules()
        return

    settings = Settings()
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
        show_intro()

    required = board.letters.required
    others = list(board.letters.others)
    print(f"[{required.upper()}] ", " ".join(others))
    print(f"Found 0/{len(board.words)}   Score 0 / {board.total_points}   Goal {board.threshold}")

    if args.hint:
        hint = engine.get_hint()
        if hint:
            print(hint)
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
            print("Commands: help, shuffle, hint, list, score, giveup, printseed, quit")
            continue
        if text == "printseed":
            # print the current board's seed (decimal and hex)
            print(f"Board seed: {settings.seed} (0x{settings.seed:X})")
            continue
        if text == "hint":
            hint = engine.get_hint()
            if hint:
                print(hint)
            else:
                print("No more words to find!")
            continue
        if text == "shuffle":
            _, others = shuffle_letters(required, others, rng)
            others = list(others)
            print(f"[{required.upper()}] ", " ".join(others))
            continue
        if text == "list":
            print("Found:")
            for w in sorted(engine.state.found):
                print(w)
            continue
        if text == "score":
            p = engine.progress()
            print(f"Found {p['found']}/{p['total_words']}   Score {p['score']} / {p['threshold']}")
            continue
        if text == "giveup":
            print("All words:")
            for e in board.words:
                print(e.text, board.scores.get(e.text, 0))
            return
        if text == "quit":
            print("Bye")
            return

        ok, msg, pts = engine.guess(text)
        if ok:
            print(f"+{pts} OK")
        else:
            print(msg)
            
        # Update progress after each guess
        p = engine.progress()
        print(f"Found {p['found']}/{p['total_words']}   Score {p['score']} / {p['total_points']}   Goal {p['threshold']}")


if __name__ == "__main__":
    run()
