import sqlite3
import sys
from pathlib import Path

def export_to_d1_sql(db_path: Path, out_path: Path):
    if not db_path.exists():
        print(f"Error: {db_path} not found")
        return

    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    
    print(f"Reading from {db_path}...")
    
    with out_path.open("w", encoding="utf-8") as f:
        f.write("DROP TABLE IF EXISTS words;\n")
        f.write("CREATE TABLE words(clean_form TEXT PRIMARY KEY, zipf REAL, mask INTEGER);\n")
        f.write("CREATE INDEX idx_mask ON words(mask);\n")
        
        count = 0
        # Only export words that are reasonably common to save space?
        # Or export all? Let's export all for now, D1 limits are generous enough (500MB).
        for row in cur.execute("SELECT clean_form, zipf, mask FROM words"):
            clean_form = row[0]
            zipf = row[1]
            mask = row[2]
            
            # Escape single quotes
            clean_form_esc = clean_form.replace("'", "''")
            
            f.write(f"INSERT INTO words(clean_form, zipf, mask) VALUES ('{clean_form_esc}', {zipf}, {mask});\n")
            count += 1
            
    print(f"Exported {count} words to {out_path}")

if __name__ == "__main__":
    # Default paths
    home = Path.home()
    db_path = home / ".it_spelling_bee" / "lexicon.sqlite"
    out_path = Path("lexicon_d1.sql")
    
    export_to_d1_sql(db_path, out_path)
