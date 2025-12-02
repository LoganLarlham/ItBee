// Daily seed calculation
function getDailySeed() {
    const now = new Date();
    const utc = new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate()));
    const epoch = Date.UTC(2024, 0, 1); // Jan 1, 2024
    const daysSinceEpoch = Math.floor((utc.getTime() - epoch) / 86400000);
    return 100000 + daysSinceEpoch; // Seeds start at 100000
}

function getTodayDateString() {
    const now = new Date();
    return `${now.getUTCFullYear()}-${String(now.getUTCMonth() + 1).padStart(2, '0')}-${String(now.getUTCDate()).padStart(2, '0')}`;
}

// Game class

class Game {
    constructor() {
        this.center = "";
        this.outer = [];
        this.validWords = new Set();
        this.foundWords = new Set();
        this.score = 0;
        this.totalPoints = 0;
        this.input = "";
        this.currentSeed = null;
        this.gameType = 'daily'; // 'daily' or 'random'

        // DOM Elements
        this.elInput = document.getElementById('input-text');
        this.elScore = document.getElementById('score');
        this.elTotalPoints = document.getElementById('total-points');
        this.elGoalScore = document.getElementById('goal-score');
        this.elScoreBar = document.getElementById('score-bar');
        this.elRank = document.getElementById('rank');
        this.elWordList = document.getElementById('word-list');
        this.elFoundWordCount = document.getElementById('found-word-count');
        this.elTotalWords = document.getElementById('total-words');
        this.elMessage = document.getElementById('message-area');
        this.elSeedDisplay = document.getElementById('seed-display');

        this.init();
    }

    async init(seed = null, gameType = 'daily') {
        // Generate game client-side using local lexicon
        let data;
        try {
            // Ensure lexicon is loaded
            if (!lexiconLoader.isLoaded()) {
                throw new Error('Lexicon not loaded yet');
            }

            const wordList = await lexiconLoader.load();

            // Determine seed and game type
            this.gameType = gameType;
            if (gameType === 'daily' && seed === null) {
                seed = getDailySeed();
                console.log('Starting daily puzzle, seed:', seed);
            } else if (seed === null) {
                // Random game
                seed = Math.floor(Math.random() * 999999) + 1;
                console.log('Starting random game, seed:', seed);
            }

            // Generate game
            data = generateGame(seed, wordList);
            console.log(`Generated ${gameType} game for seed ${seed}:`, {
                letters: data.center + data.outer.join(''),
                words: data.valid_words.length,
                points: data.total_points
            });
            this.currentSeed = seed;
        } catch (error) {
            console.error('Failed to generate game:', error);
            // Show error to user
            this.showToast(t('error_generating'), 'error');
            return;
        }

        this.center = data.center;
        this.outer = data.outer;
        this.validWords = new Set(data.valid_words);
        this.totalPoints = data.total_points;

        // Reset game state
        this.foundWords = new Set();
        this.score = 0;
        this.input = "";

        this.elWordList.innerHTML = '';
        if (this.elFoundWordCount) this.elFoundWordCount.textContent = '0';
        if (this.elTotalWords) this.elTotalWords.textContent = this.validWords.size;
        if (this.elTotalPoints) this.elTotalPoints.textContent = this.totalPoints;
        if (this.elGoalScore) this.elGoalScore.textContent = Math.floor(this.totalPoints * 0.55);
        this.updateInputDisplay();
        this.updateScore();
        this.renderHive();
        this.updateSeedDisplay();

        // Save initial state
        this.saveGameState();

        // Track game start event (Umami Analytics)
        if (typeof umami !== 'undefined') {
            umami.track('game_start', { type: this.gameType, seed: this.currentSeed });
        }
    }

    renderHive() {
        // Center
        const centerEl = document.querySelector('[data-letter="center"]');
        if (centerEl) {
            centerEl.textContent = this.center;
            centerEl.onclick = () => this.addLetter(this.center);
        }

        // Outer letters (indices 0-5)
        this.outer.forEach((char, i) => {
            const el = document.querySelector(`[data-letter="${i}"]`);
            if (el) {
                el.textContent = char;
                el.onclick = () => this.addLetter(char);
            }
        });
    }

