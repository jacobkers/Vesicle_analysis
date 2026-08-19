import sqlite3
import pandas as pd
import os
import json
from pathlib import Path
from datetime import datetime
import shutil
from gui_process import expand_df

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

def init_db(db_file):
    #needs to be done only once: build first contents of database
    with sqlite3.connect(db_file) as conn:
        conn.execute("""
        CREATE TABLE movies (
            id INTEGER PRIMARY KEY,
            properties_json TEXT
        )
        """)
    print("Database initialized.")

# def add_movie(experiment_label,db_file):
#     with sqlite3.connect(db_file) as conn:
#         conn.execute("""
#         INSERT OR IGNORE INTO movies
#         (experiment_label, properties_json, property_hash, last_run_hash, status)
#         VALUES (?, '{}', '', '', 'dirty')
#         """, (str(experiment_label),))
#     print(f"Added movie: {experiment_label}")

def backup_file(filepath):
    path = Path(filepath)
    if path.exists():
        backup_name = f"{path.stem}_backup_{timestamp()}{path.suffix}"
        backup_path = path.parent / backup_name   # <-- same directory

        shutil.copy(path, backup_path)            # <-- copy the file
        print(f"Backup created: {backup_path}")

def export_to_excel(db_file, vesicles_out, export_option="all"):
    backup_file(vesicles_out)
    with sqlite3.connect(db_file) as conn:
        df = pd.read_sql("SELECT * FROM movies", conn)
    df_out=unpack_json_in_df(df)
    if export_option=="selection":
        df_out=df_out[df_out['use_it'] == 1]

    df_out.to_excel(vesicles_out, index=False)
    print("Export complete.")


def import_excel(db_file,movies_in):
    #pass a path here
    df = pd.read_excel(movies_in)
    df_to_use = df[df['use_it'] == 1]
    df_to_DB(db_file,df_to_use)
    print("Import complete.")

def df_to_DB(db_file,df):
    #write a flat dataframe (i.e., no json blobs inside) to a DB
    #reset all 'use_it' to zero first - in the DB


    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()

        cursor.execute("""
                UPDATE movies
                SET properties_json =
                    json_set(properties_json, '$.use_it', 0)
            """)


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
                print("inserted:" + str(movie_id))
                cursor.execute("""
                    INSERT INTO movies
                    (id, properties_json)
                    VALUES (?, ?)
                """, (movie_id, props_json))
            else: #row exist, overwrite
                print("overwritten:" + str(movie_id))
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

def unpack_json_in_df(df_in):
    # Expand JSON into columns
    props_df = df_in["properties_json"].apply(
        lambda x: json.loads(x) if x else {}
    ).apply(pd.Series)
    df_out = pd.concat([df_in.drop(columns=["properties_json"]), props_df], axis=1)
    return df_out

def process_movies(db_file, pic_format):
    with sqlite3.connect(db_file) as conn:
        df = pd.read_sql("SELECT * FROM movies", conn)
        #loooots of analysis here, handle only 'use_it' rows:
        df_to_use = expand_df(df,pic_format = pic_format)
        df_to_DB(db_file,df_to_use)
    print("Processing done.")

def show_movies_df(db_file):
    with sqlite3.connect(db_file) as conn:
        df = pd.read_sql("SELECT * FROM movies", conn)
    df_out=unpack_json_in_df(df)
    print(df_out.to_string(index=False))

#for initialization DB:
if __name__ == "__main__":
    if 0:  #Danger zone: this will overwrite your Database file!
        # For safety, switch to 'if 0' after run.
        MyPath=r'C:\Users\jkerssemakers\OneDrive - Delft University of Technology\CD_recent\BN_CD24_Bert\Joss paper\example_data_set'
        db_file = os.path.join(MyPath,'project.db')
        init_db(db_file)
