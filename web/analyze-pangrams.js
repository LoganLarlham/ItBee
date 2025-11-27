// Pangram Analysis Script
// This script analyzes the current game generator to measure pangram distribution
// Run with: node web/analyze-pangrams.js [iterations]

import { readFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Load the words list
const wordsData = JSON.parse(readFileSync(join(__dirname, 'words.json'), 'utf8'));

// Copy the SeededRandom class from generator.js
class SeededRandom {
    constructor(seed) {
        this.seed = seed;
        this.m = 0x80000000;
        this.a = 1103515245;
        this.c = 12345;
        this.state = seed ? seed : Math.floor(Math.random() * (this.m - 1));
    }

    nextInt() {
        this.state = (this.a * this.state + this.c) % this.m;
        return this.state;
    }

    nextFloat() {
        return this.nextInt() / (this.m - 1);
    }

    nextRange(start, end) {
        const range = end - start;
        return start + Math.floor(this.nextFloat() * range);
    }
}

// Copy generateGame function from generator.js
function generateGame(seed, wordList) {
    const rng = new SeededRandom(seed);

    // Italian letter frequencies (approximate)
    const vowels = ['a', 'e', 'i', 'o', 'u'];
    const consonants = ['b', 'c', 'd', 'f', 'g', 'h', 'l', 'm', 'n', 'p', 'q', 'r', 's', 't', 'v', 'z'];

    let attempts = 0;
    const maxAttempts = 50;

    while (attempts < maxAttempts) {
        // Pick letters
        const numVowels = rng.nextRange(2, 4); // 2-3 vowels
        const letters = new Set();

        // Add vowels
        while (letters.size < numVowels) {
            letters.add(vowels[rng.nextRange(0, vowels.length)]);
        }

        // Fill with consonants
        while (letters.size < 7) {
            letters.add(consonants[rng.nextRange(0, consonants.length)]);
        }

        const lettersArray = Array.from(letters);
        const required = lettersArray[rng.nextRange(0, lettersArray.length)];
        const others = lettersArray.filter(l => l !== required);

        // Find valid words
        const letterSet = new Set(lettersArray);
        const validWords = wordList.filter(word => {
            if (word.length < 4) return false;
            if (!word.includes(required)) return false;
            return word.split('').every(char => letterSet.has(char));
        });

        // Check if board is playable
        if (validWords.length >= 20 && validWords.length <= 80) {
            // Calculate scores
            const scores = {};
            validWords.forEach(word => {
                let points = word.length === 4 ? 1 : word.length;
                const unique = new Set(word.split(''));
                if (unique.size === 7) points += 7; // Pangram bonus
                scores[word] = points;
            });

            const totalPoints = Object.values(scores).reduce((a, b) => a + b, 0);

            return {
                seed: seed,
                center: required,
                outer: others,
                valid_words: validWords,
                scores: scores,
                total_points: totalPoints,
                threshold: Math.floor(totalPoints * 0.7)
            };
        }

        attempts++;
    }

    return null;
}

// Analysis function
function analyzeGenerator(numTests = 1000) {
    console.log(`\n🔬 Analyzing pangram distribution across ${numTests} games...\n`);

    const stats = {
        total: 0,
        successful: 0,
        failed: 0,
        pangramCounts: {},
        totalPangrams: 0,
        generationTimes: []
    };

    for (let i = 0; i < numTests; i++) {
        const seed = 100000 + i;
        const startTime = Date.now();

        try {
            const game = generateGame(seed, wordsData);
            const endTime = Date.now();

            if (game) {
                stats.successful++;
                stats.generationTimes.push(endTime - startTime);

                // Count pangrams
                const pangrams = game.valid_words.filter(word => {
                    return new Set(word.split('')).size === 7;
                });

                const count = pangrams.length;
                stats.pangramCounts[count] = (stats.pangramCounts[count] || 0) + 1;
                stats.totalPangrams += count;
            } else {
                stats.failed++;
            }
        } catch (error) {
            stats.failed++;
            console.error(`Failed on seed ${seed}:`, error.message);
        }

        stats.total++;

        if ((i + 1) % 100 === 0) {
            process.stdout.write(`Progress: ${i + 1}/${numTests}\r`);
        }
    }

    // Calculate statistics
    const avgTime = stats.generationTimes.reduce((a, b) => a + b, 0) / stats.generationTimes.length;
    const avgPangrams = stats.totalPangrams / stats.successful;

    console.log(`\n✅ Analysis Complete\n`);
    console.log(`Total games attempted: ${stats.total}`);
    console.log(`Successful generations: ${stats.successful} (${(stats.successful / stats.total * 100).toFixed(1)}%)`);
    console.log(`Failed generations: ${stats.failed}\n`);

    console.log(`⏱️  Performance:`);
    console.log(`Average generation time: ${avgTime.toFixed(2)}ms`);
    console.log(`Min time: ${Math.min(...stats.generationTimes)}ms`);
    console.log(`Max time: ${Math.max(...stats.generationTimes)}ms\n`);

    console.log(`📊 Pangram Distribution:`);
    const sortedCounts = Object.keys(stats.pangramCounts).map(Number).sort((a, b) => a - b);
    sortedCounts.forEach(count => {
        const percentage = (stats.pangramCounts[count] / stats.successful * 100).toFixed(1);
        const bar = '█'.repeat(Math.floor(percentage / 2));
        console.log(`${count} pangrams: ${stats.pangramCounts[count].toString().padStart(4)} (${percentage.padStart(5)}%) ${bar}`);
    });

    console.log(`\nAverage pangrams per game: ${avgPangrams.toFixed(2)}`);
    console.log(`Games with 0 pangrams: ${(stats.pangramCounts[0] || 0)} (${((stats.pangramCounts[0] || 0) / stats.successful * 100).toFixed(1)}%)`);
    console.log(`Games with 1+ pangrams: ${(stats.successful - (stats.pangramCounts[0] || 0))} (${((stats.successful - (stats.pangramCounts[0] || 0)) / stats.successful * 100).toFixed(1)}%)\n`);

    return stats;
}

// Run the analysis
const iterations = process.argv[2] ? parseInt(process.argv[2]) : 1000;
analyzeGenerator(iterations);
