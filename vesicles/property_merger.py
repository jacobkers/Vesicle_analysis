import sqlite3
import pandas as pd
import numpy as np
import hashlib
import json
from pathlib import Path
from datetime import datetime
import shutil


DB_FILE = "project.db"
MOVIES_IN = "movies_in.xlsx"
VESICLES_OUT = "vesicles_out.xlsx"
CODE_VERSION = "v1.0-movies"


def canonicalize_value(v):
    if pd.isna(v):
        return None

    # convert numpy scalars to python
    if isinstance(v, np.generic):
        return v.item()

    # convert timestamps
    if isinstance(v, pd.Timestamp):
        return v.isoformat()

    return v

def build_properties(row, columns):
    return {
        col: canonicalize_value(row[col])
        for col in columns
        if col != "id"
    }

def compute_hash(data_dict):
    s = json.dumps(
        data_dict,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False
    )
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def timestamp():
    return datetime.now().strftime("%y%m%d%H")

#Backup function
def backup_file(filepath):
    #Save a date-stamped copy from work files
    path = Path(filepath)
    if path.exists():
        backup_name = f"{path.stem}_backup_{timestamp()}{path.suffix}"
        shutil.copy(path, backup_name)
        print(f"Backup created: {backup_name}")

# ---------------------------
# 1. Initialize database
# ---------------------------
def init_db():
    #needs to be done only once: build first contents of database
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY,
            properties_json TEXT,
            property_hash TEXT,
            last_run_hash TEXT,
            status TEXT,
            object_count INTEGER
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
    backup_file(VESICLES_OUT)

    with sqlite3.connect(DB_FILE) as conn:
        df = pd.read_sql("SELECT * FROM movies", conn)

    # Expand properties JSON
    props_df = df["properties_json"].apply(
        lambda x: json.loads(x) if x else {}
    ).apply(pd.Series)

    df_out = pd.concat(
        [df.drop(columns=["properties_json", "property_hash", "last_run_hash", "status"]),
         props_df],
        axis=1
    )

    df_out.to_excel(VESICLES_OUT, index=False)
    print("Export complete.")

# ---------------------------
# 4. Import from Excel + detect changes
# ---------------------------
def import_from_excel(rerun_all=False):
    backup_file(MOVIES_IN)

    df = pd.read_excel(MOVIES_IN)

    if "id" not in df.columns:
        raise ValueError("movies_in.xlsx must contain an 'id' column.")

    fixed_columns = {"id"}

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()

        # Get current DB IDs
        cursor.execute("SELECT id FROM movies")
        db_ids = {row[0] for row in cursor.fetchall()}

        excel_ids = set(df["id"])

        # Delete removed IDs
        ids_to_delete = db_ids - excel_ids
        for del_id in ids_to_delete:
            cursor.execute("DELETE FROM movies WHERE id=?", (del_id,))
            print(f"Deleted ID {del_id} from DB")

        for _, row in df.iterrows():
            movie_id = int(row["id"])

            properties = build_properties(row, df.columns)

            hash_input = {
                "properties": properties,
                "code_version": CODE_VERSION
            }

            new_hash = compute_hash(hash_input)

            cursor.execute("SELECT property_hash FROM movies WHERE id=?", (movie_id,))
            result = cursor.fetchone()

            if result is None:
                # Insert new
                cursor.execute("""
                    INSERT INTO movies
                    (id, properties_json, property_hash, last_run_hash, status, object_count)
                    VALUES (?, ?, ?, NULL, 'dirty', NULL)
                """, (movie_id, json.dumps(properties), new_hash))
                continue

            old_hash = result[0]

            status = "dirty" if (new_hash != old_hash or rerun_all) else "clean"

            cursor.execute("""
                UPDATE movies
                SET properties_json=?,
                    property_hash=?,
                    status=?
                WHERE id=?
            """, (json.dumps(properties), new_hash, status, movie_id))

        conn.commit()

    print("Import complete.")


def any_dirty():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT 1 FROM movies WHERE status='dirty' LIMIT 1"
        )
        return cursor.fetchone() is not None

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

def process_movies():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT id, properties_json, property_hash FROM movies WHERE status='dirty'")
        rows = cursor.fetchall()

        for movie_id, props_json, prop_hash in rows:
            props = json.loads(props_json)

            print(f"Processing movie {movie_id}")

            # --- PLACEHOLDER PROCESSING ---
            object_count = len(props)  # dummy example
            # --------------------------------

            cursor.execute("""
                UPDATE movies
                SET object_count=?,
                    last_run_hash=?,
                    status='clean'
                WHERE id=?
            """, (object_count, prop_hash, movie_id))

        conn.commit()

    print("Processing done.")

def show_movies_df():
    with sqlite3.connect("project.db") as conn:
        df = pd.read_sql("SELECT * FROM movies", conn)

    # Expand JSON into columns
    props_df = df["properties_json"].apply(
        lambda x: json.loads(x) if x else {}
    ).apply(pd.Series)

    df = pd.concat([df.drop(columns=["properties_json"]), props_df], axis=1)

    print(df.to_string(index=False))

def preview_excel_changes():
    df = pd.read_excel(MOVIES_IN)

    with sqlite3.connect(DB_FILE) as conn:
        db_df = pd.read_sql("SELECT id, property_hash FROM movies", conn)

    db_ids = set(db_df["id"])
    excel_ids = set(df["id"])
    new_ids = excel_ids - db_ids
    deleted_ids = db_ids - excel_ids
    changed_ids = []

    for _, row in df.iterrows():
        movie_id = row["id"]

        if movie_id not in db_ids: #new entry: skip following
            continue

        properties = build_properties(row, df.columns)

        new_hash = compute_hash({
            "properties": properties,
            "code_version": CODE_VERSION
        })

        old_hash = db_df.loc[db_df["id"] == movie_id, "properties_json"].iloc[0]

        if new_hash != old_hash:
            changed_ids.append(movie_id)

    return {
        "new": new_ids,
        "deleted": deleted_ids,
        "changed": changed_ids
    }


# ---------------------------
# Example workflow
# ---------------------------
if __name__ == "__main__":
    if 1:  #Danger zone_will overwrite your table!
        dum=1
        #init_db()

    else:  #regular use
        # update & close your Excel first
        #export_to_excel()
        import_from_excel_in()
        run_dirty_movies()
        export_to_excel_out()
        show_movies_df()
