# 🐝 Ape Italiana - Italian Spelling Bee

Live on [Itbee.app](https://ItBee.app) 

A web implementation of the NYT Spelling Bee word puzzle game, but in Italian.

[![Live Demo](https://img.shields.io/badge/demo-live-success)](https://ape-italiana.pages.dev)

## About

**Ape Italiana** challenges players to construct Italian words using a set of 7 letters arranged in a hexagonal grid. Each puzzle features:

- A center letter that must be used in every word
- 6 surrounding letters that can be used in any combination
- A guaranteed "pangram" - at least one word using all 7 letters

## Features

- **Daily Puzzle** - New challenge every day at UTC midnight
- **Random Mode** - Generate unlimited practice puzzles
- **Auto-save** - Never lose your progress
- **Dark Mode** - Easy on the eyes
- **Bilingual UI** - Italian and English support

## Tech

- **Frontend**: Vanilla JavaScript, CSS Grid, HTML5
- **Dictionary**: 46,000+ Italian words with whitelist/blacklist support
- **Deployment**: Cloudflare Pages
- **Game Logic**: Deterministic seeded random generation

## Project Structure

- `web/` - Client-side web application
- `it_spelling_bee/` - Python CLI and lexicon builder
- `data/` - Dictionary whitelist/blacklist
- `scripts/` - Build tools

## Development

```bash
# Install dependencies (for lexicon building)
pip install -r requirements.txt

# Build custom lexicon (optional)
python -m it_spelling_bee.lexicon.build \
    --dict /path/to/it_IT.dic \
    --whitelist data/whitelist.txt \
    --blacklist data/blacklist.txt

# Export to web format
python scripts/export_lexicon_to_json.py

# Deploy
cd web && wrangler pages deploy . --project-name ape-italiana
```


## Credits

Inspired by the New York Times Spelling Bee. Dictionary sourced from Italian Hunspell dictionaries and wordfreq.
Built with the help of Antigravity.
