import os
import requests
import asyncio
from datetime import datetime
from telegram import Bot
import random
import traceback
import json

class FreeAITechAgent:
    def __init__(self):
        self.bot = Bot(token=os.environ["TELEGRAM_BOT_TOKEN"])
        self.channel_id = os.environ["TELEGRAM_CHANNEL_ID"]
        self.unsplash_key = os.environ["UNSPLASH_ACCESS_KEY"]
        self.groq_key = os.environ["GROQ_API_KEY"]
    
    async def fetch_news(self):
        news = []
        
        try:
            hn_ids = requests.get("https://hacker-news.firebaseio.com/v0/topstories.json", timeout=10).json()[:5]
            for hn_id in hn_ids:
                try:
                    item = requests.get(f"https://hacker-news.firebaseio.com/v0/item/{hn_id}.json", timeout=5).json()
                    if item and item.get("type") == "story" and item.get("url") and "github" not in item["url"].lower():
                        news.append({"title": item["title"], "url": item["url"], "source": "HN"})
                except:
                    continue
        except:
            pass
        
        return news[:3]
    
    async def generate_text(self, news_items):
        news_list = "\n".join([f"- {item['title']} ({item['source']})" for item in news_items])
        
        prompt = f"""Напиши короткий пост на русском языке (200-300 слов) для Telegram-канала про ИИ. Аудитория 20-45 лет.

Новости дня:
{news_list}

Правила:
1. Заголовок с эмодзи 🤖
2. Кратко опиши 2 новости
3. Добавь блок "Почему это важно"
4. Стиль: просто, без жаргона, с лёгкой иронией
5. Не используй **жирный шрифт**, не используй сложное форматирование"""

        print(f"📡 Отправляю запрос к Groq API...")
        
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self.groq_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.1-8b-instant",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 500,
                "temperature": 0.7
            },
            timeout=30
        )
        
        print(f"📡 Статус ответа Groq: {response.status_code}")
        print(f"📡 Тело ответа: {response.text[:500]}")  # Показываем первые 500 символов
        
        if response.status_code != 200:
            raise Exception(f"Groq API error {response.status_code}: {response.text}")
        
        return response.json()["choices"][0]["message"]["content"]
    
    async def get_image(self):
        queries = ["artificial intelligence", "neural network", "futuristic technology"]
        query = random.choice(queries)
        
        try:
            img = requests.get(
                "https://api.unsplash.com/photos/random",
                params={"query": query, "orientation": "landscape", "client_id": self.unsplash_key},
                timeout=10
            ).json()
            return img["urls"]["regular"]
        except Exception as e:
            print(f"⚠️ Ошибка Unsplash: {e}")
            return "https://picsum.photos/1200/630"
    
    async def publish(self):
        print(f"🚀 Запуск агента: {datetime.now()}")
        
        try:
            news = await self.fetch_news()
            print(f"✅ Новостей собрано: {len(news)}")
            if not news:
                print("❌ Нет новостей — прерываем публикацию")
                return
            
            text = await self.generate_text(news)
            print(f"✅ Текст сгенерирован:\n---\n{text[:200]}...\n---")
            
            image_url = await self.get_image()
            print(f"🖼️ Изображение: {image_url}")
            
            await self.bot.send_photo(
                chat_id=self.channel_id,
                photo=image_url,
                caption=text[:1024],
                parse_mode=None
            )
            print(f"✅ Пост опубликован в {self.channel_id}")
            
        except Exception as e:
            print(f"❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
            print(traceback.format_exc())
            raise

if __name__ == "__main__":
    # Проверка наличия всех переменных окружения
    required_vars = ["TELEGRAM_BOT_TOKEN", "TELEGRAM_CHANNEL_ID", "GROQ_API_KEY", "UNSPLASH_ACCESS_KEY"]
    for var in required_vars:
        if not os.environ.get(var):
            print(f"❌ Ошибка: переменная {var} не установлена!")
            exit(1)
        else:
            print(f"✅ Переменная {var} установлена (длина: {len(os.environ.get(var, ''))})")
    
    asyncio.run(FreeAITechAgent().publish())
