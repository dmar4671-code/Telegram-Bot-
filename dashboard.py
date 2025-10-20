"""
Веб-дашборд для мониторинга всех 3 проектов
Доступен с телефона через браузер
"""
from flask import Flask, render_template_string
import sqlite3
from datetime import datetime, timedelta
import sys
sys.path.append('/home/ubuntu/triple-telegram-empire')
from shared.database.db import db

app = Flask(__name__)

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📊 Triple Empire Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .total-revenue {
            background: rgba(255, 255, 255, 0.2);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
            text-align: center;
            color: white;
        }
        
        .total-revenue h2 {
            font-size: 1.2em;
            margin-bottom: 10px;
            opacity: 0.9;
        }
        
        .total-revenue .amount {
            font-size: 3em;
            font-weight: bold;
        }
        
        .goal-progress {
            margin-top: 20px;
        }
        
        .progress-bar {
            background: rgba(255, 255, 255, 0.3);
            border-radius: 10px;
            height: 20px;
            overflow: hidden;
        }
        
        .progress-fill {
            background: linear-gradient(90deg, #4CAF50, #8BC34A);
            height: 100%;
            transition: width 0.3s ease;
        }
        
        .projects {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .project-card {
            background: white;
            border-radius: 20px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        }
        
        .project-card h3 {
            font-size: 1.5em;
            margin-bottom: 20px;
            color: #333;
        }
        
        .stat {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px 0;
            border-bottom: 1px solid #eee;
        }
        
        .stat:last-child {
            border-bottom: none;
        }
        
        .stat-label {
            color: #666;
            font-size: 0.9em;
        }
        
        .stat-value {
            font-size: 1.3em;
            font-weight: bold;
            color: #333;
        }
        
        .emoji {
            font-size: 2em;
            margin-bottom: 10px;
        }
        
        .refresh-btn {
            position: fixed;
            bottom: 30px;
            right: 30px;
            background: white;
            color: #667eea;
            border: none;
            border-radius: 50%;
            width: 60px;
            height: 60px;
            font-size: 1.5em;
            cursor: pointer;
            box-shadow: 0 5px 20px rgba(0, 0, 0, 0.3);
            transition: transform 0.2s;
        }
        
        .refresh-btn:active {
            transform: scale(0.95);
        }
        
        .tips {
            background: rgba(255, 255, 255, 0.2);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 25px;
            color: white;
        }
        
        .tips h3 {
            margin-bottom: 15px;
        }
        
        .tips ul {
            list-style: none;
            padding-left: 0;
        }
        
        .tips li {
            padding: 10px 0;
            padding-left: 25px;
            position: relative;
        }
        
        .tips li:before {
            content: "💡";
            position: absolute;
            left: 0;
        }
        
        @media (max-width: 768px) {
            .header h1 {
                font-size: 1.8em;
            }
            
            .total-revenue .amount {
                font-size: 2em;
            }
            
            .projects {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Triple Empire Dashboard</h1>
            <p>Мониторинг всех проектов в реальном времени</p>
        </div>
        
        <div class="total-revenue">
            <h2>💰 Общий доход</h2>
            <div class="amount">{{ total_revenue }}₽</div>
            <div class="goal-progress">
                <p>Цель: 60,000₽ за 18 дней</p>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {{ progress }}%"></div>
                </div>
                <p style="margin-top: 10px;">{{ progress }}% выполнено</p>
            </div>
        </div>
        
        <div class="projects">
            <div class="project-card">
                <div class="emoji">💌</div>
                <h3>Анонимные Признания</h3>
                <div class="stat">
                    <span class="stat-label">Доход</span>
                    <span class="stat-value">{{ confessions_revenue }}₽</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Транзакций</span>
                    <span class="stat-value">{{ confessions_transactions }}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Пользователей</span>
                    <span class="stat-value">{{ confessions_users }}</span>
                </div>
            </div>
            
            <div class="project-card">
                <div class="emoji">🔮</div>
                <h3>AI Таро & Астрология</h3>
                <div class="stat">
                    <span class="stat-label">Доход</span>
                    <span class="stat-value">{{ tarot_revenue }}₽</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Транзакций</span>
                    <span class="stat-value">{{ tarot_transactions }}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Пользователей</span>
                    <span class="stat-value">{{ tarot_users }}</span>
                </div>
            </div>
            
            <div class="project-card">
                <div class="emoji">😂</div>
                <h3>Мемы на заказ</h3>
                <div class="stat">
                    <span class="stat-label">Доход</span>
                    <span class="stat-value">{{ memes_revenue }}₽</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Транзакций</span>
                    <span class="stat-value">{{ memes_transactions }}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Пользователей</span>
                    <span class="stat-value">{{ memes_users }}</span>
                </div>
            </div>
        </div>
        
        <div class="tips">
            <h3>💡 Советы для роста</h3>
            <ul>
                <li>Поделись ботами с 5 друзьями сегодня</li>
                <li>Опубликуй пост в соцсетях со ссылкой</li>
                <li>Попроси пользователей оставить отзывы</li>
                <li>Запусти конкурс с призами для вирусности</li>
                <li>Отвечай на вопросы пользователей быстро</li>
            </ul>
        </div>
    </div>
    
    <button class="refresh-btn" onclick="location.reload()">🔄</button>
    
    <script>
        // Автообновление каждые 30 секунд
        setTimeout(() => location.reload(), 30000);
    </script>
</body>
</html>
"""

@app.route('/')
def dashboard():
    """Главная страница дашборда"""
    # Получаем статистику по всем проектам
    confessions_stats = db.get_project_stats('confessions')
    tarot_stats = db.get_project_stats('tarot')
    memes_stats = db.get_project_stats('memes')
    
    # Общий доход
    total_revenue = (
        confessions_stats['revenue'] +
        tarot_stats['revenue'] +
        memes_stats['revenue']
    )
    
    # Прогресс к цели
    goal = 60000
    progress = min(100, (total_revenue / goal) * 100)
    
    return render_template_string(
        DASHBOARD_HTML,
        total_revenue=f"{total_revenue:,.0f}".replace(',', ' '),
        progress=f"{progress:.1f}",
        confessions_revenue=f"{confessions_stats['revenue']:,.0f}".replace(',', ' '),
        confessions_transactions=confessions_stats['transactions'],
        confessions_users=confessions_stats['users'],
        tarot_revenue=f"{tarot_stats['revenue']:,.0f}".replace(',', ' '),
        tarot_transactions=tarot_stats['transactions'],
        tarot_users=tarot_stats['users'],
        memes_revenue=f"{memes_stats['revenue']:,.0f}".replace(',', ' '),
        memes_transactions=memes_stats['transactions'],
        memes_users=memes_stats['users']
    )

if __name__ == '__main__':
    print("🚀 Dashboard запущен!")
    print("📱 Открой в браузере телефона: http://localhost:5000")
    print("💡 Для доступа из интернета используй ngrok или подобный сервис")
    app.run(host='0.0.0.0', port=5000, debug=False)

