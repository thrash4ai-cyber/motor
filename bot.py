
import os
from datetime import datetime, timedelta
import logging
import pytz
from dotenv import load_dotenv

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, ConversationHandler, filters, ContextTypes

from utils.storage import init_db, ensure_user, get_usage, set_usage, log_event
from utils.numerology import parse_date, energy_of_day, compatibility_score
from utils.astrology import zodiac_sign
from utils import texts

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TZ = os.getenv("TIMEZONE", "Asia/Almaty")
DAILY_FREE_LIMIT = int(os.getenv("DAILY_FREE_LIMIT", "3"))
MODE = os.getenv("MODE", "auto").lower()  # auto | polling | webhook
WEBHOOK_BASE = os.getenv("WEBHOOK_BASE", "").rstrip("/")
PORT = int(os.getenv("PORT", "8000"))

if not TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN is not set.")

tz = pytz.timezone(TZ)

ASK_BIRTH, ASK_COMPAT, ASK_QUESTION = range(1,4)

def now_local(): return datetime.now(tz)

def usage_ok(user_id: int) -> bool:
    row = get_usage(user_id); now = datetime.utcnow()
    if not row:
        set_usage(user_id, now.isoformat(), 0); return True
    window_start_iso, count = row
    try: ws = datetime.fromisoformat(window_start_iso)
    except Exception: ws = now
    if now - ws >= timedelta(hours=24):
        set_usage(user_id, now.isoformat(), 0); return True
    return count < DAILY_FREE_LIMIT

def bump_usage(user_id: int):
    row = get_usage(user_id); now = datetime.utcnow()
    if not row:
        set_usage(user_id, now.isoformat(), 1)
    else:
        window_start_iso, count = row
        try: ws = datetime.fromisoformat(window_start_iso)
        except Exception: ws = now
        if now - ws >= timedelta(hours=24):
            set_usage(user_id, now.isoformat(), 1)
        else:
            set_usage(user_id, window_start_iso, count + 1)

def menu_keyboard():
    return ReplyKeyboardMarkup([[KeyboardButton("/energy"), KeyboardButton("/compat")],
                                [KeyboardButton("/ask"), KeyboardButton("/help")]], resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ensure_user(update.effective_user.id)
    await update.message.reply_text(texts.WELCOME + "\n\nВыбери: /energy | /compat | /ask | /help", reply_markup=menu_keyboard())

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(texts.HELP, reply_markup=menu_keyboard())

async def energy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not usage_ok(update.effective_user.id):
        await update.message.reply_text(texts.LIMIT_HIT); return ConversationHandler.END
    await update.message.reply_text(texts.ASK_DATE); return ASK_BIRTH

async def energy_calc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    d = parse_date(update.message.text)
    if not d:
        await update.message.reply_text(texts.INVALID_DATE); return ASK_BIRTH
    e = energy_of_day(d, now_local().date()); sign = zodiac_sign(d)
    bump_usage(user_id); log_event(user_id, "energy", update.message.text)
    text = (f"Путь жизни: {e['life_path']} | День: {e['day_num']} | Сумма: {e['mix']}\n"
            f"Знак: {sign}\nФокус: {e['meaning']}\n\n(Полный разбор — в Plus.)\n{texts.CTA}")
    await update.message.reply_text(text, reply_markup=menu_keyboard()); return ConversationHandler.END

async def compat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not usage_ok(update.effective_user.id):
        await update.message.reply_text(texts.LIMIT_HIT); return ConversationHandler.END
    await update.message.reply_text(texts.ASK_TWO_DATES); return ASK_COMPAT

def _split_two_dates(text: str):
    parts = [p.strip() for p in text.replace(",", " ").split() if p.strip()]
    if len(parts) != 2: return None, None
    from utils.numerology import parse_date as pd
    return pd(parts[0]), pd(parts[1])

async def compat_calc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    d1, d2 = _split_two_dates(update.message.text)
    if not d1 or not d2:
        await update.message.reply_text(texts.INVALID_TWO_DATES); return ASK_COMPAT
    sc = compatibility_score(d1, d2); bump_usage(user_id); log_event(user_id, "compat", update.message.text)
    text = (f"Пути жизни: {sc['lp1']} & {sc['lp2']}\nБыстрая гармония: {sc['score']}/100\n"
            f"Риск: {sc['risk']}\nСовет: {sc['tip']}\n\n(Глубокая совместимость — в Plus.)\n{texts.CTA}")
    await update.message.reply_text(text, reply_markup=menu_keyboard()); return ConversationHandler.END

async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not usage_ok(update.effective_user.id):
        await update.message.reply_text(texts.LIMIT_HIT); return ConversationHandler.END
    await update.message.reply_text(texts.ASK_QUESTION); return ASK_QUESTION

def _sanitize_question(q: str) -> str: return (q or "").strip()[:200]

async def ask_calc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    q = _sanitize_question(update.message.text)
    if not q:
        await update.message.reply_text(texts.ASK_QUESTION); return ASK_QUESTION
    bump_usage(user_id); log_event(user_id, "ask", q)
    bullets = [
        "1) Сформулируй желаемый итог одним предложением; без смешанных сигналов 48 часов.",
        "2) Выбери один конкретный шаг на 24 часа; пусть он будет обратимым и малорисковым.",
        "3) Коммуницируй размеренно; задай один открытый вопрос и дай тишине сработать."
    ]
    text = f"Твой вопрос: «{q}»\n\n" + "\n".join(bullets) + "\n\n(Точный тайминг — в Plus.)\n" + texts.CTA
    await update.message.reply_text(text, reply_markup=menu_keyboard()); return ConversationHandler.END

async def fallback_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(texts.FALLBACK, reply_markup=menu_keyboard())

def build_app():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(ConversationHandler(entry_points=[CommandHandler("energy", energy)], states={ASK_BIRTH:[MessageHandler(filters.TEXT & ~filters.COMMAND, energy_calc)]}, fallbacks=[CommandHandler("start", start)]))
    app.add_handler(ConversationHandler(entry_points=[CommandHandler("compat", compat)], states={ASK_COMPAT:[MessageHandler(filters.TEXT & ~filters.COMMAND, compat_calc)]}, fallbacks=[CommandHandler("start", start)]))
    app.add_handler(ConversationHandler(entry_points=[CommandHandler("ask", ask)], states={ASK_QUESTION:[MessageHandler(filters.TEXT & ~filters.COMMAND, ask_calc)]}, fallbacks=[CommandHandler("start", start)]))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, fallback_text))
    return app

def main():
    init_db()
    app = build_app()
    effective_mode = MODE if MODE in ("polling","webhook") else ("webhook" if WEBHOOK_BASE else "polling")
    if effective_mode == "polling":
        logger.info("Starting in POLLING mode (auto/failsafe).")
        app.run_polling()
    else:
        url_path = f"/webhook/{TOKEN}"
        webhook_url = (WEBHOOK_BASE or "").rstrip("/") + url_path
        try:
            if not WEBHOOK_BASE:
                raise RuntimeError("WEBHOOK_BASE missing in webhook mode")
            logger.info(f"Starting in WEBHOOK mode on port {PORT}, url_path={url_path}, webhook_url={webhook_url}")
            app.run_webhook(listen="0.0.0.0", port=PORT, url_path=url_path, webhook_url=webhook_url)
        except Exception as e:
            logger.error(f"Webhook failed ({e}); falling back to POLLING.")
            app.run_polling()

if __name__ == "__main__":
    main()
