"""
ПРОЕКТ 3: Мемы на заказ
Telegram-бот для создания персонализированных мемов с AI
"""
import sys
sys.path.append('/home/ubuntu/triple-telegram-empire')

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from shared.database.db import db
from shared.utils.ai_helper import ai

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Конфигурация
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # Замените на реальный токен
PROJECT_NAME = "memes"

class MemesBot:
    def __init__(self):
        self.app = Application.builder().token(BOT_TOKEN).build()
        self.setup_handlers()
        self.user_states = {}
    
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
        
        text = f"😂 Привет, {user.first_name}!\n\n"
        text += "Я создаю персонализированные мемы с помощью AI!\n\n"
        text += "🎨 Что я умею:\n"
        text += "• Мемы про друзей\n"
        text += "• Мемы про работу\n"
        text += "• Мемы на любую тему\n"
        text += "• Мемы на день рождения\n\n"
        text += "🎁 Первый мем БЕСПЛАТНО!\n\n"
        text += "💰 Цены:\n"
        text += "• 1 мем - 99₽\n"
        text += "• 5 мемов - 399₽\n"
        text += "• 10 мемов - 699₽\n"
        text += "• Безлимит на месяц - 999₽"
        
        keyboard = [
            [InlineKeyboardButton("🎨 Создать мем", callback_data="create_meme")],
            [InlineKeyboardButton("💎 Безлимит (999₽)", callback_data="unlimited")],
            [InlineKeyboardButton("📊 Мои мемы", callback_data="my_memes")]
        ]
        
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик нажатий на кнопки"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        data = query.data
        
        if data == "create_meme":
            await self.start_meme_creation(query, context)
        elif data == "unlimited":
            await self.show_unlimited_info(query, context)
        elif data == "my_memes":
            await self.show_my_memes(query, context)
        elif data.startswith("pay_"):
            await self.process_payment(query, context, data)
    
    async def start_meme_creation(self, query, context):
        """Начать создание мема"""
        user_id = query.from_user.id
        
        # Проверяем, был ли уже бесплатный мем
        import sqlite3
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM meme_orders WHERE user_id = ?', (user_id,))
        count = cursor.fetchone()[0]
        conn.close()
        
        is_free = (count == 0)
        
        if is_free:
            text = "🎁 Твой первый мем БЕСПЛАТНО!\n\n"
        else:
            text = "💰 Стоимость: 99₽\n\n"
        
        text += "📝 Опиши, какой мем ты хочешь:\n\n"
        text += "Примеры:\n"
        text += "• Мем про моего друга Васю, который всегда опаздывает\n"
        text += "• Мем про понедельник и работу\n"
        text += "• Мем про кота, который украл сосиску\n\n"
        text += "Напиши описание в следующем сообщении:"
        
        self.user_states[user_id] = {
            'action': 'waiting_meme_description',
            'is_free': is_free
        }
        
        await query.edit_message_text(text)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка текстовых сообщений"""
        user_id = update.effective_user.id
        text = update.message.text
        
        if user_id in self.user_states:
            state = self.user_states[user_id]
            
            if state['action'] == 'waiting_meme_description':
                await self.generate_meme(update, context, text, state)
                del self.user_states[user_id]
                return
        
        await update.message.reply_text("Используй /start чтобы создать мем! 😂")
    
    async def generate_meme(self, update, context, description, state):
        """Генерация мема"""
        user_id = update.effective_user.id
        is_free = state['is_free']
        
        await update.message.reply_text("🎨 Создаю мем...")
        
        # Генерируем идею мема с помощью AI
        meme_idea = await ai.generate_meme_idea(description)
        meme_text = await ai.generate_meme_text(description)
        
        text = f"😂 ТВОЙ МЕМ ГОТОВ!\n\n"
        text += f"📝 Описание: {description}\n\n"
        text += f"🎨 Идея мема:\n{meme_idea}\n\n"
        text += f"📄 Текст мема:\n"
        text += f"Сверху: {meme_text.get('top', '')}\n"
        text += f"Снизу: {meme_text.get('bottom', '')}\n\n"
        text += "⚠️ Примечание: В полной версии здесь будет готовая картинка мема.\n"
        text += "Для генерации изображений нужно подключить DALL-E API.\n\n"
        text += "💡 Инструкция: IMAGE_GENERATION_SETUP.md"
        
        keyboard = [
            [InlineKeyboardButton("🔄 Другой мем", callback_data="create_meme")],
            [InlineKeyboardButton("💎 Безлимит", callback_data="unlimited")]
        ]
        
        # Сохраняем в базу
        import sqlite3
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO meme_orders (user_id, description, meme_url, paid, amount)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, description, "demo_meme.jpg", is_free, 0 if is_free else 99))
        conn.commit()
        
        if not is_free:
            db.update_revenue(PROJECT_NAME, 99)
        
        conn.close()
        
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    async def show_my_memes(self, query, context):
        """Показать созданные мемы"""
        user_id = query.from_user.id
        
        import sqlite3
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT description, created_at
            FROM meme_orders
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT 10
        ''', (user_id,))
        memes = cursor.fetchall()
        conn.close()
        
        if not memes:
            text = "📭 У тебя пока нет мемов.\n\nСоздай свой первый мем бесплатно!"
            keyboard = [[InlineKeyboardButton("🎨 Создать мем", callback_data="create_meme")]]
        else:
            text = f"😂 ТВОИ МЕМЫ ({len(memes)}):\n\n"
            for i, (desc, created_at) in enumerate(memes, 1):
                short_desc = desc[:50] + "..." if len(desc) > 50 else desc
                text += f"{i}. {short_desc}\n"
            
            keyboard = [
                [InlineKeyboardButton("🎨 Создать ещё", callback_data="create_meme")],
                [InlineKeyboardButton("💎 Безлимит", callback_data="unlimited")]
            ]
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    async def show_unlimited_info(self, query, context):
        """Информация о безлимите"""
        text = "💎 БЕЗЛИМИТНАЯ ПОДПИСКА\n\n"
        text += "Что даёт безлимит:\n"
        text += "✅ Неограниченное количество мемов\n"
        text += "✅ Приоритетная генерация\n"
        text += "✅ Эксклюзивные шаблоны\n"
        text += "✅ Без водяных знаков\n\n"
        text += "💰 Цена: 999₽/месяц\n\n"
        text += "🎁 Бонус: Пригласи 3 друзей и получи месяц бесплатно!"
        
        keyboard = [
            [InlineKeyboardButton("💳 Купить безлимит (999₽)", callback_data="pay_unlimited")],
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
        logger.info("😂 Бот 'Мемы на заказ' запущен!")
        self.app.run_polling()

if __name__ == "__main__":
    bot = MemesBot()
    bot.run()

