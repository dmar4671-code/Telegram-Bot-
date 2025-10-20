"""
ПРОЕКТ 1: Анонимные Признания 2.0
Telegram-бот для анонимных сообщений
"""
import sys
sys.path.append('/home/ubuntu/triple-telegram-empire')

import logging
import random
import string
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from shared.database.db import db
from shared.utils.ai_helper import ai
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Конфигурация
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # Замените на реальный токен
PROJECT_NAME = "confessions"

class ConfessionsBot:
    def __init__(self):
        self.app = Application.builder().token(BOT_TOKEN).build()
        self.setup_handlers()
    
    def setup_handlers(self):
        """Настройка обработчиков"""
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(CommandHandler("mybox", self.my_box))
        self.app.add_handler(CommandHandler("stats", self.stats))
        self.app.add_handler(CallbackQueryHandler(self.button_callback))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    def generate_box_code(self) -> str:
        """Генерация уникального кода коробки"""
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        user = update.effective_user
        args = context.args
        
        # Добавляем пользователя в базу
        referrer_id = int(args[0]) if args and args[0].isdigit() else None
        db.add_user(user.id, user.username, user.first_name, referrer_id)
        
        # Проверяем, есть ли у пользователя коробка
        conn = db.conn if hasattr(db, 'conn') else None
        import sqlite3
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT box_code, messages_count FROM confession_boxes WHERE user_id = ?', (user.id,))
        box = cursor.fetchone()
        
        if box:
            box_code, messages_count = box
            text = f"👋 С возвращением, {user.first_name}!\n\n"
            text += f"📦 Твоя коробка признаний: `{box_code}`\n"
            text += f"💌 Получено сообщений: {messages_count}\n\n"
            text += f"🔗 Твоя ссылка для друзей:\nhttps://t.me/{context.bot.username}?start={box_code}"
        else:
            text = f"👋 Привет, {user.first_name}!\n\n"
            text += "🎭 Добро пожаловать в мир анонимных признаний!\n\n"
            text += "Здесь твои друзья могут написать тебе что угодно анонимно:\n"
            text += "• Признания в любви 💕\n"
            text += "• Честное мнение 💭\n"
            text += "• Секреты и тайны 🤫\n\n"
            text += "Создай свою коробку признаний прямо сейчас!"
        
        keyboard = [
            [InlineKeyboardButton("🎁 Создать коробку", callback_data="create_box")],
            [InlineKeyboardButton("📬 Мои сообщения", callback_data="my_messages")],
            [InlineKeyboardButton("💎 VIP статус", callback_data="vip_info")]
        ]
        
        conn.close()
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    
    async def my_box(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать информацию о коробке"""
        user_id = update.effective_user.id
        
        import sqlite3
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT box_code, messages_count, is_vip, vip_until 
            FROM confession_boxes 
            WHERE user_id = ?
        ''', (user_id,))
        box = cursor.fetchone()
        
        if not box:
            await update.message.reply_text("❌ У тебя ещё нет коробки. Используй /start чтобы создать!")
            conn.close()
            return
        
        box_code, messages_count, is_vip, vip_until = box
        
        text = f"📦 Твоя коробка признаний\n\n"
        text += f"🔑 Код: `{box_code}`\n"
        text += f"💌 Всего сообщений: {messages_count}\n"
        
        if is_vip and vip_until:
            vip_date = datetime.fromisoformat(vip_until)
            if vip_date > datetime.now():
                text += f"💎 VIP до: {vip_date.strftime('%d.%m.%Y')}\n"
            else:
                text += f"⭐ VIP истёк\n"
        
        text += f"\n🔗 Поделись ссылкой:\nhttps://t.me/{context.bot.username}?start={box_code}\n\n"
        text += "Чем больше друзей увидят ссылку, тем больше признаний получишь! 🔥"
        
        keyboard = [
            [InlineKeyboardButton("📬 Прочитать сообщения", callback_data="read_messages")],
            [InlineKeyboardButton("📊 Статистика", callback_data="box_stats")]
        ]
        
        conn.close()
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик нажатий на кнопки"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        data = query.data
        
        if data == "create_box":
            await self.create_box(query, context)
        elif data == "my_messages":
            await self.show_messages(query, context)
        elif data == "vip_info":
            await self.show_vip_info(query, context)
        elif data.startswith("read_msg_"):
            message_id = int(data.split("_")[2])
            await self.read_message(query, context, message_id)
        elif data.startswith("pay_"):
            await self.process_payment(query, context, data)
    
    async def create_box(self, query, context):
        """Создание новой коробки"""
        user_id = query.from_user.id
        
        import sqlite3
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        
        # Проверяем, есть ли уже коробка
        cursor.execute('SELECT box_code FROM confession_boxes WHERE user_id = ?', (user_id,))
        existing = cursor.fetchone()
        
        if existing:
            await query.edit_message_text("❌ У тебя уже есть коробка! Используй /mybox")
            conn.close()
            return
        
        # Создаём новую коробку
        box_code = self.generate_box_code()
        cursor.execute('''
            INSERT INTO confession_boxes (user_id, box_code)
            VALUES (?, ?)
        ''', (user_id, box_code))
        conn.commit()
        conn.close()
        
        text = f"🎉 Поздравляю! Твоя коробка создана!\n\n"
        text += f"🔑 Код коробки: `{box_code}`\n\n"
        text += f"🔗 Поделись этой ссылкой с друзьями:\nhttps://t.me/{context.bot.username}?start={box_code}\n\n"
        text += "Они смогут отправить тебе анонимные сообщения! 🤫\n\n"
        text += "💡 Совет: Размести ссылку в Instagram Stories, VK или Telegram статусе!"
        
        keyboard = [
            [InlineKeyboardButton("📬 Проверить сообщения", callback_data="my_messages")],
            [InlineKeyboardButton("💎 Стать VIP", callback_data="vip_info")]
        ]
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    
    async def show_messages(self, query, context):
        """Показать список сообщений"""
        user_id = query.from_user.id
        
        import sqlite3
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        
        # Получаем коробку пользователя
        cursor.execute('SELECT id, is_vip FROM confession_boxes WHERE user_id = ?', (user_id,))
        box = cursor.fetchone()
        
        if not box:
            await query.edit_message_text("❌ У тебя нет коробки. Создай её командой /start")
            conn.close()
            return
        
        box_id, is_vip = box
        
        # Получаем сообщения
        cursor.execute('''
            SELECT id, message, is_read, created_at
            FROM confessions
            WHERE box_id = ?
            ORDER BY created_at DESC
        ''', (box_id,))
        messages = cursor.fetchall()
        
        if not messages:
            text = "📭 Пока нет сообщений.\n\nПоделись своей ссылкой с друзьями!"
            await query.edit_message_text(text)
            conn.close()
            return
        
        # Первые 3 сообщения бесплатно
        free_count = 3
        text = f"💌 У тебя {len(messages)} сообщений!\n\n"
        
        if is_vip:
            text += "💎 VIP: Читай все сообщения бесплатно!\n\n"
            for i, msg in enumerate(messages[:10], 1):
                msg_id, message, is_read, created_at = msg
                preview = message[:50] + "..." if len(message) > 50 else message
                text += f"{i}. {preview}\n"
        else:
            text += f"🎁 Первые {free_count} сообщения бесплатно:\n\n"
            for i, msg in enumerate(messages[:free_count], 1):
                msg_id, message, is_read, created_at = msg
                text += f"{i}. {message}\n\n"
            
            if len(messages) > free_count:
                text += f"🔒 Ещё {len(messages) - free_count} сообщений скрыто\n\n"
                text += "💰 Разблокируй все сообщения:\n"
                text += "• 49₽ - 1 сообщение\n"
                text += "• 199₽ - все сообщения\n"
                text += "• 499₽ - VIP на месяц (безлимит)"
        
        keyboard = []
        if not is_vip and len(messages) > free_count:
            keyboard.append([InlineKeyboardButton("💳 Разблокировать все (199₽)", callback_data="pay_all")])
            keyboard.append([InlineKeyboardButton("💎 VIP на месяц (499₽)", callback_data="pay_vip")])
        
        conn.close()
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard) if keyboard else None)
    
    async def show_vip_info(self, query, context):
        """Информация о VIP"""
        text = "💎 VIP СТАТУС\n\n"
        text += "Что даёт VIP:\n"
        text += "✅ Безлимитное чтение всех сообщений\n"
        text += "✅ Узнай, кто написал (если отправитель согласился)\n"
        text += "✅ Приоритетная поддержка\n"
        text += "✅ Эксклюзивный значок 💎\n\n"
        text += "💰 Цена: 499₽/месяц\n\n"
        text += "🎁 Бонус: Пригласи 10 друзей и получи VIP бесплатно!"
        
        keyboard = [
            [InlineKeyboardButton("💳 Купить VIP (499₽)", callback_data="pay_vip")],
            [InlineKeyboardButton("🎁 Пригласить друзей", callback_data="referral_info")]
        ]
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    async def process_payment(self, query, context, payment_type):
        """Обработка платежа (заглушка)"""
        text = "💳 ОПЛАТА\n\n"
        text += "⚠️ Это демо-версия бота.\n\n"
        text += "Для настройки реальных платежей нужно:\n"
        text += "1. Подключить Telegram Stars или ЮKassa\n"
        text += "2. Получить API ключи\n"
        text += "3. Настроить webhook для обработки платежей\n\n"
        text += "📝 Инструкция в файле PAYMENT_SETUP.md"
        
        await query.edit_message_text(text)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка текстовых сообщений"""
        # Проверяем, это отправка признания или что-то другое
        user_id = update.effective_user.id
        text = update.message.text
        
        # Модерация контента
        moderation = await ai.moderate_content(text)
        if not moderation['is_safe']:
            await update.message.reply_text("❌ Сообщение содержит недопустимый контент и не может быть отправлено.")
            return
        
        await update.message.reply_text("💬 Чтобы отправить признание, используй ссылку друга!")
    
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
        logger.info("🚀 Бот 'Анонимные Признания' запущен!")
        self.app.run_polling()

if __name__ == "__main__":
    bot = ConfessionsBot()
    bot.run()

