from typing import Dict, Any
import sqlite3
import json
import uuid
from datetime import datetime

class SharedMemory:
    def __init__(self, db_path: str = "flowbit.db"):
        self.conn = sqlite3.connect(db_path)
        self.create_tables()
    
    def create_tables(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS inputs (
                input_id TEXT PRIMARY KEY,
                input_text TEXT,
                timestamp TEXT,
                input_type TEXT,
                metadata JSON
            )
        """)
        
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS classifications (
                input_id TEXT PRIMARY KEY,
                format TEXT,
                intent TEXT,
                reasoning TEXT,
                timestamp TEXT,
                FOREIGN KEY (input_id) REFERENCES inputs(input_id)
            )
        """)
        
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS results (
                input_id TEXT PRIMARY KEY,
                result_data JSON,
                timestamp TEXT,
                FOREIGN KEY (input_id) REFERENCES inputs(input_id)
            )
        """)
        self.conn.commit()
    
    def store_input(self, input_id: str, input_text: str, input_type: str = None) -> None:
        self.conn.execute(
            "INSERT INTO inputs (input_id, input_text, timestamp, input_type) VALUES (?, ?, ?, ?)",
            (input_id, input_text, datetime.now().isoformat(), input_type)
        )
        self.conn.commit()
    
    def store_classification(self, input_id: str, classification: Dict[str, Any]) -> None:
        self.conn.execute(
            "INSERT INTO classifications (input_id, format, intent, reasoning, timestamp) VALUES (?, ?, ?, ?, ?)",
            (input_id, classification.get('classified_format'), classification.get('classified_intent'),
             classification.get('reasoning'), datetime.now().isoformat())
        )
        self.conn.commit()
    
    def store_result(self, input_id: str, result: Dict[str, Any]) -> None:
        self.conn.execute(
            "INSERT INTO results (input_id, result_data, timestamp) VALUES (?, ?, ?)",
            (input_id, json.dumps(result), datetime.now().isoformat())
        )
        self.conn.commit()