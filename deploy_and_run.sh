#!/bin/bash

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║         🚀 TRIPLE TELEGRAM EMPIRE - AUTO DEPLOY 🚀           ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Проверка зависимостей
echo -e "${YELLOW}📦 Проверка зависимостей...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 не установлен!${NC}"
    exit 1
fi

if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}❌ pip3 не установлен!${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Python3 и pip3 найдены${NC}"
echo ""

# Установка зависимостей
echo -e "${YELLOW}📦 Установка зависимостей...${NC}"
pip3 install -q python-telegram-bot aiohttp sqlalchemy openai pillow 2>/dev/null

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Зависимости установлены${NC}"
else
    echo -e "${RED}❌ Ошибка установки зависимостей${NC}"
    exit 1
fi
echo ""

# Проверка токенов ботов
echo -e "${YELLOW}🔑 Проверка токенов ботов...${NC}"

BOT1_TOKEN=$(grep "BOT_TOKEN = " project1-confessions/bot.py | cut -d'"' -f2)
BOT2_TOKEN=$(grep "BOT_TOKEN = " project2-tarot/bot.py | cut -d'"' -f2)
BOT3_TOKEN=$(grep "BOT_TOKEN = " project3-memes/bot.py | cut -d'"' -f2)

if [ "$BOT1_TOKEN" == "YOUR_BOT_TOKEN_HERE" ] || [ -z "$BOT1_TOKEN" ]; then
    echo -e "${RED}❌ Токен бота 1 (Confessions) не настроен!${NC}"
    echo -e "${YELLOW}💡 Создай бота через @BotFather и вставь токен в project1-confessions/bot.py${NC}"
    exit 1
fi

if [ "$BOT2_TOKEN" == "YOUR_BOT_TOKEN_HERE" ] || [ -z "$BOT2_TOKEN" ]; then
    echo -e "${RED}❌ Токен бота 2 (Tarot) не настроен!${NC}"
    echo -e "${YELLOW}💡 Создай бота через @BotFather и вставь токен в project2-tarot/bot.py${NC}"
    exit 1
fi

if [ "$BOT3_TOKEN" == "YOUR_BOT_TOKEN_HERE" ] || [ -z "$BOT3_TOKEN" ]; then
    echo -e "${RED}❌ Токен бота 3 (Memes) не настроен!${NC}"
    echo -e "${YELLOW}💡 Создай бота через @BotFather и вставь токен в project3-memes/bot.py${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Все токены настроены${NC}"
echo ""

# Остановка старых процессов
echo -e "${YELLOW}🛑 Остановка старых процессов...${NC}"
pkill -f "project1-confessions/bot.py" 2>/dev/null
pkill -f "project2-tarot/bot.py" 2>/dev/null
pkill -f "project3-memes/bot.py" 2>/dev/null
pkill -f "dashboard.py" 2>/dev/null
sleep 2
echo -e "${GREEN}✅ Старые процессы остановлены${NC}"
echo ""

# Создание директорий
echo -e "${YELLOW}📁 Создание директорий...${NC}"
mkdir -p logs
mkdir -p data
echo -e "${GREEN}✅ Директории созданы${NC}"
echo ""

# Запуск ботов
echo -e "${YELLOW}🤖 Запуск ботов...${NC}"

nohup python3 project1-confessions/bot.py > logs/bot1.log 2>&1 &
BOT1_PID=$!
echo -e "${GREEN}✅ Бот 1 (Confessions) запущен (PID: $BOT1_PID)${NC}"

sleep 2

nohup python3 project2-tarot/bot.py > logs/bot2.log 2>&1 &
BOT2_PID=$!
echo -e "${GREEN}✅ Бот 2 (Tarot) запущен (PID: $BOT2_PID)${NC}"

sleep 2

nohup python3 project3-memes/bot.py > logs/bot3.log 2>&1 &
BOT3_PID=$!
echo -e "${GREEN}✅ Бот 3 (Memes) запущен (PID: $BOT3_PID)${NC}"

echo ""

# Запуск дашборда
echo -e "${YELLOW}📊 Запуск веб-дашборда...${NC}"
nohup python3 dashboard.py > logs/dashboard.log 2>&1 &
DASHBOARD_PID=$!
echo -e "${GREEN}✅ Dashboard запущен (PID: $DASHBOARD_PID)${NC}"
echo ""

# Проверка запуска
sleep 3
echo -e "${YELLOW}🔍 Проверка статуса...${NC}"

if ps -p $BOT1_PID > /dev/null; then
    echo -e "${GREEN}✅ Бот 1 работает${NC}"
else
    echo -e "${RED}❌ Бот 1 не запустился. Проверь logs/bot1.log${NC}"
fi

if ps -p $BOT2_PID > /dev/null; then
    echo -e "${GREEN}✅ Бот 2 работает${NC}"
else
    echo -e "${RED}❌ Бот 2 не запустился. Проверь logs/bot2.log${NC}"
fi

if ps -p $BOT3_PID > /dev/null; then
    echo -e "${GREEN}✅ Бот 3 работает${NC}"
else
    echo -e "${RED}❌ Бот 3 не запустился. Проверь logs/bot3.log${NC}"
fi

if ps -p $DASHBOARD_PID > /dev/null; then
    echo -e "${GREEN}✅ Dashboard работает${NC}"
else
    echo -e "${RED}❌ Dashboard не запустился. Проверь logs/dashboard.log${NC}"
fi

echo ""

# Запуск AI Marketing Orchestra
echo -e "${YELLOW}🎭 Запуск AI Marketing Orchestra...${NC}"
python3 ai_marketing_orchestra.py

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║                    ✅ СИСТЕМА ЗАПУЩЕНА! ✅                    ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo -e "${GREEN}📊 Dashboard доступен:${NC} http://$(curl -s ifconfig.me):5000"
echo ""
echo -e "${YELLOW}📋 Полезные команды:${NC}"
echo ""
echo "  Проверить статус:"
echo "    ps aux | grep python"
echo ""
echo "  Посмотреть логи:"
echo "    tail -f logs/bot1.log"
echo "    tail -f logs/bot2.log"
echo "    tail -f logs/bot3.log"
echo "    tail -f logs/dashboard.log"
echo ""
echo "  Остановить всё:"
echo "    pkill -f 'project.*bot.py'"
echo "    pkill -f 'dashboard.py'"
echo ""
echo "  Перезапустить:"
echo "    ./deploy_and_run.sh"
echo ""
echo -e "${GREEN}🎯 Следующие шаги:${NC}"
echo ""
echo "  1. Открой Dashboard в браузере"
echo "  2. Протестируй ботов в Telegram"
echo "  3. Используй созданный маркетинговый контент"
echo "  4. Публикуй в тематических группах"
echo ""
echo -e "${YELLOW}💰 Цель: 60,000₽ за 18 дней${NC}"
echo ""
echo "Удачи! 🚀💰"
echo ""

