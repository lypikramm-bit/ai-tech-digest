import os
import requests
import asyncio
from datetime import datetime
from telegram import Bot
import random
import traceback
import re
import html

class FreeAITechAgent:
    def __init__(self):
        self.bot = Bot(token=os.environ["TELEGRAMOT_TOKEN"])
        self.channel_id = os.environ["TELEGRAM_CHANNEL_ID"]
        self.unsplash_key = os.environ["UNSPLASH_ACCESS_KEY"]
        self.reddit_headers = {"User-agent": "AITechBot/1.0"}
    
    async def fetch_reddit_posts(self):
        """Парсим практичные кейсы"""
        posts = []
        subreddits = [
            ("r/StableDiffusion", "бесплатная генерация"),
            ("r/sidehustle", "монетизация ИИ"),
            ("r/Midjourney", "промпты"),
            ("r/ArtificialIntelligence", "новые сервисы")
        ]
        
        for subreddit, niche in subreddits:
            try:
                url = f"https://www.reddit.com/{subreddit}/top.json?t=week&limit=10"
                response = requests.get(url, headers=self.reddit_headers, timeout=10)
                data = response.json()
                
                for post in data["data"]["children"]:
                    title = post["data"]["title"]
                    score = post["data"]["score"]
                    if score < 80:
                        continue
                    if any(word in title.lower() for word in ["crypto", "nft", "bitcoin", "scam"]):
                        continue
                    if len(title) < 40:
                        continue
                    posts.append({
                        "title": title,
                        "subreddit": subreddit,
                        "score": score
                    })
            except:
                continue
        
        posts.sort(key=lambda x: x["score"], reverse=True)
        return posts[:3]
    
    async def generate_text(self, reddit_posts=None):
        """Генерируем пост с форматированием"""
        
        topics = [
            "бесплатные генераторы изображений 2026",
            "как продавать промпты на маркетплейсах",
            "бесплатные генераторы видео без водяных знаков",
            "как получить образовательную подписку на ИИ-сервисы",
            "бесплатные альтернативы Midjourney",
            "как генерировать 100 изображений в день бесплатно",
            "как создать аккаунт без номера телефона",
            "локальные модели ИИ без интернета"
        ]
        topic = random.choice(topics)
        
        prompt = f"""Ты — эксперт по ИИ. Пиши посты с визуальным форматированием для Telegram.

Тема: {topic}

СТРУКТУРА ПОСТА (ОБЯЗАТЕЛЬНО):
1. Заголовок: <b>Эмодзи + короткий заголовок</b>
2. Описание проблемы: 1 строка без форматирования
3. Секция "Что даёт:" или "Как начать:" с жирными подзаголовками
4. Список из 3-5 пунктов:
   — Каждый пункт начинается с эмодзи
   — Ключевые слова в <b>жирном</b>
   — Дополнительные детали в <i>курсиве</i>
5. Цены/ограничения: через тире, цифры в <b>жирном</b>
6. Ссылка: <a href="URL">короткий текст</a>

ПРАВИЛА ФОРМАТИРОВАНИЯ:
✅ Используй ТОЛЬКО эти теги:
   — <b>текст</b> для акцентов и заголовков
   — <i>текст</i> для дополнительных деталей
   — <a href="URL">текст</a> для ссылок
✅ Экранируй спецсимволы для HTML:
   — &lt; вместо <
   — &gt; вместо >
   — &amp; вместо &
✅ Никаких **звёздочек** или _подчёркиваний_ — только HTML-теги
✅ Максимум 900 символов (чтобы уместилось в подпись к фото)

ПРИМЕР ИДЕАЛЬНОГО ПОСТА:
<b>🎨 Бесплатные генераторы изображений 2026</b>

Устал платить $10 за каждую генерацию?

<b>Что даёт:</b>
🖼️ <b>Leonardo.ai</b> — <i>150 бесплатных генераций</i> при регистрации
🎨 <b>Playground AI</b> — <i>1000 изображений/день</i> без карты
🚀 <b>Bing Image Creator</b> — <i>безлимит</i> через аккаунт Microsoft

<b>Цены:</b>
— Бесплатно: до 150 генераций
— Платно: от $10/мес за ускорение

<i>Лайфхак:</i> зарегистрируйся во всех трёх — получишь 2000+ генераций в месяц

<a href="https://leonardo.ai">Начать с Leonardo.ai</a>"""

        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {os.environ['GROQ_API_KEY']}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.1-70b-versatile",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 500,
                    "temperature": 0.7
                },
                timeout=35
            )
            
            if response.status_code != 200:
                return self._fallback_post()
            
            text = response.json()["choices"][0]["message"]["content"]
            return self._clean_html(text)
            
        except:
            return self._fallback_post()
    
    def _clean_html(self, text):
        """Очищаем и валидируем HTML для Telegram"""
        # Убираем лишние форматирования
        text = text.replace("**", "").replace("__", "").replace("```", "")
        # Экранируем спецсимволы для HTML
        text = html.escape(text, quote=False)
        # Восстанавливаем правильные теги
        text = re.sub(r'&lt;b&gt;(.*?)&lt;/b&gt;', r'<b>\1</b>', text)
        text = re.sub(r'&lt;i&gt;(.*?)&lt;/i&gt;', r'<i>\1</i>', text)
        text = re.sub(r'&lt;a href=&quot;(.*?)&quot;&gt;(.*?)&lt;/a&gt;', r'<a href="\1">\2</a>', text)
        # Убираем запрещённые слова
        text = re.sub(r'(?i)лайфхак[:\s]*', '', text)
        text = re.sub(r'(?i)проверено[:\sа-я0-9]+', '', text)
        # Обрезаем до 900 символов (лимит Telegram для подписи к фото)
        if len(text) > 900:
            text = text[:897] + "..."
        # Фильтруем пустые строки
        lines = [line.rstrip() for line in text.split("\n") if line.strip()]
        return "\n".join(lines[:25])
    
    def _fallback_post(self):
        """Гарантированно хороший пост с форматированием"""
        return """<b>🎨 Бесплатные генераторы изображений 2026</b>

Устал платить $10 за каждую генерацию?

<b>Что даёт:</b>
🖼️ <b>Leonardo.ai</b> — <i>150 бесплатных генераций</i> при регистрации
🎨 <b>Playground AI</b> — <i>1000 изображений/день</i> без карты
🚀 <b>Bing Image Creator</b> — <i>безлимит</i> через аккаунт Microsoft

<b>Цены:</b>
— Бесплатно: до 150 генераций
— Платно: от $10/мес за ускорение

<i>Лайфхак:</i> зарегистрируйся во всех трёх — получишь 2000+ генераций в месяц

<a href="https://leonardo.ai">Начать с Leonardo.ai</a>"""
    
    async def get_image(self):
        """Релевантные картинки"""
        queries = [
            "ai art generation", "digital creativity", "neural network art",
            "creative technology", "prompt engineering", "generative design"
        ]
        query = random.choice(queries)
        
        try:
            img = requests.get(
                "https://api.unsplash.com/photos/random",
                params={"query": query, "orientation": "landscape", "client_id": self.unsplash_key},
                timeout=10
            ).json()
            return img["urls"]["regular"]
        except:
            return "https://images.unsplash.com/photo-1677234558153-bf5ce094bad4?w=1200&h=630&fit=crop"
    
    async def publish(self):
        print(f"🚀 Запуск агента: {datetime.now()}")
        
        try:
            reddit_posts = await self.fetch_reddit_posts()
            print(f"✅ Найдено {len(reddit_posts)} кейсов")
            
            text = await self.generate_text(reddit_posts)
            print(f"✅ Текст:\n---\n{text}\n---")
            
            image_url = await self.get_image()
            print(f"🖼️ Картинка: {image_url[:60]}")
            
            # ОТПРАВЛЯЕМ КАК ОДНО СООБЩЕНИЕ С ИЗОБРАЖЕНИЕМ И ТЕКСТОМ
            await self.bot.send_photo(
                chat_id=self.channel_id,
                photo=image_url,
                caption=text,
                parse_mode="HTML"  # Важно! Для корректного отображения форматирования
            )
            print(f"✅ Пост опубликован в {self.channel_id} (картинка + текст в одном сообщении)")
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            print(traceback.format_exc())
            # Фолбэк: отправка как два сообщения (на всякий случай)
            await self.bot.send_photo(
                chat_id=self.channel_id,
                photo="https://images.unsplash.com/photo-1677234558153-bf5ce094bad4?w=1200&h=630&fit=crop"
            )
            await asyncio.sleep(1)
            await self.bot.send_message(
                chat_id=self.channel_id,
                text=self._fallback_post(),
                parse_mode="HTML"
            )
            print("✅ Фолбэк опубликован (картинка + текст)")

if __name__ == "__main__":
    asyncio.run(FreeAITechAgent().publish())
