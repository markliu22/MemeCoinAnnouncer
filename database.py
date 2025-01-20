import sqlite3
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Subscriber:
    id: Optional[int]
    email: Optional[str]
    phone: Optional[str]
    is_active: bool = True

class Database:
    def __init__(self, db_path="subscribers.db"):
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def init_db(self):
        with self.get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS subscribers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE,
                    phone TEXT UNIQUE,
                    is_active BOOLEAN DEFAULT 1
                )
            """)
            conn.commit()

    def add_subscriber(self, email: str = None, phone: str = None) -> bool:
        if not email and not phone:
            return False
            
        try:
            with self.get_connection() as conn:
                # First try to reactivate existing subscriber (subscribe, unsubscribe, then subscribe again case)
                if email:
                    conn.execute(
                        "UPDATE subscribers SET is_active = 1 WHERE email = ?",
                        (email,)
                    )
                if phone:
                    conn.execute(
                        "UPDATE subscribers SET is_active = 1 WHERE phone = ?",
                        (phone,)
                    )
                
                # If no rows were updated, insert new subscriber
                if conn.total_changes == 0:
                    conn.execute(
                        "INSERT INTO subscribers (email, phone) VALUES (?, ?)",
                        (email, phone)
                    )
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False

    def get_all_active_subscribers(self) -> List[Subscriber]:
        with self.get_connection() as conn:
            cursor = conn.execute(
                "SELECT id, email, phone, is_active FROM subscribers WHERE is_active = 1"
            )
            return [Subscriber(*row) for row in cursor.fetchall()]

    def deactivate_subscriber(self, email: str = None, phone: str = None) -> bool:
        if not email and not phone:
            return False

        with self.get_connection() as conn:
            if email:
                conn.execute(
                    "UPDATE subscribers SET is_active = 0 WHERE email = ?",
                    (email,)
                )
            if phone:
                conn.execute(
                    "UPDATE subscribers SET is_active = 0 WHERE phone = ?",
                    (phone,)
                )
            conn.commit()
            return True 