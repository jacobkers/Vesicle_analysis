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


def canonical_value(v):
    import numpy as np
    import pandas as pd

    if pd.isna(v):
        return None
    if isinstance(v, np.generic):
        return v.item()
    if isinstance(v, pd.Timestamp):
        return v.isoformat()

    return v


def build_properties(row, columns):
    return {
        col: canonical_value(row[col])
        for col in columns
        if col != "id"
    }

def compute_hash(properties):

    payload = {
        "properties": properties,
        "code_version": CODE_VERSION
    }

    s = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(s.encode()).hexdigest()


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
        CREATE TABLE movies (
            id INTEGER PRIMARY KEY,
            properties_json TEXT,
            last_hash TEXT,
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
        [df.drop(columns=["properties_json"]),
         props_df],
        axis=1
    )

    df_out.to_excel(VESICLES_OUT, index=False)
    print("Export complete.")

# ---------------------------
# 4. Import from Excel + detect changes
# ---------------------------
def import_excel():

    df = pd.read_excel(MOVIES_IN)

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()

        for _, row in df.iterrows():

            movie_id = int(row["id"])

            props = build_properties(row, df.columns)
            props_json = json.dumps(props)
            current_hash = compute_hash(props)

            cursor.execute("""
                SELECT last_hash
                FROM movies
                WHERE id=?
            """, (movie_id,))

            result = cursor.fetchone()

            if result is None:

                cursor.execute("""
                    INSERT INTO movies
                    (id, properties_json, last_hash)
                    VALUES (?, ?, NULL)
                """, (movie_id, props_json))

            else:

                cursor.execute("""
                    UPDATE movies
                    SET properties_json=?
                    WHERE id=?
                """, (props_json, movie_id))

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

def process_movies():

    with sqlite3.connect(DB_FILE) as conn:

        df = pd.read_sql("SELECT * FROM movies", conn)

        cursor = conn.cursor()

        for _, row in df.iterrows():

            props = json.loads(row["properties_json"])
            current_hash = compute_hash(props)

            if current_hash == row["last_hash"]:
                continue

            movie_id = row["id"]

            print("Processing", movie_id)

            object_count = len(props)  # placeholder

            cursor.execute("""
                UPDATE movies
                SET object_count=?,
                    last_hash=?
                WHERE id=?
            """, (object_count, current_hash, movie_id))

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

def excel_changed(excel_file=MOVIES_IN, stored_hash=None):

    df = pd.read_excel(excel_file)

    # normalize dataframe
    df = df.where(pd.notna(df), None)

    # convert to deterministic structure
    data = {
        "columns": list(df.columns),
        "rows": df.to_dict(orient="records")
    }

    s = json.dumps(data, sort_keys=True, separators=(",", ":"))
    new_hash = hashlib.sha256(s.encode()).hexdigest()

    if stored_hash is None:
        return new_hash, False

    return new_hash, (new_hash != stored_hash)

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
