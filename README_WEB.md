# Ape Italiana - Web Deployment

## Overview

**Ape Italiana** is a fully client-side Italian Spelling Bee game deployed on Cloudflare Pages. No backend server required!

**Live URL**: https://42da8801.ape-italiana.pages.dev

## Architecture

### Client-Side Only ✨
- **No Backend**: All game logic runs in the browser
- **No Database**: Word list (46,293 Italian words) downloaded once and cached
- **No API Calls**: Game generation is instant
- **Offline Support**: Works without internet after first load
- **Zero Cost**: Free hosting on Cloudflare Pages

### Files Structure

```
web/
├── index.html           # Main HTML
├── style.css            # Core styles  
├── modal.css            # Modal dialogs
├── controls.css         # Game controls
├── loading.css          # Loading screen
├── app.js               # Game logic
├── app-init.js          # Event handlers & initialization
├── generator.js         # Seeded game generation
├── lexicon-loader.js    # Word list loader with caching
├── i18n.js              # Internationalization (IT/EN)
└── words.json           # Italian lexicon (586KB, ~195KB gzipped)
```

## Quick Deployment

### Prerequisites
- [Wrangler CLI](https://developers.cloudflare.com/workers/wrangler/install-and-update/) installed
- Cloudflare account

### Steps

1. **Export Lexicon** (if not already done):
   ```bash
   python3 scripts/export_lexicon_to_json.py
   ```

2. **Deploy to Cloudflare Pages**:
   ```bash
   cd web
   wrangler pages deploy . --project-name ape-italiana
   ```

That's it! Your app will be live at `https://<deployment-id>.ape-italiana.pages.dev`

## Development

### Local Testing
```bash
cd web
python3 -m http.server 8080
```

Visit http://localhost:8080

### How It Works

1. **First Visit**:
   - Loading screen shows  
   - Downloads `words.json` (~195KB gzipped)
   - Caches wordlist in localStorage
   - Loading screen fades out
   - Game starts instantly

2. **Subsequent Visits**:
   - Loads wordlist from cache immediately
   - No download needed
   - Instant start

3. **Game Generation**:
   - User clicks "New Game" or specifies a seed
   - Seeded RNG generates 7 letters (2-3 vowels, rest consonants)
   - Filters 46K words to find valid matches
   - Checks constraints (20-80 words for playability)
   - Displays game instantly (no network delay)

4. **Word Validation**:
   - Checks if submitted word is in cached valid word set
   - Instant feedback (no API call)

## Features

- ✅ **Deterministic Seeds**: Same seed = same game
- ✅ **Language Toggle**: Italian ↔ English UI
- ✅ **Dark Mode Ready**: Toggle in settings (to be styled)
- ✅ **Help & How to Play**: Modal dialogs
- ✅ **Seed Display**: Shows current game seed
- ✅ **Custom Seeds**: Start game from specific seed
- ✅ **Found Words List**: Track your progress
- ✅ **Score & Ranking System**: Beginner → Queen Bee
- ✅ **Pangram Detection**: +7 bonus points
- ✅ **Confetti Animation**: For pangrams
- ✅ **Debug Mode**: Show all valid words

## Cost Analysis

| Component | Old (Worker + D1) | New (Client-Side) |
|-----------|------------------|-------------------|
| **Hosting** | Pages: Free | Pages: Free |
| **Backend** | Worker: $5/mo (1M req) | None |
| **Database** | D1: $0.75/mo (10M reads) | None |
| **Bandwidth** | Minimal | ~200KB first load |
| **Total** | **~$5-10/month** | **$0/month** |

## Performance

- **First Load**: ~1-2 seconds (download + parse 195KB)
- **Cached Load**: <100ms  
- **New Game**: <50ms (instant, no API)
- **Word Check**: <1ms (local Set lookup)
- **Offline**: Fully functional

## Browser Compatibility

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

## Future Enhancements

- [ ] Implement dark mode styling
- [ ] Add sound effects
- [ ] Add hints system
- [ ] Progressive Web App (PWA) with offline manifest
- [ ] Daily challenge mode (date-based seed)
- [ ] Share score feature
- [ ] Leaderboard (optional backend integration)

## Notes

- Lexicon is sourced from `~/.it_spelling_bee/lexicon.sqlite`
- Word list updates require re-export and redeployment
- Cache version is controlled in `lexicon-loader.js` (increment to force refresh)
- Gzip compression is automatic via Cloudflare CDN

## Migration from Worker Backend

This app was originally built with:
- Cloudflare Worker (Python) for game generation 
- D1 database for word storage
- API endpoints for new-game and word validation

All functionality has been moved client-side for:
- Zero operating costs
- Better performance  
- Offline support
- Simpler deployment
