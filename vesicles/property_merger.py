import sqlite3
import pandas as pd
import hashlib
import json


from pathlib import Path

DB_FILE = "project.db"
EXCEL_FILE = "movies.xlsx"
CODE_VERSION = "v1.0-movies"


# ---------------------------
# Utility: hash computation
# ---------------------------
def compute_hash(data_dict):
    s = json.dumps(data_dict, sort_keys=True)
    return hashlib.sha256(s.encode()).hexdigest()


# ---------------------------
# 1. Initialize database
# ---------------------------
def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            label TEXT UNIQUE,
            properties_json TEXT,
            property_hash TEXT,
            last_run_hash TEXT,
            status TEXT
        )
        """)
    print("Database initialized.")

# ---------------------------
# 2. Add movie entries
# ---------------------------
def add_movie(path):
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("""
        INSERT OR IGNORE INTO movies
        (label, properties_json, property_hash, last_run_hash, status)
        VALUES (?, '{}', '', '', 'dirty')
        """, (str(path),))
    print(f"Added movie: {path}")

def export_to_excel():
    with sqlite3.connect(DB_FILE) as conn:
        df = pd.read_sql("SELECT * FROM movies", conn)

    # Expand JSON properties into columns
    props_df = df["properties_json"].apply(json.loads).apply(pd.Series)
    df = pd.concat([df.drop(columns=["properties_json"]), props_df], axis=1)

    df.to_excel(EXCEL_FILE, index=False)
    print("Exported.")

# ---------------------------
# 4. Import from Excel + detect changes
# ---------------------------
def import_from_excel():
    df = pd.read_excel(EXCEL_FILE)

    fixed_columns = {"id", "label"}

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()

        for _, row in df.iterrows():
            dir_id = row["id"]

            # Everything except fixed columns is a user property
            properties = {
                col: row[col]
                for col in df.columns
                if col not in fixed_columns
            }

            # Remove NaN → convert to None
            properties = {
                k: (None if pd.isna(v) else v)
                for k, v in properties.items()
            }

            # Include code version in hash
            hash_input = {
                "properties": properties,
                "code_version": CODE_VERSION
            }

            new_hash = compute_hash(hash_input)

            cursor.execute("SELECT property_hash FROM movies WHERE id=?", (dir_id,))
            old_hash = cursor.fetchone()[0]

            status = "dirty" if new_hash != old_hash else "clean"

            cursor.execute("""
                UPDATE movies
                SET properties_json=?,
                    property_hash=?,
                    status=?
                WHERE id=?
            """, (
                json.dumps(properties),
                new_hash,
                status,
                dir_id
            ))

        conn.commit()

    print("Import complete.")


# ---------------------------
# 5. Simulated run step
# ---------------------------
def run_dirty_movies():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT id, property_hash FROM movies WHERE status='dirty'")
        rows = cursor.fetchall()

        for dir_id, prop_hash in rows:
            print(f"Running movie {dir_id}...")

            # Simulate processing here

            cursor.execute("""
                UPDATE movies
                SET last_run_hash=?,
                    status='clean'
                WHERE id=?
            """, (prop_hash, dir_id))

        conn.commit()

    print("Run complete.")



def show_movies_df():
    with sqlite3.connect("project.db") as conn:
        df = pd.read_sql("SELECT * FROM movies", conn)

    # Expand JSON into columns
    props_df = df["properties_json"].apply(
        lambda x: json.loads(x) if x else {}
    ).apply(pd.Series)

    df = pd.concat([df.drop(columns=["properties_json"]), props_df], axis=1)

    print(df.to_string(index=False))

# ---------------------------
# Example workflow
# ---------------------------
if __name__ == "__main__":
    if 0:  #Danger zone_will overwrite your table!
        init_db()

        # Add some movies (only needed once)
        add_movie(r'File A')
        add_movie(r'File B')
        add_movie(r'File D')

        # Export editable Excel
        export_to_excel()

        print("Edit movies.xlsx, then re-run this script with:")
        print("import_from_excel()")
    else:  #regular use
        # update & close your Excel first
        import_from_excel()
        show_movies_df()