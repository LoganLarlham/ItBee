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
            const cachedText = localStorage.getItem('lexicon_data');
            const cachedFingerprint = localStorage.getItem('lexicon_fp');

            // Download from network with force-cache to use Cloudflare edge cache
            // The Cloudflare Cache Rule ensures edge TTL=120s, browser TTL=0s
            console.log('📥 Downloading lexicon...');
            const response = await fetch('words.json', { cache: 'force-cache' });

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

            // Generate SHA-256 fingerprint using Web Crypto API
            const encoder = new TextEncoder();
            const data = encoder.encode(text);
            const hashBuffer = await crypto.subtle.digest('SHA-256', data);
            const hashArray = Array.from(new Uint8Array(hashBuffer));
            // Convert to 16-character hex string (first 64 bits)
            const fingerprint = hashArray.slice(0, 8).map(b => b.toString(16).padStart(2, '0')).join('');

            // If cache matches, use it; otherwise update cache
            if (cachedFingerprint === fingerprint && cachedText) {
                console.log('📖 Using cached lexicon (content unchanged)');
                this.words = JSON.parse(cachedText);
            } else {
                console.log('💾 Caching new lexicon version');
                this.words = JSON.parse(text);
                try {
                    localStorage.setItem('lexicon_data', text);
                    localStorage.setItem('lexicon_fp', fingerprint);
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
