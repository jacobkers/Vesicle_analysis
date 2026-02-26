import sqlite3
import pandas as pd
import hashlib
import json


from pathlib import Path

DB_FILE = "project.db"
EXCEL_IN_FILE = "movies_in.xlsx"
EXCEL_OUT_FILE = "movies_out.xlsx"
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
            experiment_label TEXT UNIQUE,
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
def add_movie(experiment_label):
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("""
        INSERT OR IGNORE INTO movies
        (experiment_label, properties_json, property_hash, last_run_hash, status)
        VALUES (?, '{}', '', '', 'dirty')
        """, (str(experiment_label),))
    print(f"Added movie: {experiment_label}")

def export_to_excel():
    with sqlite3.connect(DB_FILE) as conn:
        df = pd.read_sql("SELECT id, experiment_label, properties_json FROM movies", conn)

    # Expand JSON properties into columns
    props_df = df["properties_json"].apply(
        lambda x: json.loads(x) if x else {}
    ).apply(pd.Series)

    df = pd.concat([df.drop(columns=["properties_json"]), props_df], axis=1)

    df.to_excel(EXCEL_OUT_FILE, index=False)
    print("Exported clean Excel (no hash columns).")

# ---------------------------
# 4. Import from Excel + detect changes
# ---------------------------
def import_from_excel():
    df = pd.read_excel(EXCEL_IN_FILE)

    fixed_columns = {"id", "experiment_label"}

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()

        for _, row in df.iterrows():

            dir_id = row.get("id", None)

            # Extract user properties
            properties = {
                col: (None if pd.isna(row[col]) else row[col])
                for col in df.columns
                if col not in fixed_columns
            }

            hash_input = {
                "properties": properties,
                "code_version": CODE_VERSION
            }

            new_hash = compute_hash(hash_input)

            # -----------------------
            # CASE 1: New row (no id)
            # -----------------------
            if pd.isna(dir_id):
                cursor.execute("""
                    INSERT INTO movies
                    (experiment_label, properties_json, property_hash, last_run_hash, status)
                    VALUES (?, ?, ?, NULL, 'dirty')
                """, (
                    row["experiment_label"],
                    json.dumps(properties),
                    new_hash
                ))
                continue

            # -----------------------
            # CASE 2: Existing row
            # -----------------------
            cursor.execute("SELECT property_hash FROM movies WHERE id=?", (int(dir_id),))
            result = cursor.fetchone()

            if result is None:
                print(f"Warning: ID {dir_id} not found. Skipping.")
                continue

            old_hash = result[0]
            status = "dirty" if new_hash != old_hash else "clean"

            cursor.execute("""
                UPDATE movies
                SET experiment_label=?,
                    properties_json=?,
                    property_hash=?,
                    status=?
                WHERE id=?
            """, (
                row["experiment_label"],
                json.dumps(properties),
                new_hash,
                status,
                int(dir_id)
            ))

        conn.commit()

    print("Excel import complete.")


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
    # 5. Simulated run step
    # ---------------------------
def run_dirty_movies():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT id, property_hash FROM movies WHERE status='dirty'")
        rows = cursor.fetchall()

        for dir_id, prop_hash in rows:
            print(f"Running movies {dir_id}...")

            # Simulate processing here

            cursor.execute("""
                UPDATE movies
                SET last_run_hash=?,
                    status='clean'
                WHERE id=?
            """, (prop_hash, dir_id))

        conn.commit()

    print("Run complete.")


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
        #export_to_excel()
        import_from_excel()
        run_dirty_movies()
        export_to_excel()
        show_movies_df()
