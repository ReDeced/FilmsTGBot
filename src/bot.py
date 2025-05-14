import telebot
import json
from gigachat import GigaChat
from gigachat.models import Chat, Messages, MessagesRole


system_prompt = 'Напиши список из нескольких фильмов (по умолчанию 3) по следующему запросу: {message}. ' +\
    'Формат ответа: {"films": [{"author": "Автор фильма", "name": "Название фильма"}], ' +\
    '"response_error": {"status": "false", "message": "текст ошибки"}} ' +\
    'Если ты не можешь создать ДОСТОВЕРНЫЙ список по запросу, или запрос не по теме, то ответ будет следующим: ' +\
    '{"response_error": {"status": "true", "message": "текст ошибки"}} ' +\
    'ПОМНИ, ЧТО ОТВЕТ ЭТО ТОЛЬКО ТЕКСТ В ФОРМАТЕ JSON БЕЗ ЛИШНИХ СИМВОЛОВ'


class Bot:
    def __init__(self, bot_token, auth_key):
        self.bot = telebot.TeleBot(bot_token)
        self.credentials = auth_key

        self.handle_start()
        self.handle_message()

        self.bot.infinity_polling()

    def handle_start(self):
        @self.bot.message_handler(commands=['help', 'start'])
        def send_welcome(message):
            self.bot.reply_to(message, """\
        Привет, я буду составлять тебе список фильмов к просмотру, по твоему запросу. Пример:\nФильмы для просмотра всей семьей\
        """)

    def handle_message(self):
        @self.bot.message_handler(func=lambda message: True)
        def echo_message(message):
            delete_message = self.bot.send_message(message.chat.id, "Обрабатываю ваш зарос")
            with GigaChat(credentials=self.credentials,verify_ssl_certs=False, model="GigaChat-2-Max") as gigachat:
                prompt = system_prompt
                payload = Chat(
                    messages=[
                        Messages(
                            role=MessagesRole.SYSTEM,
                            content=prompt
                        ),
                        Messages(
                            role=MessagesRole.USER,
                            content=f'message = {message.text}'
                        )
                    ],
                    temperature=0.7
                )
                response = gigachat.chat(payload)
                try:
                    response = response.choices[0].message.content
                    response = json.loads(response)
                    err = False
                    for key in response:
                        if key == "response_error":
                            err = True
                    if err:
                        self.bot.reply_to(message, response["response_error"]["message"])
                    else:
                        response_message = ""
                        for film in response["films"]:
                            name = "БЕЗ НАЗВАНИЯ"
                            author = "НЕИЗВЕСТЕН"
                            for key in film:
                                if key.lower() == "name":
                                    name = film[key]
                                elif key.lower() == "author":
                                    author = film[key]
                            response_message += f'• {film["name"]} — {film["author"]}\n'
                        self.bot.reply_to(message, response_message)
                except Exception as e:
                    print(prompt)
                    print(response)
                    print(e)
                    self.bot.reply_to(message, "Ошибка, попробуйте ещё раз немного позже")

            self.bot.delete_message(delete_message.chat.id, delete_message.id)
