// Translation system for UI
const translations = {
    en: {
        // Header
        title: "Italian Bee",
        rank_beginner: "Beginner",
        rank_good: "Good Start",
        rank_moving_up: "Moving Up",
        rank_good_job: "Good",
        rank_solid: "Solid",
        rank_nice: "Nice",
        rank_great: "Great",
        rank_amazing: "Amazing",
        rank_genius: "Genius",
        points: "points",
        goal_score: "Goal",
        words_label: "Words",

        // Controls
        btn_delete: "Delete",
        btn_enter: "Enter",
        btn_shuffle: "Shuffle",

        // Word list
        words_found: "Words Found",
        show_all_words: "🔍 Show All Words (Debug)",

        // Messages
        too_short: "Too short",
        missing_center: "Missing center letter",
        invalid_letter: "Invalid letter",
        already_found: "Already found",
        word_not_recognized: "Word not recognized",
        pangram: "Pangram!",

        // Modals
        help_title: "How to Play",
        help_objective: "🎯 Objective",
        help_objective_text: "Find all Italian words using the letters in the hive!",
        help_rules: "📝 Rules",
        help_rule_1: "Words must contain at least <strong>4 letters</strong>",
        help_rule_2: "Each word must include the <strong>center letter</strong> (yellow)",
        help_rule_3: "You can use letters multiple times",
        help_rule_4: "Find a <strong>pangram</strong> (word with all 7 letters) for bonus points! 🎊",
        help_commands: "⚡ Controls",
        help_cmd_1: "<strong>Click</strong> on letters or <strong>type</strong> on keyboard",
        help_cmd_2: "<strong>Enter</strong> to submit word",
        help_cmd_3: "<strong>Delete</strong> to remove last letter",
        help_cmd_4: "<strong>Space</strong> to shuffle letters",

        settings_title: "Settings",
        settings_game: "Game",
        settings_current_seed: "Current Seed:",
        settings_new_game: "🎲 New Random Game",
        settings_load_seed: "🔢 Load Seed",
        settings_seed_placeholder: "Enter seed...",
        settings_preferences: "Preferences",
        settings_language: "Language",
        settings_dark_mode: "Dark mode",
        settings_sound_effects: "Sound effects",
        settings_about: "About",
        settings_about_title: "Information",
        settings_about_desc: "A word game inspired by the New York Times Spelling Bee.",
        settings_about_tech: "Built with ❤️ using Client-Side Web Technologies",
        game_title: "Italian Bee",
        give_up: "🏳️ Give Up & Show Answers",

        // Solution Modal
        solution_title: "Solutions",
        solution_total: "Total words",
        solution_pangrams: "Pangrams",
        solution_by_length: "By Length",
        solution_letters: "Letters",
        solution_center: "Center",

        // Debug
        debug_total: "Total",
        debug_words: "words",
        debug_pangrams: "Pangrams",
        debug_console: "Complete list printed to console!\n\nTotal: {0} words\nPangrams: {1}\n\nOpen console (F12) to see full list.",
    },
    it: {
        // Header
        title: "Ape Italiana (per Marzia)",
        rank_beginner: "Principiante",
        rank_good: "Buon Inizio",
        rank_moving_up: "In Salita",
        rank_good_job: "Buono",
        rank_solid: "Solido",
        rank_nice: "Bello",
        rank_great: "Ottimo",
        rank_amazing: "Fantastico",
        rank_genius: "Genio",
        points: "punti",
        goal_score: "Obiettivo",
        words_label: "Parole",

        // Controls
        btn_delete: "Cancella",
        btn_enter: "Invio",
        btn_shuffle: "Mescola",

        // Word list
        words_found: "Parole Trovate",
        show_all_words: "🔍 Mostra Tutte le Parole (Debug)",

        // Messages
        too_short: "Troppo corta",
        missing_center: "Manca la lettera centrale",
        invalid_letter: "Lettera non valida",
        already_found: "Già trovata",
        word_not_recognized: "Parola non riconosciuta",
        pangram: "Pangramma!",

        // Modals
        help_title: "Come Si Gioca",
        help_objective: "🎯 Obiettivo",
        help_objective_text: "Trova tutte le parole italiane usando le lettere nell'alveare!",
        help_rules: "📝 Regole",
        help_rule_1: "Le parole devono contenere almeno <strong>4 lettere</strong>",
        help_rule_2: "Ogni parola deve includere la <strong>lettera centrale</strong> (gialla)",
        help_rule_3: "Puoi usare le lettere più volte",
        help_rule_4: "Trova un <strong>pangramma</strong> (parola con tutte le 7 lettere) per punti bonus! 🎊",
        help_commands: "⚡ Comandi",
        help_cmd_1: "<strong>Clicca</strong> sulle lettere o <strong>digita</strong> sulla tastiera",
        help_cmd_2: "<strong>Invio</strong> per inviare la parola",
        help_cmd_3: "<strong>Cancella</strong> per rimuovere l'ultima lettera",
        help_cmd_4: "<strong>Spazio</strong> per mescolare le lettere",

        settings_title: "Impostazioni",
        settings_game: "Gioco",
        settings_current_seed: "Seed Attuale:",
        settings_new_game: "🎲 Nuovo Gioco Casuale",
        settings_load_seed: "🔢 Carica Seed",
        settings_seed_placeholder: "Inserisci seed...",
        settings_preferences: "Preferenze",
        settings_language: "Lingua",
        settings_dark_mode: "Modalità scura",
        settings_sound_effects: "Effetti sonori",
        settings_about: "Informazioni",
        settings_about_title: "Informazioni",
        settings_about_desc: "Un gioco di parole ispirato al New York Times Spelling Bee.",
        settings_about_tech: "Sviluppato con ❤️ usando Tecnologie Web Client-Side",
        game_title: "Ape Italiana",
        give_up: "🏳️ Arrenditi & Mostra Soluzioni",

        // Solution Modal
        solution_title: "Soluzioni",
        solution_total: "Totale parole",
        solution_pangrams: "Pangrammi",
        solution_by_length: "Per Lunghezza",
        solution_letters: "Lettere",
        solution_center: "Centro",

        // Debug
        debug_total: "Totale",
        debug_words: "parole",
        debug_pangrams: "Pangrams",
        debug_console: "Lista completa stampata nella console!\n\nTotale: {0} parole\nPangrams: {1}\n\nApri la console (F12) per vedere la lista completa.",
    }
};

let currentLang = localStorage.getItem('language') || 'it';

function t(key) {
    return translations[currentLang][key] || key;
}

function setLanguage(lang) {
    currentLang = lang;
    localStorage.setItem('language', lang);
    updateUILanguage();
}

function updateUILanguage() {
    // Update all elements with data-i18n attribute
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (el.tagName === 'INPUT' && el.getAttribute('placeholder')) {
            el.placeholder = t(key);
        } else {
            el.innerHTML = t(key);
        }
    });

    // Update title
    const titleEl = document.querySelector('h1');
    if (titleEl) titleEl.textContent = t('title');

    // Update score display - preserve dynamic values
    const scoreEl = document.getElementById('score');
    const totalPointsEl = document.getElementById('total-points');
    if (scoreEl && totalPointsEl) {
        const score = scoreEl.textContent;
        const totalPoints = totalPointsEl.textContent;
        const scoreText = document.querySelector('.score-text');
        if (scoreText) {
            scoreText.innerHTML = `<span id="score">${score}</span> / <span id="total-points">${totalPoints}</span> <span data-i18n="points">${t('points')}</span>`;
        }
    }
}
