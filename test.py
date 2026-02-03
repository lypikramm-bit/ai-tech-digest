import os
import requests

print("🔍 Проверка переменных окружения...")
for var in ["TELEGRAM_BOT_TOKEN", "TELEGRAM_CHANNEL_ID", "GROQ_API_KEY", "UNSPLASH_ACCESS_KEY"]:
    val = os.environ.get(var, "")
    print(f"✅ {var}: {'[СКРЫТО]' if val else '❌ ОТСУТСТВУЕТ'} (длина: {len(val)})")

print("\n📡 Проверка Unsplash API...")
try:
    r = requests.get(
        "https://api.unsplash.com/photos/random",
        params={"query": "technology", "client_id": os.environ["UNSPLASH_ACCESS_KEY"]},
        timeout=10
    )
    if r.status_code == 200:
        print(f"✅ Unsplash работает! Изображение: {r.json()['urls']['regular'][:50]}...")
    else:
        print(f"❌ Unsplash ошибка {r.status_code}: {r.text[:200]}")
except Exception as e:
    print(f"❌ Unsplash exception: {e}")

print("\n🤖 Проверка Groq API (простой запрос)...")
try:
    r = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {os.environ['GROQ_API_KEY']}"},
        json={
            "model": "llama-3.1-8b-instant",
            "messages": [{"role": "user", "content": "Привет"}],
            "max_tokens": 10
        },
        timeout=15
    )
    print(f"Статус: {r.status_code}")
    print(f"Ответ: {r.text[:300]}")
    if r.status_code == 200:
        print("✅ Groq API работает!")
    else:
        print(f"❌ Groq ошибка: {r.text}")
except Exception as e:
    print(f"❌ Groq exception: {e}")

print("\n✅ Все проверки завершены!")
