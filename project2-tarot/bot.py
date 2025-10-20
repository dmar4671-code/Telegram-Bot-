"""
ПРОЕКТ 2: AI Таро & Астрология
Telegram-бот для гаданий
"""
import sys
sys.path.append('/home/ubuntu/triple-telegram-empire')

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from shared.database.db import db
from shared.utils.ai_helper import ai
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Конфигурация
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # Замените на реальный токен
PROJECT_NAME = "tarot"

ZODIAC_SIGNS = {
    "♈ Овен": "aries",
    "♉ Телец": "taurus",
    "♊ Близнецы": "gemini",
    "♋ Рак": "cancer",
    "♌ Лев": "leo",
    "♍ Дева": "virgo",
    "♎ Весы": "libra",
    "♏ Скорпион": "scorpio",
    "♐ Стрелец": "sagittarius",
    "♑ Козерог": "capricorn",
    "♒ Водолей": "aquarius",
    "♓ Рыбы": "pisces"
}

class TarotBot:
    def __init__(self):
        self.app = Application.builder().token(BOT_TOKEN).build()
        self.setup_handlers()
        self.user_states = {}  # Хранение состояний пользователей
    
    def setup_handlers(self):
        """Настройка обработчиков"""
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(CommandHandler("stats", self.stats))
        self.app.add_handler(CallbackQueryHandler(self.button_callback))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        user = update.effective_user
        db.add_user(user.id, user.username, user.first_name)
        
        text = f"🔮 Добро пожаловать, {user.first_name}!\n\n"
        text += "Я помогу тебе заглянуть в будущее с помощью карт Таро и астрологии.\n\n"
        text += "✨ Что я умею:\n"
        text += "🃏 Гадание на Таро\n"
        text += "⭐ Персональный гороскоп\n"
        text += "💕 Гадание на любовь\n"
        text += "💼 Гадание на карьеру\n\n"
        text += "🎁 Первое гадание БЕСПЛАТНО!"
        
        keyboard = [
            [InlineKeyboardButton("🃏 Гадание на Таро", callback_data="tarot_menu")],
            [InlineKeyboardButton("⭐ Гороскоп на день", callback_data="horoscope_menu")],
            [InlineKeyboardButton("💎 VIP подписка", callback_data="vip_info")]
        ]
        
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик нажатий на кнопки"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        data = query.data
        
        if data == "tarot_menu":
            await self.show_tarot_menu(query, context)
        elif data == "horoscope_menu":
            await self.show_horoscope_menu(query, context)
        elif data == "vip_info":
            await self.show_vip_info(query, context)
        elif data.startswith("tarot_"):
            reading_type = data.split("_")[1]
            await self.start_tarot_reading(query, context, reading_type)
        elif data.startswith("zodiac_"):
            sign = data.split("_", 1)[1]
            await self.generate_horoscope(query, context, sign)
        elif data.startswith("pay_"):
            await self.process_payment(query, context, data)
    
    async def show_tarot_menu(self, query, context):
        """Меню гаданий на Таро"""
        text = "🃏 ГАДАНИЕ НА ТАРО\n\n"
        text += "Выбери тип гадания:\n\n"
        text += "🌅 На день - 99₽\n"
        text += "💕 На любовь - 199₽\n"
        text += "💼 На карьеру - 199₽\n"
        text += "🔮 Общее гадание - 299₽\n\n"
        text += "🎁 Первое гадание БЕСПЛАТНО!"
        
        keyboard = [
            [InlineKeyboardButton("🌅 На день (99₽)", callback_data="tarot_day")],
            [InlineKeyboardButton("💕 На любовь (199₽)", callback_data="tarot_love")],
            [InlineKeyboardButton("💼 На карьеру (199₽)", callback_data="tarot_career")],
            [InlineKeyboardButton("🔮 Общее (299₽)", callback_data="tarot_general")],
            [InlineKeyboardButton("« Назад", callback_data="back_to_main")]
        ]
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    async def show_horoscope_menu(self, query, context):
        """Меню выбора знака зодиака"""
        text = "⭐ ГОРОСКОП НА ДЕНЬ\n\n"
        text += "Выбери свой знак зодиака:\n\n"
        text += "💰 Цена: 49₽\n"
        text += "🎁 Первый гороскоп БЕСПЛАТНО!"
        
        keyboard = []
        signs_list = list(ZODIAC_SIGNS.items())
        for i in range(0, len(signs_list), 3):
            row = []
            for sign_name, sign_code in signs_list[i:i+3]:
                row.append(InlineKeyboardButton(sign_name, callback_data=f"zodiac_{sign_code}"))
            keyboard.append(row)
        
        keyboard.append([InlineKeyboardButton("« Назад", callback_data="back_to_main")])
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    async def start_tarot_reading(self, query, context, reading_type):
        """Начать гадание на Таро"""
        user_id = query.from_user.id
        
        # Проверяем, было ли уже бесплатное гадание
        import sqlite3
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM tarot_readings WHERE user_id = ?', (user_id,))
        count = cursor.fetchone()[0]
        
        is_free = (count == 0)
        
        if is_free:
            text = "🎁 Это твоё первое гадание - оно БЕСПЛАТНО!\n\n"
        else:
            prices = {"day": 99, "love": 199, "career": 199, "general": 299}
            price = prices.get(reading_type, 99)
            text = f"💳 Стоимость: {price}₽\n\n"
            text += "⚠️ Это демо-версия. Платежи не подключены.\n\n"
        
        text += "❓ Задай свой вопрос картам Таро:\n"
        text += "(Напиши свой вопрос в следующем сообщении)"
        
        # Сохраняем состояние пользователя
        self.user_states[user_id] = {
            'action': 'waiting_tarot_question',
            'reading_type': reading_type,
            'is_free': is_free
        }
        
        conn.close()
        await query.edit_message_text(text)
    
    async def generate_horoscope(self, query, context, zodiac_sign):
        """Генерация гороскопа"""
        user_id = query.from_user.id
        
        await query.edit_message_text("⏳ Читаю звёзды...")
        
        # Генерируем гороскоп с помощью AI
        horoscope = await ai.generate_horoscope(zodiac_sign)
        
        # Находим название знака
        sign_name = [k for k, v in ZODIAC_SIGNS.items() if v == zodiac_sign][0]
        
        text = f"⭐ ГОРОСКОП НА СЕГОДНЯ\n"
        text += f"{sign_name}\n\n"
        text += horoscope
        text += "\n\n💫 Пусть звёзды будут благосклонны к тебе!"
        
        keyboard = [
            [InlineKeyboardButton("🔄 Другой знак", callback_data="horoscope_menu")],
            [InlineKeyboardButton("🃏 Гадание на Таро", callback_data="tarot_menu")]
        ]
        
        # Сохраняем в базу
        import sqlite3
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO tarot_readings (user_id, reading_type, question, result, paid, amount)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, 'horoscope', zodiac_sign, horoscope, False, 0))
        conn.commit()
        conn.close()
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка текстовых сообщений"""
        user_id = update.effective_user.id
        text = update.message.text
        
        # Проверяем состояние пользователя
        if user_id in self.user_states:
            state = self.user_states[user_id]
            
            if state['action'] == 'waiting_tarot_question':
                await self.process_tarot_question(update, context, text, state)
                del self.user_states[user_id]
                return
        
        # Если нет активного состояния
        await update.message.reply_text("Используй /start чтобы начать гадание! 🔮")
    
    async def process_tarot_question(self, update, context, question, state):
        """Обработка вопроса для гадания"""
        user_id = update.effective_user.id
        reading_type = state['reading_type']
        is_free = state['is_free']
        
        await update.message.reply_text("🃏 Раскладываю карты Таро...")
        
        # Генерируем гадание с помощью AI
        reading = await ai.generate_tarot_reading(question, reading_type)
        
        text = f"🔮 ГАДАНИЕ НА ТАРО\n\n"
        text += f"❓ Твой вопрос: {question}\n\n"
        text += reading
        text += "\n\n✨ Пусть карты укажут тебе верный путь!"
        
        keyboard = [
            [InlineKeyboardButton("🔄 Ещё гадание", callback_data="tarot_menu")],
            [InlineKeyboardButton("⭐ Гороскоп", callback_data="horoscope_menu")]
        ]
        
        # Сохраняем в базу
        import sqlite3
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO tarot_readings (user_id, reading_type, question, result, paid, amount)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, reading_type, question, reading, is_free, 0 if is_free else 99))
        conn.commit()
        
        if not is_free:
            db.update_revenue(PROJECT_NAME, 99)
        
        conn.close()
        
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    async def show_vip_info(self, query, context):
        """Информация о VIP"""
        text = "💎 VIP ПОДПИСКА\n\n"
        text += "Что даёт VIP:\n"
        text += "✅ Безлимитные гадания\n"
        text += "✅ Ежедневный гороскоп\n"
        text += "✅ Персональные предсказания\n"
        text += "✅ Приоритетная поддержка\n\n"
        text += "💰 Цена: 999₽/месяц\n\n"
        text += "🎁 Бонус: Пригласи 5 друзей и получи месяц VIP бесплатно!"
        
        keyboard = [
            [InlineKeyboardButton("💳 Купить VIP (999₽)", callback_data="pay_vip")],
            [InlineKeyboardButton("« Назад", callback_data="back_to_main")]
        ]
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    async def process_payment(self, query, context, payment_type):
        """Обработка платежа (заглушка)"""
        text = "💳 ОПЛАТА\n\n"
        text += "⚠️ Это демо-версия бота.\n\n"
        text += "Для настройки реальных платежей см. PAYMENT_SETUP.md"
        
        await query.edit_message_text(text)
    
    async def stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Статистика проекта"""
        stats = db.get_project_stats(PROJECT_NAME)
        
        text = f"📊 СТАТИСТИКА ПРОЕКТА\n\n"
        text += f"💰 Доход: {stats['revenue']:.2f}₽\n"
        text += f"💳 Транзакций: {stats['transactions']}\n"
        text += f"👥 Пользователей: {stats['users']}\n"
        
        await update.message.reply_text(text)
    
    def run(self):
        """Запуск бота"""
        logger.info("🔮 Бот 'AI Таро' запущен!")
        self.app.run_polling()

if __name__ == "__main__":
    bot = TarotBot()
    bot.run()

