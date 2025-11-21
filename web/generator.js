// Seeded Random Number Generator
// Using Mulberry32 algorithm for deterministic randomness
class SeededRandom {
    constructor(seed) {
        this.seed = seed;
    }

    // Generate next random number [0, 1)
    next() {
        let t = this.seed += 0x6D2B79F5;
        t = Math.imul(t ^ t >>> 15, t | 1);
        t ^= t + Math.imul(t ^ t >>> 7, t | 61);
        return ((t ^ t >>> 14) >>> 0) / 4294967296;
    }

    // Random integer in range [min, max)
    randInt(min, max) {
        return Math.floor(this.next() * (max - min)) + min;
    }

    // Random element from array
    choice(arr) {
        return arr[this.randInt(0, arr.length)];
    }

    // Sample n unique elements from array
    sample(arr, n) {
        const copy = [...arr];
        const result = [];
        for (let i = 0; i < n; i++) {
            const idx = this.randInt(0, copy.length);
            result.push(copy[idx]);
            copy.splice(idx, 1);
        }
        return result;
    }

    // Shuffle array in place
    shuffle(arr) {
        for (let i = arr.length - 1; i > 0; i--) {
            const j = this.randInt(0, i + 1);
            [arr[i], arr[j]] = [arr[j], arr[i]];
        }
        return arr;
    }
}

// Calculate letter mask for a word  
function calculateMask(letters) {
    let mask = 0;
    for (const char of letters) {
        mask |= (1 << (char.charCodeAt(0) - 97));
    }
    return mask;
}

// Check if word uses only these letters
function wordOnlyUsesLetters(word, letters) {
    const letterSet = new Set(letters);
    for (const char of word) {
        if (!letterSet.has(char)) {
            return false;
        }
    }
    return true;
}

// Generate game board with given seed and word list
function generateGame(seed, wordList) {
    const rng = new SeededRandom(seed);

    // Italian letter frequencies
    const vowels = 'aeiou';
    const consonants = 'bcdfghlmnprstvz';

    // Try up to 50 times to generate a valid board
    for (let attempt = 0; attempt < 50; attempt++) {
        // Sample 7 letters: 2-3 vowels, rest consonants
        const numVowels = rng.randInt(2, 4); // 2 or 3
        const numConsonants = 7 - numVowels;

        const selectedVowels = rng.sample([...vowels], numVowels);
        const selectedConsonants = rng.sample([...consonants], numConsonants);
        const letters = [...selectedVowels, ...selectedConsonants];

        rng.shuffle(letters);

        const center = letters[0];
        const outer = letters.slice(1);

        // Filter word list
        const validWords = wordList.filter(word => {
            return word.length >= 4 &&
                word.includes(center) &&
                wordOnlyUsesLetters(word, letters);
        });

        // Check constraints (20-80 words for playability)
        if (validWords.length >= 20 && validWords.length <= 80) {
            // Calculate total points
            let totalPoints = 0;
            for (const word of validWords) {
                let pts = word.length === 4 ? 1 : word.length;
                // Pangram bonus (uses all 7 letters)
                const uniqueLetters = new Set(word);
                if (uniqueLetters.size === 7) {
                    pts += 7;
                }
                totalPoints += pts;
            }

            return {
                center,
                outer,
                valid_words: validWords,
                total_points: totalPoints,
                seed
            };
        }
    }

    // Failed to generate valid board
    throw new Error(`Could not generate valid board for seed ${seed}`);
}
