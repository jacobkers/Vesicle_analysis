import sqlite3
import pandas as pd
import numpy as np
import hashlib
import json
from pathlib import Path
from datetime import datetime
import shutil
import os

#set paths and files here
PATH_IN =str("C:/Users/jkerssemakers/OneDrive - Delft University of Technology/CD_recent/BN_CD24_Bert/Joss paper/example_data_set/")
MOVIES_IN = os.path.join(PATH_IN, "data_overview.xlsx")
VESICLES_OUT = os.path.join(PATH_IN, "vesicles_out.xlsx")
DB_FILE = os.path.join(PATH_IN, "project.db")
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

def timestamp():
    return datetime.now().strftime("%y%m%d%H")

def init_db():
    #needs to be done only once: build first contents of database
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("""
        CREATE TABLE movies (
            id INTEGER PRIMARY KEY,
            properties_json TEXT,
            object_count INTEGER
        )
        """)
    print("Database initialized.")

def add_movie(experiment_label):
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("""
        INSERT OR IGNORE INTO movies
        (experiment_label, properties_json, property_hash, last_run_hash, status)
        VALUES (?, '{}', '', '', 'dirty')
        """, (str(experiment_label),))
    print(f"Added movie: {experiment_label}")

def backup_file(filepath):
    path = Path(filepath)
    if path.exists():
        backup_name = f"{path.stem}_backup_{timestamp()}{path.suffix}"
        backup_path = path.parent / backup_name   # <-- same directory

        shutil.copy(path, backup_path)            # <-- copy the file
        print(f"Backup created: {backup_path}")

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


def import_excel():
    #pass a path here
    df = pd.read_excel(MOVIES_IN)

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()

        for _, row in df.iterrows():

            movie_id = int(row["id"])

            props = build_properties(row, df.columns)
            props_json = json.dumps(props)

            cursor.execute("""
                SELECT *
                FROM movies
                WHERE id=?
            """, (movie_id,))

            result = cursor.fetchone()

            if result is None:

                cursor.execute("""
                    INSERT INTO movies
                    (id, properties_json)
                    VALUES (?, ?)
                """, (movie_id, props_json))

            else:

                cursor.execute("""
                    UPDATE movies
                    SET properties_json=?
                    WHERE id=?
                """, (props_json, movie_id))

        conn.commit()
    print("Import complete.")

def process_movies():

    with sqlite3.connect(DB_FILE) as conn:
        df = pd.read_sql("SELECT * FROM movies", conn)
        cursor = conn.cursor()

        for _, row in df.iterrows():

            props = json.loads(row["properties_json"])
            movie_id = row["id"]
            print("Processing", movie_id)
            object_count = len(props)  # placeholder

            cursor.execute("""
                            SELECT *
                            FROM movies
                            WHERE id=?
                        """, (movie_id,))

        conn.commit()

    print("Processing done.")

def show_movies_df():
    with sqlite3.connect(DB_FILE) as conn:
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
        dum=0
        init_db()

    else:  #regular use
        # update & close your Excel first
        #export_to_excel()
        show_movies_df()
