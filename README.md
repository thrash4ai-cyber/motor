
# Astro Freemium Bot (Telegram) — Webhook, Russian UI, No External AI

A self-contained Telegram **freemium** bot (astro-psychology / numerology) with **Russian interface** and **webhook mode** for **free cloud deploy** (Render.com example).  
**No external AI**. Heuristic logic only.

## Why webhook?
Webhooks let Telegram push updates to your hosted endpoint. This means you can deploy to a free web service (e.g., Render.com) without running anything locally.

---

## ✳️ Quick Deploy on Render.com (Free)
**No local PC required.** You only need a GitHub account.

1) **Create a GitHub repo** and upload project files as-is (or use GitHub UI to create files).  
2) Go to **Render.com → New → Web Service**.  
   - Connect your GitHub repo.  
   - **Environment**: Python 3.11  
   - **Build Command**: `pip install -r requirements.txt`  
   - **Start Command**: `python bot.py`  
3) Set **Environment Variables** in Render:
   - `TELEGRAM_BOT_TOKEN` = `123456:ABC...` (from @BotFather)
   - `MODE` = `webhook`
   - `WEBHOOK_BASE` = `https://your-service.onrender.com` (Render URL after create)
   - `TIMEZONE` = `Asia/Almaty`
   - `DAILY_FREE_LIMIT` = `3`
   - (optional) `PLUS_URL`, `CONSULT_URL`
4) Deploy. Render gives you a public URL like `https://your-service.onrender.com`.  
   The bot sets the webhook automatically at `WEBHOOK_BASE + "/webhook/" + TOKEN` on startup.
5) Open Telegram and send `/start` to your bot.

> Render free tier may sleep when idle. Telegram will wake it with the next webhook call.

---

## 🇷🇺 Интерфейс (Russian UI)

Команды:
- `/start` — приветствие и меню
- `/energy` — «Энергия дня» по дате рождения (кратко)
- `/compat` — быстрая совместимость двух дат (оценка + риск + совет)
- `/ask` — один короткий вопрос → 3 маркера (без глубины)
- `/help` — помощь

Лимиты фри-уровня: 3 запроса на 24 часа на пользователя.  
Апсейл: ссылки на Plus и Консультации (замените `PLUS_URL` / `CONSULT_URL` в `.env`).

---

## Local (Optional)
If you ever need to run locally:
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
export TELEGRAM_BOT_TOKEN=XXX
export MODE=polling
python bot.py
```

---

## Files
```
.
├─ bot.py
├─ utils/
│  ├─ numerology.py
│  ├─ astrology.py
│  ├─ storage.py
│  ├─ texts.py        # Russian UI strings
├─ requirements.txt
├─ config.example.env
├─ Dockerfile         # Optional container deploy
├─ LICENSE
└─ README.md
```

---

## Env Vars
- `TELEGRAM_BOT_TOKEN` — token from @BotFather
- `MODE` — `webhook` or `polling` (default: `webhook`)
- `WEBHOOK_BASE` — public base URL for webhook (e.g., Render URL)
- `TIMEZONE` — IANA tz (default: `Asia/Almaty`)
- `DAILY_FREE_LIMIT` — free requests per 24h (default: 3)
- `PLUS_URL` / `CONSULT_URL` — your upsell links

---

## License
MIT
