"""
Общая база данных для всех трёх проектов
"""
import sqlite3
import asyncio
from datetime import datetime
from typing import Optional, List, Dict

class Database:
    def __init__(self, db_path: str = "empire.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Инициализация всех таблиц"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Таблица пользователей (общая для всех проектов)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                referrer_id INTEGER,
                total_spent REAL DEFAULT 0
            )
        ''')
        
        # Проект 1: Анонимные признания
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS confession_boxes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                box_code TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                messages_count INTEGER DEFAULT 0,
                is_vip BOOLEAN DEFAULT 0,
                vip_until TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS confessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                box_id INTEGER,
                sender_id INTEGER,
                message TEXT,
                is_read BOOLEAN DEFAULT 0,
                reveal_sender BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (box_id) REFERENCES confession_boxes(id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS confession_payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                amount REAL,
                type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # Проект 2: Таро и астрология
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tarot_readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                reading_type TEXT,
                question TEXT,
                result TEXT,
                paid BOOLEAN DEFAULT 0,
                amount REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tarot_subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                subscription_type TEXT,
                valid_until TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # Проект 3: Мемы на заказ
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS meme_orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                description TEXT,
                meme_url TEXT,
                paid BOOLEAN DEFAULT 0,
                amount REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS meme_subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                valid_until TIMESTAMP,
                memes_created INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # Общая таблица статистики
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE UNIQUE,
                project TEXT,
                new_users INTEGER DEFAULT 0,
                revenue REAL DEFAULT 0,
                transactions INTEGER DEFAULT 0
            )
        ''')
        
        # Таблица реферальной программы
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS referrals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                referrer_id INTEGER,
                referred_id INTEGER,
                project TEXT,
                reward_given BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (referrer_id) REFERENCES users(user_id),
                FOREIGN KEY (referred_id) REFERENCES users(user_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_user(self, user_id: int, username: str = None, first_name: str = None, referrer_id: int = None):
        """Добавить нового пользователя"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO users (user_id, username, first_name, referrer_id)
                VALUES (?, ?, ?, ?)
            ''', (user_id, username, first_name, referrer_id))
            conn.commit()
        finally:
            conn.close()
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        """Получить информацию о пользователе"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
            row = cursor.fetchone()
            if row:
                return {
                    'user_id': row[0],
                    'username': row[1],
                    'first_name': row[2],
                    'created_at': row[3],
                    'referrer_id': row[4],
                    'total_spent': row[5]
                }
        finally:
            conn.close()
        return None
    
    def update_revenue(self, project: str, amount: float):
        """Обновить статистику дохода"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            today = datetime.now().date()
            cursor.execute('''
                INSERT INTO daily_stats (date, project, revenue, transactions)
                VALUES (?, ?, ?, 1)
                ON CONFLICT(date) DO UPDATE SET
                    revenue = revenue + ?,
                    transactions = transactions + 1
            ''', (today, project, amount, amount))
            conn.commit()
        finally:
            conn.close()
    
    def get_total_revenue(self) -> float:
        """Получить общий доход по всем проектам"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT SUM(revenue) FROM daily_stats')
            result = cursor.fetchone()[0]
            return result if result else 0.0
        finally:
            conn.close()
    
    def get_project_stats(self, project: str) -> Dict:
        """Получить статистику по проекту"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT 
                    SUM(revenue) as total_revenue,
                    SUM(transactions) as total_transactions,
                    SUM(new_users) as total_users
                FROM daily_stats
                WHERE project = ?
            ''', (project,))
            row = cursor.fetchone()
            return {
                'revenue': row[0] if row[0] else 0,
                'transactions': row[1] if row[1] else 0,
                'users': row[2] if row[2] else 0
            }
        finally:
            conn.close()

# Глобальный экземпляр базы данных
db = Database()

