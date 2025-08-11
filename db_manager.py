# db_manager.py
import sqlite3

class DBManager:
    def __init__(self, db_file="pipeline_monitor.db"):
        self.conn = sqlite3.connect(db_file)
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pipeline_retry (
                pipeline_name TEXT,
                original_run_id TEXT,
                retry_count INTEGER,
                last_attempt_run_id TEXT,
                status TEXT,
                PRIMARY KEY (pipeline_name, original_run_id)
            )
        """)
        self.conn.commit()

    def insert_run(self, pipeline_name, original_run_id, retry_count=2):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR IGNORE INTO pipeline_retry
            (pipeline_name, original_run_id, retry_count, last_attempt_run_id, status)
            VALUES (?, ?, ?, NULL, 'pending')
        """, (pipeline_name, original_run_id, retry_count))
        self.conn.commit()

    def get_run_info(self, pipeline_name, original_run_id):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT retry_count, last_attempt_run_id, status
            FROM pipeline_retry
            WHERE pipeline_name = ? AND original_run_id = ?
        """, (pipeline_name, original_run_id))
        row = cursor.fetchone()
        return {"retry_count": row[0], "last_attempt_run_id": row[1], "status": row[2]} if row else None

    def update_retry(self, pipeline_name, original_run_id, retry_count=None, last_attempt_run_id=None, status=None):
        cursor = self.conn.cursor()
        fields, params = [], []
        if retry_count is not None:
            fields.append("retry_count = ?")
            params.append(retry_count)
        if last_attempt_run_id is not None:
            fields.append("last_attempt_run_id = ?")
            params.append(last_attempt_run_id)
        if status is not None:
            fields.append("status = ?")
            params.append(status)
        params += [pipeline_name, original_run_id]
        cursor.execute(f"""
            UPDATE pipeline_retry
            SET {", ".join(fields)}
            WHERE pipeline_name = ? AND original_run_id = ?
        """, params)
        self.conn.commit()

    def delete_run(self, pipeline_name, original_run_id):
        cursor = self.conn.cursor()
        cursor.execute("""
            DELETE FROM pipeline_retry
            WHERE pipeline_name = ? AND original_run_id = ?
        """, (pipeline_name, original_run_id))
        self.conn.commit()
