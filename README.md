
# Astro Freemium Bot — Render-Ready (RU UI, No External AI)

Freemium Telegram bot (astro-psychology & numerology) with **Russian UI** and **auto mode**.
- If `WEBHOOK_BASE` is set → webhook; else → polling.
- No third‑party AI.

## Deploy on Render
1) Upload to GitHub.
2) Render → New → Web Service → select repo (auto-detects `render.yaml`).
3) In Render UI set `TELEGRAM_BOT_TOKEN` (others are prefilled).
4) First run works in polling. After URL appears, add `WEBHOOK_BASE=https://<your>.onrender.com` → restart.

## Commands
/start, /help, /energy, /compat, /ask
