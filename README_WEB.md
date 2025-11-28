# 🐝 Ape Italiana - Italian Spelling Bee

A modern, responsive web implementation of the classic Spelling Bee word puzzle game, adapted for the Italian language.

## 🎯 Project Overview

**Ape Italiana** is a client-side web application where players construct Italian words using a set of 7 letters. The core objective is to find as many words as possible, with special bonuses for "pangrams" (words using all 7 letters).

### Key Features
- **Daily Puzzle**: A new, unique puzzle generated every day (UTC midnight).
- **Random Mode**: Generate unlimited random puzzles with guaranteed solutions.
- **Pangram Guarantee**: Every puzzle is guaranteed to have at least one word that uses all 7 letters.
- **Progressive Scoring**: Rank system from "Principiante" to "Ape Regina".
- **Responsive Design**: Fully adaptive layout that works on mobile, tablet, and desktop.
- **Offline Capable**: Entirely client-side logic with no server dependencies for gameplay.
- **State Persistence**: Auto-saves progress so you never lose your game.

---

## 🛠 Technology Stack

The project is built with **Vanilla JavaScript**, **CSS3**, and **HTML5**, prioritizing performance and simplicity.

### Core Technologies
- **HTML5**: Semantic structure with accessible modal dialogs.
- **CSS3**: 
  - **CSS Grid**: Used for the main application layout to ensure robust responsiveness and prevent overlaps.
  - **Flexbox**: Used for component-level layouts (buttons, lists).
  - **Variables**: Extensive use of CSS custom properties for theming (colors, fonts).
  - **Animations**: Keyframe animations for interactions (pop-ins, toasts).
- **JavaScript (ES6+)**:
  - **Modules**: Code organized into functional modules (`app.js`, `generator.js`, etc.).
  - **Async/Await**: For non-blocking lexicon loading.
  - **LocalStorage**: For persisting game state and settings.

### Tools & Deployment
- **Cloudflare Pages**: Static site hosting and deployment.
- **Wrangler**: CLI tool for local development and deployment to Cloudflare.

---

## 📂 Project Structure

The codebase is organized in the `web/` directory:

```
web/
├── index.html          # Main entry point and UI structure
├── style.css           # Core application styles and responsive grid layout
├── app.js              # Main Game class and core logic
├── app-init.js         # Application bootstrap and event wiring
├── generator.js        # Puzzle generation logic (seeds, pangrams)
├── lexicon-loader.js   # Efficient word list loading
├── i18n.js             # Internationalization (IT/EN support)
├── words.json          # Compressed Italian dictionary
├── modal.css           # Styles for help/settings modals
├── controls.css        # Styles for game control buttons
└── loading.css         # Styles for the initial loading screen
```

---

## 💾 Data Handling

### The Lexicon (`words.json`)
The game relies on a curated list of valid Italian words.
- **Format**: JSON array of strings.
- **Loading**: `lexicon-loader.js` fetches this file asynchronously on startup.
- **Optimization**: The file is loaded once and cached in memory as a `Set` for O(1) lookup times during gameplay.

### Game State (`localStorage`)
Player progress is saved automatically to the browser's LocalStorage.
- **Key**: `gameState`
- **Schema**:
  ```json
  {
    "daily": {
      "seed": 12345,
      "foundWords": ["ciao", "amico"],
      "score": 15,
      "date": "2023-11-28"
    },
    "random": { ... },
    "lastPlayed": "daily"
  }
  ```
- **Settings**: Preferences like Dark Mode and Language are stored separately.

---

## 🎮 Game Logic

### 1. Puzzle Generation (`generator.js`)
Puzzles are generated deterministically using a seeded random number generator.
- **Seed**: A numeric value (e.g., date-based for daily puzzles).
- **Algorithm**:
  1. Select a "pangram" word from the dictionary (7 unique letters).
  2. Shuffle letters to assign the "center" letter (mandatory) and "outer" letters.
  3. Verify the board has a minimum number of valid words and points.
  4. **Guarantee**: The generator retries until a valid board with at least one pangram is found.

### 2. The Game Loop (`app.js`)
The `Game` class manages the runtime state:
- **Input**: Handles clicks and keyboard events.
- **Validation**: Checks if a word:
  - Is in the dictionary.
  - Uses only available letters.
  - Contains the center letter.
  - Is at least 4 letters long.
- **Scoring**:
  - 4 letters: 1 point.
  - 5+ letters: 1 point per letter.
  - Pangram: +7 bonus points.

---

## 🎨 Styling & Layout

### Responsive Grid System
The application uses a **CSS Grid** layout to handle different screen sizes without overlapping elements.

**Desktop Layout**:
- **Grid**: 2 Columns (Game | Sidebar).
- **Rows**: Explicit rows for Hive, Input, Message, and Actions.
- **Behavior**: The "Found Words" list moves to a sidebar on the right.

**Mobile Layout**:
- **Grid**: Single column vertical stack.
- **Behavior**: The "Found Words" list appears below the game area.
- **Scrolling**: `overflow-y: auto` ensures content is accessible on small screens.

### Visual Design
- **Theme**: Clean, modern aesthetic with a "Golden Yellow" primary color (`#FFD700`).
- **Feedback**: Visual cues for valid words, errors, and ranking up.
- **Typography**: Uses 'Outfit' font for a friendly, geometric look.
