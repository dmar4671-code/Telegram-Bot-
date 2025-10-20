"""
AI Marketing Orchestra - Полностью автоматизированный маркетинг БЕЗ участия друзей
Использует AI для генерации контента, поиска аудитории и автоматического продвижения
"""
import asyncio
import random
from datetime import datetime
from openai import OpenAI

# Инициализация OpenAI клиента (API ключ уже в переменных окружения)
client = OpenAI()

class AIMarketingOrchestra:
    """Оркестр AI-агентов для автоматического маркетинга"""
    
    def __init__(self):
        self.model = "gpt-4.1-mini"
        
    async def content_creator_agent(self, project_type):
        """Агент создания вирусного контента"""
        prompts = {
            'confessions': """Создай 5 вирусных постов для продвижения бота анонимных признаний в русскоязычном Telegram.
            Посты должны:
            - Быть короткими (2-3 предложения)
            - Вызывать любопытство
            - Содержать эмодзи
            - Быть на русском языке
            - Не быть спамом
            
            Формат: каждый пост с новой строки, без нумерации.""",
            
            'tarot': """Создай 5 вирусных постов для продвижения AI-бота гаданий на Таро в русскоязычном Telegram.
            Посты должны:
            - Быть мистическими и интригующими
            - Содержать эмодзи
            - Быть короткими
            - На русском языке
            
            Формат: каждый пост с новой строки, без нумерации.""",
            
            'memes': """Создай 5 вирусных постов для продвижения AI-бота создания мемов в русскоязычном Telegram.
            Посты должны:
            - Быть смешными
            - Содержать эмодзи
            - Быть короткими
            - На русском языке
            
            Формат: каждый пост с новой строки, без нумерации."""
        }
        
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Ты эксперт по вирусному маркетингу в русскоязычном Telegram."},
                    {"role": "user", "content": prompts[project_type]}
                ],
                temperature=0.9
            )
            
            content = response.choices[0].message.content
            posts = [p.strip() for p in content.split('\n') if p.strip() and not p.strip().startswith('#')]
            return posts[:5]
        except Exception as e:
            print(f"❌ Ошибка создания контента: {e}")
            return []
    
    async def channel_finder_agent(self):
        """Агент поиска целевых каналов и групп"""
        # Список популярных тематических каналов/групп (публичная информация)
        channels = {
            'confessions': [
                '@ru_confessions',
                '@anonymous_chat_ru',
                '@secrets_ru',
                '@priznania_ru',
                '@confession_room'
            ],
            'tarot': [
                '@tarot_ru',
                '@astrology_ru',
                '@magic_ru',
                '@gadanie_ru',
                '@ezoterika_ru'
            ],
            'memes': [
                '@memes_ru',
                '@humor_ru',
                '@jokes_ru',
                '@fun_ru',
                '@lol_ru'
            ]
        }
        
        # Генерируем стратегию поиска новых каналов
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Ты эксперт по поиску целевой аудитории в Telegram."},
                    {"role": "user", "content": """Предложи 10 ключевых слов для поиска тематических групп в Telegram 
                    по темам: анонимные признания, гадания, мемы. На русском языке. Только слова, без объяснений."""}
                ],
                temperature=0.7
            )
            
            keywords = response.choices[0].message.content.split('\n')
            keywords = [k.strip('- ').strip() for k in keywords if k.strip()]
            
            return {
                'channels': channels,
                'search_keywords': keywords[:10]
            }
        except Exception as e:
            print(f"❌ Ошибка поиска каналов: {e}")
            return {'channels': channels, 'search_keywords': []}
    
    async def engagement_agent(self, post_content):
        """Агент создания вовлекающих комментариев"""
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Ты создаёшь естественные, не спамные комментарии для Telegram."},
                    {"role": "user", "content": f"""Создай 3 коротких комментария (1-2 предложения) к посту: "{post_content}"
                    Комментарии должны:
                    - Быть естественными
                    - Не выглядеть как реклама
                    - Вызывать интерес
                    - Быть на русском
                    
                    Формат: каждый комментарий с новой строки."""}
                ],
                temperature=0.8
            )
            
            comments = response.choices[0].message.content.split('\n')
            return [c.strip() for c in comments if c.strip()][:3]
        except Exception as e:
            print(f"❌ Ошибка создания комментариев: {e}")
            return []
    
    async def viral_strategy_agent(self):
        """Агент разработки вирусной стратегии"""
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Ты эксперт по вирусному маркетингу без бюджета."},
                    {"role": "user", "content": """Создай план вирусного продвижения Telegram-ботов БЕЗ бюджета на сегодня.
                    Учти:
                    - Нет друзей для продвижения
                    - Нет денег на рекламу
                    - Только органические методы
                    - Русскоязычная аудитория
                    
                    Дай 5 конкретных действий на сегодня. Кратко, по пунктам."""}
                ],
                temperature=0.7
            )
            
            strategy = response.choices[0].message.content
            return strategy
        except Exception as e:
            print(f"❌ Ошибка создания стратегии: {e}")
            return "Стратегия не создана"
    
    async def timing_optimizer_agent(self):
        """Агент оптимизации времени публикаций"""
        # Оптимальное время для русскоязычной аудитории
        optimal_times = {
            'morning': '09:00-11:00',
            'lunch': '13:00-14:00',
            'evening': '18:00-21:00',
            'night': '22:00-23:00'
        }
        
        current_hour = datetime.now().hour
        
        if 9 <= current_hour < 11:
            return 'morning', 'Утро - хорошее время для мотивационного контента'
        elif 13 <= current_hour < 14:
            return 'lunch', 'Обед - время для лёгкого развлекательного контента'
        elif 18 <= current_hour < 21:
            return 'evening', 'Вечер - ЛУЧШЕЕ время для вирусного контента'
        elif 22 <= current_hour < 24:
            return 'night', 'Ночь - время для интимного контента (признания, гадания)'
        else:
            return 'other', 'Не оптимальное время, лучше подождать'
    
    async def run_daily_campaign(self):
        """Запуск ежедневной маркетинговой кампании"""
        print("🚀 Запуск AI Marketing Orchestra...")
        print(f"📅 Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n")
        
        # 1. Оптимизация времени
        time_slot, time_advice = await self.timing_optimizer_agent()
        print(f"⏰ Время: {time_slot}")
        print(f"💡 Совет: {time_advice}\n")
        
        # 2. Стратегия на день
        print("📋 Стратегия на сегодня:")
        strategy = await self.viral_strategy_agent()
        print(strategy)
        print()
        
        # 3. Создание контента для каждого проекта
        projects = ['confessions', 'tarot', 'memes']
        all_content = {}
        
        for project in projects:
            print(f"\n{'='*60}")
            print(f"📱 Проект: {project.upper()}")
            print(f"{'='*60}\n")
            
            # Создаём вирусный контент
            posts = await self.content_creator_agent(project)
            all_content[project] = posts
            
            print(f"✅ Создано {len(posts)} постов:\n")
            for i, post in enumerate(posts, 1):
                print(f"{i}. {post}\n")
            
            # Создаём комментарии для первого поста
            if posts:
                comments = await self.engagement_agent(posts[0])
                print(f"💬 Комментарии для вовлечения:\n")
                for i, comment in enumerate(comments, 1):
                    print(f"   {i}. {comment}")
            
            print()
        
        # 4. Поиск каналов
        print(f"\n{'='*60}")
        print("🔍 Целевые каналы и стратегия поиска")
        print(f"{'='*60}\n")
        
        channels_data = await self.channel_finder_agent()
        
        print("📢 Рекомендованные каналы:")
        for project, channels in channels_data['channels'].items():
            print(f"\n{project.upper()}:")
            for channel in channels:
                print(f"  • {channel}")
        
        print(f"\n🔎 Ключевые слова для поиска новых каналов:")
        for keyword in channels_data['search_keywords']:
            print(f"  • {keyword}")
        
        # 5. Сохранение результатов
        await self.save_campaign_results(all_content, channels_data, strategy)
        
        print(f"\n{'='*60}")
        print("✅ Кампания завершена!")
        print(f"{'='*60}\n")
        
        return all_content, channels_data, strategy
    
    async def save_campaign_results(self, content, channels, strategy):
        """Сохранение результатов кампании"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"/home/ubuntu/Telegram-Bot-/marketing_campaign_{timestamp}.md"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# Маркетинговая кампания {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n")
            
            f.write("## Стратегия\n\n")
            f.write(f"{strategy}\n\n")
            
            f.write("## Контент для публикации\n\n")
            for project, posts in content.items():
                f.write(f"### {project.upper()}\n\n")
                for i, post in enumerate(posts, 1):
                    f.write(f"{i}. {post}\n\n")
            
            f.write("## Целевые каналы\n\n")
            for project, channels_list in channels['channels'].items():
                f.write(f"### {project.upper()}\n\n")
                for channel in channels_list:
                    f.write(f"- {channel}\n")
                f.write("\n")
            
            f.write("## Ключевые слова для поиска\n\n")
            for keyword in channels['search_keywords']:
                f.write(f"- {keyword}\n")
        
        print(f"💾 Результаты сохранены: {filename}")

async def main():
    """Главная функция"""
    orchestra = AIMarketingOrchestra()
    
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║           🤖 AI MARKETING ORCHESTRA 🤖                       ║
║                                                              ║
║     Полностью автоматизированный маркетинг БЕЗ бюджета      ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    await orchestra.run_daily_campaign()
    
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║  📋 ЧТО ДЕЛАТЬ ДАЛЬШЕ:                                       ║
║                                                              ║
║  1. Используй созданный контент для постов                   ║
║  2. Найди указанные каналы в Telegram                        ║
║  3. Публикуй контент в оптимальное время                     ║
║  4. Запускай этот скрипт каждый день                         ║
║                                                              ║
║  💡 Для автоматического запуска используй cron:              ║
║     crontab -e                                               ║
║     0 9,13,18 * * * python3 ai_marketing_orchestra.py        ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)

if __name__ == "__main__":
    asyncio.run(main())

