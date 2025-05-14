import os
from dotenv import load_dotenv
from src.bot import Bot


def main():
    if not load_dotenv():
        raise RuntimeError("Не удалось загрузить .env файл")

    auth_key = os.getenv('GIGA_AUTH_KEY')

    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')

    bot = Bot(bot_token, auth_key)


if __name__ == "__main__":
    main()