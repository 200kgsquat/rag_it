import sqlite3
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any
from pathlib import Path
from src.qabot.repository.models import LogRecord

from config import config

class LogRepository:
    def __init__(self, db_path: Path = config.logs_dir / "logs.db"):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                session_id TEXT NOT NULL,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                top_doc_paths TEXT NOT NULL,
                answer_length INTEGER NOT NULL,
                retrieve_ms INTEGER NOT NULL,
                llm_ms INTEGER NOT NULL,
                total_ms INTEGER NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

    def create(self, record: LogRecord) -> int:
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO logs (timestamp, session_id, question, answer, top_doc_paths, answer_length, retrieve_ms, llm_ms, total_ms)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            record.timestamp.isoformat(),
            record.session_id,
            record.question,
            record.answer,
            json.dumps(record.top_doc_paths),
            record.answer_length,
            record.retrieve_ms,
            record.llm_ms,
            record.total_ms
        ))
        record_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return record_id

    def get_by_session(self, session_id: str) -> List[LogRecord]:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        rows = cursor.execute('SELECT * FROM logs WHERE session_id = ?', (session_id,)).fetchall()
        conn.close()
        return [self._row_to_record(row) for row in rows]

    def get_by_time_range(self, start: datetime, end: datetime) -> List[LogRecord]:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        rows = cursor.execute('SELECT * FROM logs WHERE timestamp BETWEEN ? AND ?',
                              (start.isoformat(), end.isoformat())).fetchall()
        conn.close()
        return [self._row_to_record(row) for row in rows]

    def _row_to_record(self, row: sqlite3.Row) -> LogRecord:
        return LogRecord(
            id=row['id'],
            timestamp=datetime.fromisoformat(row['timestamp']),
            session_id=row['session_id'],
            question=row['question'],
            answer=row['answer'],
            top_doc_paths=json.loads(row['top_doc_paths']),
            answer_length=row['answer_length'],
            retrieve_ms=row['retrieve_ms'],
            llm_ms=row['llm_ms'],
            total_ms=row['total_ms']
        )

    def get_time_stats(self) -> Dict[str, Any]:
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        stats = cursor.execute('''
            SELECT
                AVG(retrieve_ms) as avg_retrieve,
                MIN(retrieve_ms) as min_retrieve,
                MAX(retrieve_ms) as max_retrieve,
                AVG(llm_ms) as avg_llm,
                MIN(llm_ms) as min_llm,
                MAX(llm_ms) as max_llm,
                AVG(total_ms) as avg_total,
                MIN(total_ms) as min_total,
                MAX(total_ms) as max_total
            FROM logs
        ''').fetchone()
        conn.close()
        return {
            "retrieve_ms": {"avg": stats[0], "min": stats[1], "max": stats[2]},
            "llm_ms": {"avg": stats[3], "min": stats[4], "max": stats[5]},
            "total_ms": {"avg": stats[6], "min": stats[7], "max": stats[8]},
        }
