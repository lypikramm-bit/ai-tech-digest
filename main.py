import os
import requests
import asyncio
from datetime import datetime
from telegram import Bot
import random
import traceback

class FreeAITechAgent:
    def __init__(self):
        self.bot = Bot(token=os.environ["TELEGRAM_BOT_TOKEN"])
        self.channel_id = os.environ["TELEGRAM_CHANNEL_ID"]
        self.unsplash_key = os.environ["UNSPLASH_ACCESS_KEY"]
    
    async def generate_text(self):
        # Темы под вашу нишу
        topics = [
            "бесплатные сервисы генерации видео",
            "заработок на промптах для Midjourney",
            "промпты для ИИ-ассистентов",
            "лайфхаки генерации изображений",
            "как бесплатно генерировать 100 изображений в день",
            "реальные кейсы заработка на ИИ без вложений",
            "скрытые фичи Leonardo.ai и Playground AI",
            "как продавать промпты и зарабатывать $300/мес",
            "бесплатные аналоги Midjourney которые работают",
            "как создать вирусный мем за 60 секунд с ИИ"
        ]
        topic = random.choice(topics)
        
        prompt = f"""Ты — крутой друг-айтишник, который делится лайфхаками про ИИ в стиле коротких, живых постов для Telegram.

Тема: {topic}

Правила ЖЁСТКО:
✅ Пиши как живой человек: коротко, с юмором, без заумностей
✅ Длина: 90-150 слов. НИКАКОЙ ВОДЫ. Каждая строка = польза.
✅ Структура:
   - Заголовок с эмодзи 🔥/💸/⚡/🤖 (цепляющий, как кликбейт)
   - 1 строка — боль аудитории ("Устал платить за Midjourney?")
   - 3-4 пункта с лайфхаками/сервисами (каждый с эмодзи)
   - В конце: короткий призыв + ссылка на бесплатный сервис
✅ Стиль:
   - Разговорный язык ("братан", "чувак", "лайфхак", "забей")
   - Эмодзи в начале КАЖДОГО пункта (💰 🎨 🤯 🚀)
   - Жирный шрифт **только** для ключевых слов (сервисов, сумм)
   - Короткие строки (макс 1 предложение)
✅ Темы: генерация видео/изображений, заработок на ИИ, промпты, лайфхаки, бесплатные сервисы
✅ ЗАПРЕЩЕНО: длинные предложения, формальный тон, "Вы", "Ваш", "профессионал", "следует отметить" """

        print(f"🧠 Генерирую пост на тему: {topic}")
        
        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {os.environ['GROQ_API_KEY']}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.1-8b-instant",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 350,
                    "temperature": 1.0  # Больше креатива!
                },
                timeout=30
            )
            
            if response.status_code != 200:
                print(f"❌ Groq error {response.status_code}: {response.text[:200]}")
                return self._fallback_post()
            
            text = response.json()["choices"][0]["message"]["content"]
            return self._clean_text(text)
            
        except Exception as e:
            print(f"⚠️ Ошибка генерации текста: {e}")
            return self._fallback_post()
    
    def _clean_text(self, text):
        """Убираем формальное форматирование, оставляем живой текст"""
        # Убираем звёздочки для жирного шрифта (оставляем только для ключевых слов)
        text = text.replace("**", "*").replace("*", "")
        # Убираем лишние отступы и пустые строки
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        return "\n".join(lines[:12])  # Макс 12 строк
    
    def _fallback_post(self):
        """Заготовленный пост на случай ошибки"""
        return """🔥 Midjourney без бабла? Легко!

Устал платить $10 за генерацию?

✅ Leonardo.ai — 150 генераций бесплатно при регистрации
✅ Playground AI — 1000 изображений/день без карты
✅ Bing Image Creator — безлимит через аккаунт Microsoft

Лайфхак: зарегистрируйся во всех трёх — получишь 2000+ бесплатных генераций в месяц 🚀

👉 https://leonardo.ai"""
    
    async def get_image(self):
        """Подбираем ТОЛЬКО релевантные картинки (никаких автомобилей!)"""
        queries = [
            "digital art creation", "ai generated artwork", "neural network visualization",
            "online income", "side hustle laptop", "creative technology",
            "prompt engineering", "digital creator workspace", "money online",
            "abstract technology", "futuristic interface", "creative coding"
        ]
        query = random.choice(queries)
        
        try:
            print(f"🖼️ Запрашиваю картинку: '{query}'")
            img = requests.get(
                "https://api.unsplash.com/photos/random",
                params={
                    "query": query,
                    "orientation": "landscape",
                    "client_id": self.unsplash_key
                },
                timeout=10
            ).json()
            url = img["urls"]["regular"]
            print(f"✅ Картинка получена: {url[:60]}...")
            return url
        except Exception as e:
            print(f"⚠️ Ошибка Unsplash: {e}")
            # Фолбэк: абстрактная технологичная картинка
            return "https://images.unsplash.com/photo-1677234558153-bf5ce094bad4?w=1200&h=630&fit=crop"
    
    async def publish(self):
        print(f"🚀 Запуск агента: {datetime.now()}")
        
        try:
            # 1. Генерируем текст
            text = await self.generate_text()
            print(f"✅ Текст готов:\n---\n{text}\n---")
            
            # 2. Получаем релевантную картинку
            image_url = await self.get_image()
            
            # 3. Публикуем картинку БЕЗ текста (чтобы не обрезалось)
            await self.bot.send_photo(
                chat_id=self.channel_id,
                photo=image_url
            )
            print("✅ Картинка опубликована")
            
            # 4. Отправляем текст отдельным сообщением (без ограничения 1024 символа)
            await asyncio.sleep(1)
            await self.bot.send_message(
                chat_id=self.channel_id,
                text=text,
                parse_mode=None
            )
            print(f"✅ Текст опубликован в {self.channel_id}")
            
        except Exception as e:
            print(f"❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
            print(traceback.format_exc())
            # Фолбэк: публикуем хотя бы текст
            await self.bot.send_message(
                chat_id=self.channel_id,
                text=self._fallback_post(),
                parse_mode=None
            )
            print("✅ Фолбэк-пост опубликован")

if __name__ == "__main__":
    asyncio.run(FreeAITechAgent().publish())
