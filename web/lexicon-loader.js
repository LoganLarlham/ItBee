// Lexicon Loader - Download and cache Italian word list
class LexiconLoader {
    constructor() {
        this.words = null;
        this.loading = false;
        this.loaded = false;
    }

    async load(onProgress = null) {
        if (this.loaded) return this.words;
        if (this.loading) {
            // Wait for existing load to complete
            while (this.loading) {
                await new Promise(resolve => setTimeout(resolve, 100));
            }
            return this.words;
        }

        this.loading = true;

        try {
            // Check cache first
            const cached = localStorage.getItem('lexicon_cache');
            const cacheVersion = localStorage.getItem('lexicon_version');
            const currentVersion = '1.0'; // Increment this when lexicon updates

            if (cached && cacheVersion === currentVersion) {
                console.log('📖 Loading lexicon from cache');
                this.words = JSON.parse(cached);
                this.loaded = true;
                this.loading = false;
                return this.words;
            }

            // Download from network
            console.log('📥 Downloading lexicon...');
            const response = await fetch('words.json');

            if (!response.ok) {
                throw new Error(`Failed to load lexicon: ${response.status}`);
            }

            // Track download progress
            const contentLength = response.headers.get('content-length');
            const total = contentLength ? parseInt(contentLength) : 600000; // Approximate

            const reader = response.body.getReader();
            let received = 0;
            const chunks = [];

            while (true) {
                const { done, value } = await reader.read();

                if (done) break;

                chunks.push(value);
                received += value.length;

                if (onProgress) {
                    onProgress(received, total);
                }
            }

            // Combine chunks
            const blob = new Blob(chunks);
            const text = await blob.text();
            this.words = JSON.parse(text);

            // Cache it
            try {
                localStorage.setItem('lexicon_cache', text);
                localStorage.setItem('lexicon_version', currentVersion);
                console.log('💾 Lexicon cached');
            } catch (e) {
                console.warn('Failed to cache lexicon:', e);
            }

            this.loaded = true;
            this.loading = false;
            console.log(`✅ Loaded ${this.words.length} words`);
            return this.words;

        } catch (error) {
            this.loading = false;
            throw error;
        }
    }

    isLoaded() {
        return this.loaded;
    }
}

// Global lexicon loader instance
const lexiconLoader = new LexiconLoader();