    setupEvents() {
        // Keyboard
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Backspace') {
                this.deleteLetter();
            } else if (e.key === 'Enter') {
                this.submit();
            } else if (e.key === ' ') {
                e.preventDefault();
                this.shuffle();
            } else if (/^[a-zA-Z]$/.test(e.key)) {
                this.addLetter(e.key.toLowerCase());
            }
        });

        // Buttons
        const btnDelete = document.getElementById('btn-delete');
        if (btnDelete) btnDelete.onclick = () => this.deleteLetter();

        const btnEnter = document.getElementById('btn-submit'); // ID was btn-submit in HTML, but btn-enter in some JS?
        if (btnEnter) btnEnter.onclick = () => this.submit();

        const btnShuffle = document.getElementById('btn-shuffle');
        if (btnShuffle) btnShuffle.onclick = () => this.shuffle();
    }

    addLetter(char) {
        this.input += char;
        this.updateInputDisplay();
    }

    deleteLetter() {
        this.input = this.input.slice(0, -1);
        this.updateInputDisplay();
    }

    updateInputDisplay() {
        this.elInput.textContent = this.input;
        // Highlight center letter?
        // Simple text for now
    }

    shuffle() {
        // Fisher-Yates shuffle for outer letters
        for (let i = this.outer.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [this.outer[i], this.outer[j]] = [this.outer[j], this.outer[i]];
        }
        this.renderHive();

        // Add animation class
        const hive = document.querySelector('.hive');
        if (hive) {
            hive.style.animation = 'none';
            hive.offsetHeight; /* trigger reflow */
            hive.style.animation = 'popIn 0.3s ease';
        }
    }

    submit() {
        const word = this.input.toLowerCase();
        if (!word) return;

        const result = this.checkWord(word);

        if (result.ok) {
            this.foundWords.add(word);
            this.score += result.points;
            this.updateScore();
            this.addWordToList(word);
            this.showToast(`+${result.points} ${result.message || ''}`, 'success');

            // Trigger confetti for pangrams or high scores
            if (result.points >= 7) {
                this.triggerConfetti();
            }

            // Save progress
            this.saveGameState();
        } else {
            this.showToast(result.message, 'error');
            this.shakeInput();
        }

        // Always clear input after submit
        this.input = "";
        this.updateInputDisplay();
    }

    checkWord(word) {
        if (word.length < 4) return { ok: false, message: "Troppo corta" };
        if (!word.includes(this.center)) return { ok: false, message: "Manca la lettera centrale" };

        const allowed = new Set([...this.outer, this.center]);
        for (let char of word) {
            if (!allowed.has(char)) return { ok: false, message: "Lettera non valida" };
        }

        if (this.foundWords.has(word)) return { ok: false, message: "Già trovata" };

        if (!this.validWords.has(word)) return { ok: false, message: "Parola non riconosciuta" };

        // Calculate points
        let points = 1;
        if (word.length === 4) points = 1;
        else points = word.length;

        // Pangram bonus
        const unique = new Set(word);
        if (unique.size === 7) {
            points += 7;

            // Track pangram event (Umami Analytics)
            if (typeof umami !== 'undefined') {
                umami.track('pangram_found', { word: word, type: this.gameType });
            }

            return { ok: true, points, message: "PANGRAMMA!" };
        }

        return { ok: true, points };
    }

    updateScore() {
        this.elScore.textContent = this.score;
        if (this.elGoalScore && this.totalPoints) {
            const goalScore = Math.floor(this.totalPoints * 0.55);
            this.elGoalScore.textContent = goalScore;

            // Track win event when player reaches goal score (Umami Analytics)
            if (this.score >= goalScore && this.score - (this.score > 0 ? 1 : 0) < goalScore) {
                if (typeof umami !== 'undefined') {
                    umami.track('game_win', {
                        type: this.gameType,
                        score: this.score,
                        words_found: this.foundWords.size
                    });
                }
            }
        }
        if (this.elTotalPoints) {
            this.elTotalPoints.textContent = this.totalPoints;
        }
        if (this.elFoundWordCount) {
            this.elFoundWordCount.textContent = this.foundWords.size;
        }
        if (this.elTotalWords) {
            this.elTotalWords.textContent = this.validWords.size;
        }
        const pct = Math.min(100, (this.score / this.totalPoints) * 100);
        this.elScoreBar.style.width = `${pct}%`;

        // Update rank text
        let rank = "Principiante";
        if (pct > 2) rank = "Buon inizio";
        if (pct > 5) rank = "In movimento";
        if (pct > 8) rank = "Buono";
        if (pct > 15) rank = "Solido";
        if (pct > 25) rank = "Esperto";
        if (pct > 40) rank = "Eccellente";
        if (pct > 50) rank = "Genio";
        if (pct > 70) rank = "Ape Regina";
        this.elRank.textContent = rank;
    }

    addWordToList(word) {
        const li = document.createElement('li');
        li.textContent = word;
        this.elWordList.prepend(li);
        if (this.elFoundWordCount) {
            this.elFoundWordCount.textContent = this.foundWords.size;
        }
    }

    showToast(msg, type = 'neutral') {
        const container = document.getElementById('toast-container');
        const el = document.createElement('div');
        el.className = 'toast';
        if (type === 'success') el.classList.add('success');

        // Icon
        let icon = '';
        if (type === 'success') icon = '<span>✨</span>';
        if (type === 'error') icon = '<span>⚠️</span>';

        el.innerHTML = `${icon} ${msg}`;

        container.appendChild(el);
        setTimeout(() => el.remove(), 2500);
    }

    shakeInput() {
        const el = document.querySelector('.input-area');
        el.style.transform = 'translateX(5px)';
        setTimeout(() => el.style.transform = 'translateX(-5px)', 50);
        setTimeout(() => el.style.transform = 'translateX(5px)', 100);
        setTimeout(() => el.style.transform = 'translateX(0)', 150);
    }

    triggerConfetti() {
        const colors = ['#FFD700', '#ffeb3b', '#ffc107', '#2c3e50', '#ffffff'];
        for (let i = 0; i < 50; i++) {
            const el = document.createElement('div');
            el.style.position = 'fixed';
            el.style.left = '50%';
            el.style.top = '50%';
            el.style.width = '10px';
            el.style.height = '10px';
            el.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
            el.style.borderRadius = '50%';
            el.style.pointerEvents = 'none';
            el.style.zIndex = '1000';
            document.body.appendChild(el);

            const angle = Math.random() * Math.PI * 2;
            const velocity = 5 + Math.random() * 10;
            const dx = Math.cos(angle) * velocity;
            const dy = Math.sin(angle) * velocity;

            let x = 0;
            let y = 0;
            let opacity = 1;

            const anim = setInterval(() => {
                x += dx;
                y += dy + 0.5; // gravity
                opacity -= 0.02;
                el.style.transform = `translate(${x}px, ${y}px)`;
                el.style.opacity = opacity;

                if (opacity <= 0) {
                    clearInterval(anim);
                    el.remove();
                }
            }, 16);
        }
    }

    updateSeedDisplay() {
        const seedText = `${this.currentSeed}`;
        if (this.elSeedDisplay) {
            this.elSeedDisplay.textContent = `Seed: ${seedText}`;
        }
        const modalSeed = document.getElementById('seed-display-modal');
        if (modalSeed) {
            modalSeed.textContent = seedText;
        }
    }



    showAllWords() {
        const wordsByLength = {};
        const pangrams = [];

        for (const word of this.validWords) {
            const len = word.length;
            if (!wordsByLength[len]) wordsByLength[len] = [];
            wordsByLength[len].push(word);

            // Check if pangram (uses all 7 letters)
            const uniqueLetters = new Set(word);
            if (uniqueLetters.size === 7) {
                pangrams.push(word);
            }
        }

        // Build modal content
        const solutionList = document.getElementById('solution-list');
        solutionList.innerHTML = '';

        // Summary section
        const summary = document.createElement('div');
        summary.className = 'solution-section';
        summary.innerHTML = `
            <p><strong>${t('solution_center')}:</strong> ${this.center.toUpperCase()}</p>
            <p><strong>${t('solution_letters')}:</strong> ${this.center.toUpperCase()}, ${this.outer.map(l => l.toUpperCase()).join(', ')}</p>
            <p><strong>${t('solution_total')}:</strong> ${this.validWords.size}</p>
            <p><strong>${t('solution_pangrams')}:</strong> ${pangrams.length}</p>
        `;
        solutionList.appendChild(summary);

        // Pangrams section
        if (pangrams.length > 0) {
            const pangramSection = document.createElement('div');
            pangramSection.className = 'solution-section';
            pangramSection.innerHTML = `<h3>🎊 ${t('solution_pangrams')}</h3>`;

            const pangramWords = document.createElement('div');
            pangramWords.className = 'solution-words';
            pangrams.sort().forEach(word => {
                const span = document.createElement('span');
                span.className = 'solution-word pangram';
                if (this.foundWords.has(word)) {
                    span.classList.add('found');
                }
                span.textContent = word;
                pangramWords.appendChild(span);
            });
            pangramSection.appendChild(pangramWords);
            solutionList.appendChild(pangramSection);
        }

        // Words by length
        const byLengthSection = document.createElement('div');
        byLengthSection.className = 'solution-section';
        byLengthSection.innerHTML = `<h3>📝 ${t('solution_by_length')}</h3>`;

        const lengths = Object.keys(wordsByLength).map(Number).sort((a, b) => a - b);
        lengths.forEach(len => {
            const lengthGroup = document.createElement('div');
            lengthGroup.style.marginBottom = '1rem';

            const heading = document.createElement('h4');
            heading.style.fontSize = '0.9rem';
            heading.style.color = '#666';
            heading.style.marginBottom = '0.5rem';
            heading.textContent = `${len} ${len === 1 ? 'lettera' : 'lettere'} (${wordsByLength[len].length})`;
            lengthGroup.appendChild(heading);

            const wordsDiv = document.createElement('div');
            wordsDiv.className = 'solution-words';

            wordsByLength[len].sort().forEach(word => {
                const span = document.createElement('span');
                span.className = 'solution-word';
                if (this.foundWords.has(word)) {
                    span.classList.add('found');
                }
                span.textContent = word;
                wordsDiv.appendChild(span);
            });

            lengthGroup.appendChild(wordsDiv);
            byLengthSection.appendChild(lengthGroup);
        });

        solutionList.appendChild(byLengthSection);

        // Open the modal
        const modal = document.getElementById('solution-modal');
        if (modal) {
            modal.classList.add('active');
        }
    }

    saveGameState() {
        try {
            const state = {
                dailyGame: null,
                randomGame: null,
                lastPlayedType: this.gameType
            };

            const gameData = {
                seed: this.currentSeed,
                foundWords: Array.from(this.foundWords),
                score: this.score,
                timestamp: Date.now(),
                center: this.center,
                outer: this.outer
            };

            if (this.gameType === 'daily') {
                gameData.date = getTodayDateString();
                state.dailyGame = gameData;
                // Preserve random game if it exists
                const existing = localStorage.getItem('game_state');
                if (existing) {
                    const existingState = JSON.parse(existing);
                    state.randomGame = existingState.randomGame;
                }
            } else {
                state.randomGame = gameData;
                // Preserve daily game if it exists
                const existing = localStorage.getItem('game_state');
                if (existing) {
                    const existingState = JSON.parse(existing);
                    state.dailyGame = existingState.dailyGame;
                }
            }

            localStorage.setItem('game_state', JSON.stringify(state));
        } catch (error) {
            console.error('Failed to save game state:', error);
        }
    }

    loadGameState() {
        try {
            const saved = localStorage.getItem('game_state');
            if (!saved) return null;

            const state = JSON.parse(saved);

            // Check if we should load daily or random game
            const gameToLoad = this.gameType === 'daily' ? state.dailyGame : state.randomGame;

            if (!gameToLoad) return null;

            // For daily games, check if it's still today's puzzle
            if (this.gameType === 'daily') {
                if (gameToLoad.date !== getTodayDateString()) {
                    // Old daily puzzle, clear it
                    console.log('Daily puzzle expired, starting fresh');
                    return null;
                }
            }

            return gameToLoad;
        } catch (error) {
            console.error('Failed to load game state:', error);
            return null;
        }
    }

    restoreGameState(savedState) {
        this.foundWords = new Set(savedState.foundWords);
        this.score = savedState.score;

        // Update UI
        this.elWordList.innerHTML = '';
        this.foundWords.forEach(word => this.addWordToList(word));
        this.updateScore();

        console.log('Game state restored:', this.foundWords.size, 'words found');
    }
}
