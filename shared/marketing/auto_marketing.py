"""
Система автоматического маркетинга для всех проектов
Работает БЕЗ вложений - только органический рост
"""
import asyncio
import random
from typing import List, Dict
import sys
sys.path.append('/home/ubuntu/triple-telegram-empire')

class AutoMarketing:
    def __init__(self):
        self.viral_templates = {
            'confessions': [
                "Мне написали {count} анонимных сообщений 😱 Попробуй сам: {link}",
                "Узнала, что обо мне думают друзья через этот бот 👀 {link}",
                "Кто-то признался мне в любви анонимно 💕 Создай свою коробку: {link}",
                "{count} человек написали мне что-то... Интересно, что 🤔 {link}"
            ],
            'tarot': [
                "Карты Таро предсказали мне {prediction} 🔮 Попробуй: {link}",
                "Этот бот угадал мою ситуацию на 100%! 😱 {link}",
                "Гороскоп на сегодня оказался точным 💫 {link}",
                "Спросила у карт Таро про любовь... Результат шокировал 💕 {link}"
            ],
            'memes': [
                "Этот бот создал мем про меня за 10 секунд 😂 {link}",
                "Лучший мем про понедельник, который я видел 🤣 {link}",
                "AI сделал мем про моего друга - он в шоке 😆 {link}",
                "Подарил другу персональный мем на ДР - он оценил 🎉 {link}"
            ]
        }
    
    def generate_share_text(self, project: str, **kwargs) -> str:
        """Генерация текста для шаринга"""
        templates = self.viral_templates.get(project, [])
        if not templates:
            return ""
        
        template = random.choice(templates)
        return template.format(**kwargs)
    
    async def create_referral_link(self, bot_username: str, user_id: int) -> str:
        """Создание реферальной ссылки"""
        return f"https://t.me/{bot_username}?start={user_id}"
    
    def get_free_marketing_channels(self) -> List[Dict]:
        """
        Список бесплатных каналов для продвижения
        (без спама - только легальные методы)
        """
        return [
            {
                'type': 'telegram_groups',
                'name': 'Тематические группы',
                'description': 'Поиск групп по интересам и органическое упоминание',
                'daily_reach': '100-500',
                'method': 'Участвуй в обсуждениях, помогай людям, ненавязчиво упоминай бота'
            },
            {
                'type': 'word_of_mouth',
                'name': 'Сарафанное радио',
                'description': 'Расскажи друзьям, семье, коллегам',
                'daily_reach': '10-50',
                'method': 'Личные рекомендации - самый эффективный способ'
            },
            {
                'type': 'social_media',
                'name': 'Соцсети (VK, Instagram)',
                'description': 'Посты в своих аккаунтах',
                'daily_reach': '50-200',
                'method': 'Сториз, посты, статусы со ссылкой на бота'
            },
            {
                'type': 'forums',
                'name': 'Форумы и Q&A',
                'description': 'Ответы на вопросы с упоминанием бота',
                'daily_reach': '20-100',
                'method': 'Pikabu, Reddit, тематические форумы'
            },
            {
                'type': 'viral_mechanics',
                'name': 'Встроенная вирусность',
                'description': 'Пользователи сами приводят друзей',
                'daily_reach': '100-1000',
                'method': 'Реферальная программа, обязательный шаринг'
            }
        ]
    
    def get_viral_mechanics(self, project: str) -> Dict:
        """
        Вирусные механики для каждого проекта
        """
        mechanics = {
            'confessions': {
                'mandatory_share': {
                    'name': 'Обязательный шаринг',
                    'description': 'Чтобы получить сообщения, нужно поделиться ссылкой',
                    'conversion': '100%',
                    'viral_coefficient': '3-5'
                },
                'curiosity_trigger': {
                    'name': 'Триггер любопытства',
                    'description': 'Показываем количество сообщений, но не даём прочитать все',
                    'conversion': '60-80%',
                    'viral_coefficient': '1-2'
                },
                'referral_rewards': {
                    'name': 'Награды за рефералов',
                    'description': 'Пригласи 5 друзей = бесплатное чтение',
                    'conversion': '30-50%',
                    'viral_coefficient': '5-10'
                }
            },
            'tarot': {
                'shareable_results': {
                    'name': 'Делимые результаты',
                    'description': 'Красивая картинка с результатом гадания',
                    'conversion': '40-60%',
                    'viral_coefficient': '2-3'
                },
                'daily_horoscope_channel': {
                    'name': 'Канал с гороскопами',
                    'description': 'Ежедневные посты привлекают подписчиков',
                    'conversion': '10-20%',
                    'viral_coefficient': '1-2'
                },
                'friend_readings': {
                    'name': 'Гадания для друзей',
                    'description': 'Погадай другу - оба получите бонус',
                    'conversion': '50-70%',
                    'viral_coefficient': '2-4'
                }
            },
            'memes': {
                'watermark': {
                    'name': 'Водяной знак',
                    'description': 'Мемы с логотипом бота распространяются сами',
                    'conversion': '20-30%',
                    'viral_coefficient': '5-10'
                },
                'group_orders': {
                    'name': 'Групповые заказы',
                    'description': 'Мемы для всей компании со скидкой',
                    'conversion': '60-80%',
                    'viral_coefficient': '5-15'
                },
                'meme_challenges': {
                    'name': 'Мем-челленджи',
                    'description': 'Конкурсы на лучший мем с призами',
                    'conversion': '30-50%',
                    'viral_coefficient': '10-20'
                }
            }
        }
        
        return mechanics.get(project, {})
    
    def calculate_viral_growth(self, initial_users: int, days: int, viral_coefficient: float = 2.0) -> List[int]:
        """
        Расчёт вирусного роста пользователей
        
        Args:
            initial_users: Начальное количество пользователей
            days: Количество дней
            viral_coefficient: Коэффициент вирусности (сколько новых пользователей приводит 1 пользователь)
        
        Returns:
            Список количества пользователей по дням
        """
        users_by_day = [initial_users]
        current_users = initial_users
        
        for day in range(1, days + 1):
            # Каждый день часть пользователей приводит новых
            active_users = current_users * 0.3  # 30% активных пользователей
            new_users = int(active_users * viral_coefficient * 0.1)  # 10% конверсия в день
            current_users += new_users
            users_by_day.append(current_users)
        
        return users_by_day
    
    def estimate_revenue(self, users: int, project: str) -> float:
        """
        Оценка дохода на основе количества пользователей
        """
        conversion_rates = {
            'confessions': 0.15,  # 15% платят
            'tarot': 0.20,  # 20% платят
            'memes': 0.10  # 10% платят
        }
        
        average_check = {
            'confessions': 199,  # средний чек
            'tarot': 150,
            'memes': 99
        }
        
        conversion = conversion_rates.get(project, 0.1)
        check = average_check.get(project, 100)
        
        paying_users = users * conversion
        revenue = paying_users * check
        
        return revenue
    
    def get_marketing_plan_no_budget(self) -> Dict:
        """
        План маркетинга БЕЗ бюджета (только органика)
        """
        return {
            'day_1_3': {
                'actions': [
                    'Расскажи о боте 10 друзьям лично',
                    'Опубликуй в своих соцсетях (VK, Instagram, Telegram)',
                    'Попроси друзей поделиться',
                    'Запости в 3-5 тематических группах Telegram'
                ],
                'expected_users': '20-50',
                'expected_revenue': '0-1,000₽'
            },
            'day_4_7': {
                'actions': [
                    'Активируй реферальную программу',
                    'Создай Telegram-канал с контентом (гороскопы/мемы)',
                    'Участвуй в обсуждениях на форумах с упоминанием бота',
                    'Попроси первых пользователей оставить отзывы'
                ],
                'expected_users': '100-300',
                'expected_revenue': '3,000-10,000₽'
            },
            'day_8_14': {
                'actions': [
                    'Вирусный эффект начинает работать',
                    'Пользователи сами приводят друзей',
                    'Оптимизируй конверсию на основе данных',
                    'Добавь новые фичи по запросам пользователей'
                ],
                'expected_users': '500-2,000',
                'expected_revenue': '15,000-50,000₽'
            },
            'day_15_18': {
                'actions': [
                    'Масштабирование через сарафанное радио',
                    'Партнёрства с другими ботами (бартер)',
                    'Запуск конкурсов и челленджей',
                    'Активная работа с сообществом'
                ],
                'expected_users': '2,000-5,000',
                'expected_revenue': '50,000-100,000₽'
            }
        }
    
    def get_content_ideas(self, project: str) -> List[str]:
        """
        Идеи контента для органического продвижения
        """
        ideas = {
            'confessions': [
                'Подборка самых смешных анонимных признаний (с согласия)',
                'Истории: "Что мне написали анонимно"',
                'Советы: "Как реагировать на анонимные признания"',
                'Мемы про анонимность и признания',
                'Опросы: "Ты бы хотел узнать, кто написал?"'
            ],
            'tarot': [
                'Ежедневные гороскопы для всех знаков',
                'Разбор значений карт Таро',
                'Истории: "Как Таро изменило мою жизнь"',
                'Советы астролога на неделю',
                'Интересные факты об астрологии'
            ],
            'memes': [
                'Подборка лучших мемов недели',
                'Мем-челленджи с призами',
                'Обучение: "Как создать вирусный мем"',
                'Тренды мемов 2025',
                'Мемы про актуальные события'
            ]
        }
        
        return ideas.get(project, [])

# Глобальный экземпляр
marketing = AutoMarketing()

# Пример использования
if __name__ == "__main__":
    # Расчёт вирусного роста
    growth = marketing.calculate_viral_growth(initial_users=10, days=18, viral_coefficient=2.5)
    print("📈 Прогноз роста пользователей:")
    for day, users in enumerate(growth):
        if day == 0:
            print(f"День 0 (старт): {users} пользователей")
        else:
            revenue_conf = marketing.estimate_revenue(users, 'confessions')
            revenue_tarot = marketing.estimate_revenue(users, 'tarot')
            revenue_memes = marketing.estimate_revenue(users, 'memes')
            total_revenue = revenue_conf + revenue_tarot + revenue_memes
            print(f"День {day}: {users} пользователей | Доход: {total_revenue:.0f}₽")
    
    print("\n💰 Итоговый прогноз за 18 дней:")
    final_users = growth[-1]
    final_revenue = (
        marketing.estimate_revenue(final_users, 'confessions') +
        marketing.estimate_revenue(final_users, 'tarot') +
        marketing.estimate_revenue(final_users, 'memes')
    )
    print(f"Пользователей: {final_users}")
    print(f"Доход: {final_revenue:.0f}₽")

