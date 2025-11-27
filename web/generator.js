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
function generateGame(seed, wordList, requirePangram = true) {
    const rng = new SeededRandom(seed);

    // Italian letter frequencies
    const vowels = 'aeiou';
    const consonants = 'bcdf ghlmnprstvz';

    // If pangram is required, try multiple seed variations
    const maxPangramAttempts = requirePangram ? 100 : 1;

    for (let pangramAttempt = 0; pangramAttempt < maxPangramAttempts; pangramAttempt++) {
        // Use a derived seed for retries
        const attemptSeed = seed + (pangramAttempt * 1000);
        const attemptRng = new SeededRandom(attemptSeed);

        // Try up to 50 times to generate a valid board with this seed
        for (let attempt = 0; attempt < 50; attempt++) {
            // Sample 7 letters: 2-3 vowels, rest consonants
            const numVowels = attemptRng.randInt(2, 4); // 2 or 3
            const numConsonants = 7 - numVowels;

            const selectedVowels = attemptRng.sample([...vowels], numVowels);
            const selectedConsonants = attemptRng.sample([...consonants], numConsonants);
            const letters = [...selectedVowels, ...selectedConsonants];

            attemptRng.shuffle(letters);

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
                // Check for pangrams if required
                const pangrams = validWords.filter(word => new Set(word).size === 7);

                if (requirePangram && pangrams.length === 0) {
                    continue; // Try next board variation
                }

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

                if (requirePangram && pangramAttempt > 0) {
                    console.log(`Found pangram on attempt ${pangramAttempt + 1} (${pangrams.length} pangrams)`);
                }

                return {
                    center,
                    outer,
                    valid_words: validWords,
                    total_points: totalPoints,
                    seed: attemptSeed // Return the actual seed used
                };
            }
        }
    }

    // Failed to generate valid board with pangram
    if (requirePangram) {
        console.warn(`Could not generate board with pangram for seed ${seed} after ${maxPangramAttempts} attempts, returning best attempt`);
        // Fall back to generating without pangram requirement
        return generateGame(seed, wordList, false);
    }

    throw new Error(`Could not generate valid board for seed ${seed}`);
}

