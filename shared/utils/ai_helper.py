"""
Утилиты для работы с AI (OpenAI API)
"""
import os
from openai import OpenAI

class AIHelper:
    def __init__(self):
        self.client = OpenAI()
    
    async def generate_tarot_reading(self, question: str, reading_type: str) -> str:
        """Генерация гадания на Таро"""
        prompts = {
            "day": f"Ты опытный таролог. Сделай гадание на день для человека. Вопрос: {question}. Используй 3 карты Таро, опиши их значение и дай совет. Пиши мистически и загадочно, но позитивно. Максимум 300 слов.",
            "love": f"Ты опытный таролог. Сделай гадание на любовь. Вопрос: {question}. Используй расклад на 5 карт Таро, опиши ситуацию в любви и дай рекомендации. Пиши романтично и загадочно. Максимум 400 слов.",
            "career": f"Ты опытный таролог. Сделай гадание на карьеру и финансы. Вопрос: {question}. Используй 4 карты Таро, опиши перспективы и дай практические советы. Максимум 350 слов.",
            "general": f"Ты опытный таролог. Сделай общее гадание. Вопрос: {question}. Используй расклад на 7 карт Таро, дай подробный ответ. Максимум 500 слов."
        }
        
        prompt = prompts.get(reading_type, prompts["general"])
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": "Ты мистический таролог с 20-летним опытом. Твои предсказания всегда точны и помогают людям."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.9,
                max_tokens=600
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Карты сегодня молчат... Попробуйте позже. (Ошибка: {str(e)})"
    
    async def generate_horoscope(self, zodiac_sign: str) -> str:
        """Генерация гороскопа на день"""
        prompt = f"Создай гороскоп на сегодня для знака зодиака {zodiac_sign}. Напиши о любви, карьере, здоровье и общем настроении. Будь позитивным и мотивирующим. Максимум 200 слов."
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": "Ты профессиональный астролог, который пишет точные и вдохновляющие гороскопы."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=300
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Звёзды сегодня скрыты облаками... (Ошибка: {str(e)})"
    
    async def generate_meme_idea(self, description: str) -> str:
        """Генерация идеи для мема"""
        prompt = f"Создай смешную идею для мема на основе описания: {description}. Опиши, что должно быть на картинке, какой текст сверху и снизу. Мем должен быть понятным русскоязычной аудитории и смешным. Максимум 150 слов."
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": "Ты креативный мемолог, который создаёт вирусные мемы для русскоязычной аудитории."},
                    {"role": "user", "content": prompt}
                ],
                temperature=1.0,
                max_tokens=200
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Креатив сломался... (Ошибка: {str(e)})"
    
    async def generate_meme_text(self, description: str) -> dict:
        """Генерация текста для мема (верх и низ)"""
        prompt = f"Создай текст для мема. Описание: {description}. Ответь в формате JSON: {{\"top\": \"текст сверху\", \"bottom\": \"текст снизу\"}}. Текст должен быть коротким, смешным и на русском языке."
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": "Ты создаёшь тексты для мемов. Отвечай только в формате JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=1.0,
                max_tokens=100,
                response_format={"type": "json_object"}
            )
            import json
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            return {"top": "КОГДА ЧТО-ТО", "bottom": "ПОШЛО НЕ ТАК"}
    
    async def moderate_content(self, text: str) -> dict:
        """Модерация контента на токсичность"""
        try:
            response = self.client.moderations.create(input=text)
            result = response.results[0]
            return {
                "is_safe": not result.flagged,
                "categories": result.categories.model_dump() if result.flagged else {}
            }
        except Exception as e:
            # В случае ошибки считаем контент безопасным
            return {"is_safe": True, "categories": {}}
    
    async def generate_marketing_comment(self, post_text: str, bot_name: str) -> str:
        """Генерация нативного комментария для маркетинга"""
        prompt = f"Пост: '{post_text}'. Напиши короткий естественный комментарий (1-2 предложения), в котором ненавязчиво упомянешь бота @{bot_name}. Комментарий должен выглядеть как органическая рекомендация от реального человека, а не как реклама."
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": "Ты обычный пользователь Telegram, который делится полезными ботами с друзьями."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.9,
                max_tokens=100
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Попробуй @{bot_name}, мне помог! 👍"

# Глобальный экземпляр AI помощника
ai = AIHelper()

