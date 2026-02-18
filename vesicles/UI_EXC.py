import sqlite3
import pandas as pd
import hashlib
import json
from pathlib import Path

DB_FILE = "project.db"
EXCEL_FILE = "directories.xlsx"
CODE_VERSION = "v1.0-directories"


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
        CREATE TABLE IF NOT EXISTS directories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            path_in TEXT UNIQUE,
            path_out TEXT UNIQUE,
            use_this INTEGER,
            salt_concentration TEXT,
            remarks TEXT,
            property_hash TEXT,
            last_run_hash TEXT,
            status TEXT
        )
        """)
    print("Database initialized.")


# ---------------------------
# 2. Add directory entries
# ---------------------------
def add_directory(path):
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("""
        INSERT OR IGNORE INTO directories
        (path, use_this, salt_concentration, remarks, property_hash, last_run_hash, status)
        VALUES (?, 1, NULL, '', '', '', 'dirty')
        """, (str(path),))
    print(f"Added directory: {path}")


# ---------------------------
# 3. Export to Excel
# ---------------------------
def export_to_excel():
    with sqlite3.connect(DB_FILE) as conn:
        df = pd.read_sql("SELECT id, path, use_this, salt_concentration, remarks FROM directories", conn)

    df.to_excel(EXCEL_FILE, index=False)
    print(f"Exported to {EXCEL_FILE}")


# ---------------------------
# 4. Import from Excel + detect changes
# ---------------------------
def import_from_excel():
    df = pd.read_excel(EXCEL_FILE)

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()

        for _, row in df.iterrows():
            data_dict = {
                "use_this": int(row["use_this"]),
                "salt_concentration": row["salt_concentration"],
                "remarks": row["remarks"],
                "code_version": CODE_VERSION
            }

            new_hash = compute_hash(data_dict)

            cursor.execute("SELECT property_hash FROM directories WHERE id=?", (row["id"],))
            result = cursor.fetchone()

            old_hash = result[0] if result else None

            status = "dirty" if new_hash != old_hash else "clean"

            cursor.execute("""
                UPDATE directories
                SET use_this=?,
                    salt_concentration=?,
                    remarks=?,
                    property_hash=?,
                    status=?
                WHERE id=?
            """, (
                int(row["use_this"]),
                row["salt_concentration"],
                row["remarks"],
                new_hash,
                status,
                row["id"]
            ))

        conn.commit()

    print("Import complete. Change detection applied.")


# ---------------------------
# 5. Simulated run step
# ---------------------------
def run_dirty_directories():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT id, property_hash FROM directories WHERE status='dirty'")
        rows = cursor.fetchall()

        for dir_id, prop_hash in rows:
            print(f"Running directory {dir_id}...")

            # Simulate processing here

            cursor.execute("""
                UPDATE directories
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
    init_db()

    # Add some directories (only needed once)
    add_directory("data/experiment_1")
    add_directory("data/experiment_2")

    # Export editable Excel
    export_to_excel()

    print("Edit directories.xlsx, then re-run this script with:")
    print("import_from_excel()")
