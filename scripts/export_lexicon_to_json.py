#!/usr/bin/env python3
"""
Export the Italian lexicon from SQLite to JSON for client-side use.
Outputs a simple JSON array of word strings.
"""

import sqlite3
import json
import os

def export_lexicon_to_json():
    # Paths
    home = os.path.expanduser("~")
    db_path = os.path.join(home, '.it_spelling_bee', 'lexicon.sqlite')
    output_path = os.path.join(os.path.dirname(__file__), '..', 'web', 'words.json')
    
    # Connect to SQLite
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all words
    cursor.execute("SELECT clean_form FROM words ORDER BY clean_form")
    words = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    
    # Write to JSON
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(words, f, ensure_ascii=False)
    
    # Stats
    file_size = os.path.getsize(output_path)
    print(f"✅ Exported {len(words):,} words to {output_path}")
    print(f"📦 File size: {file_size:,} bytes ({file_size / 1024:.1f} KB)")
    print(f"💡 Gzipped size will be ~{file_size / 1024 / 3:.1f} KB")

if __name__ == '__main__':
    export_lexicon_to_json()
