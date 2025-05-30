# Telegram Trading Bot

A simple Telegram bot for simulating trading sessions.

## Features

- Select trading amount (5$ / 10$)
- Simulated ("fake") market analysis
- Result tracking (win/loss) per user

## Usage

1. Create a bot with [BotFather](https://t.me/BotFather) and get your token.
2. Clone this repository.
3. Install requirements:
   ```
   pip install -r requirements.txt
   ```
4. Edit `trading_bot.py` and put your bot token:
   ```python
   BOT_TOKEN = 'YOUR_BOT_TOKEN'
   ```
5. Run the bot:
   ```
   python trading_bot.py
   ```

## How it works

- Use `/start` to begin.
- Choose your trade amount.
- Type `analyze` for a market analysis.
- After making your trade decision, press "Win ✅" or "Lose ❌" to track your results.

## Notes

- This bot is for educational purposes and does not connect to real markets.
- You can modify the analysis logic in the `analyze` function.
