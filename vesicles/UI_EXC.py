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
            experiment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            experiment_path_in TEXT UNIQUE,
            experiment_path_out TEXT UNIQUE,
            experiment_use_it INTEGER,
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
        (
            experiment_path_in,
            experiment_path_out,
            experiment_use_it,
            remarks,
            property_hash,
            last_run_hash,
            status
        )
        VALUES (?, '', 1, '', '', '', 'dirty')
        """, (str(path),))
    print(f"Added directory: {path}")

# ---------------------------
# 3. Export to Excel
# ---------------------------
def export_to_excel():
    with sqlite3.connect(DB_FILE) as conn:
        df = pd.read_sql("SELECT experiment_path_in,experiment_path_out,experiment_use_it,remarks FROM directories", conn)

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
                SET use_this=?,,
                    remarks=?,
                    property_hash=?,
                    status=?
                WHERE id=?
            """, (
                int(row["use_this"]),
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
    add_directory(r'M:\tnw\bn\cd\Shared\Jacob\TESTdata_in\2025_Charu\pilots\20082025_CS_test')
    add_directory(r'M:\tnw\bn\cd\Shared\Jacob\TESTdata_in\2025_Charu\pilots\20082025_CS_test_00')
    add_directory(r'M:\tnw\bn\cd\Shared\Jacob\TESTdata_in\2025_Charu\pilots\20082025_CS_test_01')

    # Export editable Excel
    export_to_excel()

    print("Edit directories.xlsx, then re-run this script with:")
    print("import_from_excel()")
