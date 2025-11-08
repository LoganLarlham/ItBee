import argparse
import random
import sys

from .config import Settings
from .lexicon.store import Lexicon
from .generator import generate_board
from .engine import Engine
from .letters import shuffle_letters


def run(argv=None):
    parser = argparse.ArgumentParser(prog="itbee")
    parser.add_argument("--seed", type=int, default=None)
    args = parser.parse_args(argv)
    settings = Settings()
    if args.seed is not None:
        settings.seed = args.seed
    rng = random.Random(settings.seed)
    lex = Lexicon()
    board = generate_board(lex, settings, rng)
    engine = Engine(board)

    required = board["letters"]["required"]
    others = board["letters"]["others"]
    print(f"[{required.upper()}] ", " ".join(others))
    print(f"Found 0/{len(board['words'])}   Score 0 / {board['threshold']}   Goal {board['threshold']}")

    while True:
        try:
            text = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye")
            return
        if not text:
            continue
        if text == "help":
            print("Commands: help, shuffle, list, score, giveup, quit")
            continue
        if text == "shuffle":
            _, others = shuffle_letters(required, others, rng)
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
            for e in board["words"]:
                print(e["text"], board["scores"].get(e["text"], 0))
            return
        if text == "quit":
            print("Bye")
            return

        ok, msg, pts = engine.guess(text)
        if ok:
            print(f"+{pts} OK")
        else:
            print(msg)


if __name__ == "__main__":
    run()
