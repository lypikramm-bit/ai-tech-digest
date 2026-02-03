import os
import requests
import asyncio
from datetime import datetime
from telegram import Bot
import random

class FreeAITechAgent:
    def __init__(self):
        self.bot = Bot(token=os.environ["TELEGRAM_BOT_TOKEN"])
        self.channel_id = os.environ["TELEGRAM_CHANNEL_ID"]
        self.unsplash_key = os.environ["UNSPLASH_ACCESS_KEY"]
    
    async def fetch_news(self):
        news = []
        
        try:
            hn_ids = requests.get("https://hacker-news.firebaseio.com/v0/topstories.json").json()[:5]
            for hn_id in hn_ids:
                item = requests.get(f"https://hacker-news.firebaseio.com/v0/item/{hn_id}.json").json()
                if item and item.get("type") == "story" and item.get("url") and "github" not in item["url"].lower():
                    news.append({"title": item["title"], "url": item["url"], "source": "HN"})
        except:
            pass
        
        try:
            reddit = requests.get(
                "https://www.reddit.com/r/artificial/top.json?t=day",
                headers={"User-agent": "AITechBot/1.0"}
            ).json()
            for post in reddit["data"]["children"][:3]:
                data = post["data"]
                if not data["is_self"]:
                    news.append({"title": data["title"], "url": data["url"], "source": "Reddit"})
        except:
            pass
        
        return news[:4]
    
    async def generate_text(self, news_items):
        news_list = "\n".join([f"• {item['title']} [{item['source']}]({item['url']})" for item in news_items])
        
        prompt = f"""Ты — эксперт по ИИ, ведёшь Telegram-канал для аудитории 20-45 лет. Напиши пост на русском языке (250-350 слов) на основе этих новостей:

{news_list}

Правила:
1. Заголовок: цепляющий с эмодзи 🤖⚡🧠
2. Основная часть: 2-3 ключевые новости с кратким объяснением сути
3. Блок «Зачем это знать»: почему это важно для разработчиков/бизнеса/обычных людей
4. Заключение: лёгкий прогноз или вопрос для размышления (без требования ответа)
5. Стиль: экспертный, но без занудства, с лёгкой иронией
6. Форматирование: короткие абзацы (1-2 предложения), эмодзи для разделения блоков, жирный шрифт для акцентов через **текст**"""

        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.environ['GROQ_API_KEY']}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.1-70b-versatile",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 600,
                "temperature": 0.8
            },
            timeout=30
        )
        return response.json()["choices"][0]["message"]["content"]
    
    async def get_image(self, news_items):
        queries = ["artificial intelligence", "neural network", "robotics", "data science", "futuristic technology"]
        query = random.choice(queries)
        
        try:
            img = requests.get(
                "https://api.unsplash.com/photos/random",
                params={"query": query, "orientation": "landscape", "client_id": self.unsplash_key},
                timeout=10
            ).json()
            return img["urls"]["regular"]
        except:
            return "https://picsum.photos/1200/630"
    
    async def publish(self):
        print(f"🚀 Запуск агента: {datetime.now()}")
        
        news = await self.fetch_news()
        if not news:
            print("❌ Не удалось собрать новости")
            return
        
        print(f"✅ Новостей собрано: {len(news)}")
        
        text = await self.generate_text(news)
        print(f"✅ Текст сгенерирован ({len(text)} символов)")
        
        image_url = await self.get_image(news)
        print(f"🖼️ Изображение: {image_url[:50]}...")
        
        try:
            await self.bot.send_photo(
                chat_id=self.channel_id,
                photo=image_url,
                caption=text[:1024],
                parse_mode="MarkdownV2"
            )
            if len(text) > 1024:
                await asyncio.sleep(2)
                await self.bot.send_message(
                    chat_id=self.channel_id,
                    text=text[1024:],
                    parse_mode="MarkdownV2",
                    disable_web_page_preview=True
                )
            print(f"✅ Пост опубликован в {self.channel_id}")
        except Exception as e:
            print(f"❌ Ошибка публикации: {e}")
            try:
                await self.bot.send_message(
                    chat_id=self.channel_id,
                    text=text,
                    disable_web_page_preview=False
                )
                print("✅ Пост опубликован без форматирования")
            except Exception as e2:
                print(f"❌ Полная ошибка: {e2}")

if __name__ == "__main__":
    asyncio.run(FreeAITechAgent().publish())
