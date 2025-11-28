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
            const cachedText = localStorage.getItem('lexicon_cache');
            const cachedKey = localStorage.getItem('lexicon_cache_key');

            // Download from network (CDN will never serve stale thanks to _headers)
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

            // Generate cache key from first 100 chars (acts as simple hash/fingerprint)
            const cacheKey = text.substring(0, 100);

            // If cache matches, use it; otherwise update cache
            if (cachedKey === cacheKey && cachedText) {
                console.log('📖 Using cached lexicon (content unchanged)');
                this.words = JSON.parse(cachedText);
            } else {
                console.log('💾 Caching new lexicon version');
                this.words = JSON.parse(text);
                try {
                    localStorage.setItem('lexicon_cache', text);
                    localStorage.setItem('lexicon_cache_key', cacheKey);
                } catch (e) {
                    console.warn('Failed to cache lexicon:', e);
                }
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
