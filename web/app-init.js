// Start
window.addEventListener('DOMContentLoaded', async () => {
    console.log('DOM loaded, loading lexicon...');

    // Get loading screen elements
    const loadingScreen = document.getElementById('loading-screen');
    const progressFill = document.getElementById('progress-fill');
    const loadingBytes = document.getElementById('loading-bytes');
    const loadingTotal = document.getElementById('loading-total');

    // Modal elements
    const helpModal = document.getElementById('help-modal');
    const settingsModal = document.getElementById('settings-modal');
    const helpBtn = document.getElementById('btn-help');
    const settingsBtn = document.getElementById('btn-settings');

    try {
        // Load lexicon with progress
        await lexiconLoader.load((received, total) => {
            const percent = (received / total) * 100;
            progressFill.style.width = percent + '%';
            loadingBytes.textContent = Math.round(received / 1024);
            loadingTotal.textContent = Math.round(total / 1024);
        });

        console.log('Lexicon loaded, initializing game...');

        // Hide loading screen
        setTimeout(() => {
            loadingScreen.classList.remove('active');
        }, 300);

    } catch (error) {
        console.error('Failed to load lexicon:', error);
        alert('Failed to load word list. Please refresh the page.');
        return;
    }

    const game = new Game();

    // Setup events once after first init
    game.setupEvents();

    // Check for saved state and restore if available
    const savedState = game.loadGameState();
    if (savedState && savedState.seed) {
        // Restore the game with saved state
        console.log('Restoring saved game state');
        await game.init(savedState.seed, game.gameType);
        game.restoreGameState(savedState);
    } else {
        // Start fresh daily puzzle
        console.log('Starting fresh daily puzzle');
        await game.init(null, 'daily');
    }

    // New game controls - prevent modal from closing
    const newGameBtn = document.getElementById('btn-new-game');
    const seedGameBtn = document.getElementById('btn-seed-game');
    const showWordsBtn = document.getElementById('btn-show-words');

    console.log('New game button:', newGameBtn);
    console.log('Seed game button:', seedGameBtn);
    console.log('Show words button:', showWordsBtn);

    if (newGameBtn) {
        newGameBtn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            console.log('New random game clicked');
            // Close modal first
            if (settingsModal) {
                settingsModal.classList.remove('active');
            }
            // Start a new random game
            setTimeout(() => {
                game.init(null, 'random');
            }, 100);
        });
    }

    if (seedGameBtn) {
        seedGameBtn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            const seedInput = document.getElementById('seed-input');
            const seed = parseInt(seedInput.value);
            console.log('Seed game clicked, seed:', seed);
            if (!isNaN(seed)) {
                // Close modal first
                if (settingsModal) {
                    settingsModal.classList.remove('active');
                }
                // Start a random game with specific seed
                setTimeout(() => {
                    game.init(seed, 'random');
                }, 100);
            }
        });
    }

    if (showWordsBtn) {
        showWordsBtn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            console.log('Show words clicked');
            game.showAllWords();
        });
    }

    // Modal functionality
    // Elements moved to top of scope

    // Open modals
    if (helpBtn) {
        helpBtn.addEventListener('click', (e) => {
            console.log('Help button clicked!');
            e.preventDefault();
            e.stopPropagation();
            if (helpModal) {
                helpModal.classList.add('active');
                console.log('Added active class to help modal');
            }
        });
    }

    if (settingsBtn) {
        settingsBtn.addEventListener('click', (e) => {
            console.log('Settings button clicked!');
            e.preventDefault();
            e.stopPropagation();
            if (settingsModal) {
                settingsModal.classList.add('active');
                console.log('Added active class to settings modal');
            }
        });
    }

    // Close modals
    document.querySelectorAll('.modal-close').forEach(btn => {
        btn.addEventListener('click', () => {
            const modalId = btn.getAttribute('data-modal');
            console.log('Closing modal:', modalId);
            const modal = document.getElementById(modalId);
            if (modal) {
                modal.classList.remove('active');
            }
        });
    });

    // Close on background click
    if (helpModal) {
        helpModal.addEventListener('click', (e) => {
            if (e.target === helpModal) {
                helpModal.classList.remove('active');
            }
        });
    }

    if (settingsModal) {
        settingsModal.addEventListener('click', (e) => {
            if (e.target === settingsModal) {
                settingsModal.classList.remove('active');
            }
        });
    }

    const solutionModal = document.getElementById('solution-modal');
    if (solutionModal) {
        solutionModal.addEventListener('click', (e) => {
            if (e.target === solutionModal) {
                solutionModal.classList.remove('active');
            }
        });
    }

    // Settings persistence
    const darkMode = document.getElementById('dark-mode');
    const languageSelect = document.getElementById('language-select');

    if (darkMode) {
        // Apply dark mode from localStorage on page load
        const isDarkMode = localStorage.getItem('darkMode') === 'true';
        if (isDarkMode) {
            document.body.classList.add('dark-mode');
        }
        darkMode.checked = isDarkMode;

        // Toggle dark mode when checkbox changes
        darkMode.addEventListener('change', () => {
            const enabled = darkMode.checked;
            localStorage.setItem('darkMode', enabled);

            if (enabled) {
                document.body.classList.add('dark-mode');
            } else {
                document.body.classList.remove('dark-mode');
            }
        });
    }

    // Language selector
    if (languageSelect) {
        languageSelect.value = currentLang;
        languageSelect.addEventListener('change', () => {
            setLanguage(languageSelect.value);
        });
    }

    // Initialize UI language
    updateUILanguage();
    console.log('Initialization complete');
});
