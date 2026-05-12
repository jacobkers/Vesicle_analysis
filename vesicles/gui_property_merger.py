import sqlite3
import pandas as pd
import numpy as np
import hashlib
import json
from pathlib import Path
from datetime import datetime
import shutil
import os

from gui_process import expand_df

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
    #returns a row of column values except for the id column
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
            properties_json TEXT
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
    #TODO: here, somehow DB gets overwritten. We'd like to have the ones not used to be unconsidered
    df_to_DB(df)
    print("Import complete.")

def df_to_DB(df):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()

        for _, row in df.iterrows():
            movie_id = int(row["id"])
            #build col values in single json text
            props = build_properties(row, df.columns)
            props_json = json.dumps(props)

            cursor.execute("""
                SELECT *
                FROM movies
                WHERE id=?
            """, (movie_id,))
            result = cursor.fetchone()
            if result is None:  #movie_id does not yet exist
                print("insert!")
                cursor.execute("""
                    INSERT INTO movies
                    (id, properties_json)
                    VALUES (?, ?)
                """, (movie_id, props_json))
            else: #row exist, overwrite
                print("overwrite!")
                cursor.execute("""
                    UPDATE movies
                    SET properties_json=?
                    WHERE id=?
                """, (props_json, movie_id))
        conn.commit()


def ensure_columns_from_dataframe(conn, table_name, df):

    cursor = conn.cursor()

    existing = cursor.execute(f"""
        PRAGMA table_info({table_name})
    """).fetchall()
    existing_names = {col[1] for col in existing}
    for col in df.columns:
        if col not in existing_names:
            dtype = df[col].dtype

            # map pandas dtype -> SQLite type
            if pd.api.types.is_integer_dtype(dtype):
                sql_type = "INTEGER"
            elif pd.api.types.is_float_dtype(dtype):
                sql_type = "REAL"
            else:
                sql_type = "TEXT"
            print(f"Adding column: {col} ({sql_type})")

            cursor.execute(f"""
                ALTER TABLE {table_name}
                ADD COLUMN "{col}" {sql_type}
            """)

    conn.commit()

def process_movies():
    with sqlite3.connect(DB_FILE) as conn:

        df = pd.read_sql("SELECT * FROM movies", conn)


        #loooots of analysis here------------------
        df_to_use = expand_df(df)
        #currently, contains only 'use_it'=1 rows
        #-------------------------------------

        #define new columns made in dataframe df during processing
        #ensure_columns_from_dataframe(conn, "movies", df_to_use)
        df_to_DB(df_to_use)
        #then write to movies:
        # cursor = conn.cursor()
        # for _, row in df_to_use.iterrows():
        #     movie_id = row["id"]
        #     columns = [col for col in df_to_use.columns if col != "id"]
        #     set_clause = ", ".join([
        #         f'"{col}" = ?'
        #         for col in columns
        #     ])
        #     values = [row[col] for col in columns]
        #
        #     sql = f"""
        #         UPDATE movies
        #         SET {set_clause}
        #         WHERE id = ?
        #     """
        #
        #     cursor.execute(sql, values + [movie_id])
        #
        # conn.commit()

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
        init_db()
