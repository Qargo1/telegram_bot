from extensions import CurrencyValue, APIException
import telebot

# Импортируем токен
from main_helper import TOKEN


# Инициализация
cv = CurrencyValue()
bot = telebot.TeleBot(TOKEN)  # Замените на ваш токен
users_started = set()
        
# Обработчики команд
@bot.message_handler(commands=['start'])
def start(message):
    users_started.add(message.chat.id)
    bot.reply_to(
        message, 
        "Привет! Для конвертации введите:\n"
        "<валюта1>, <валюта2>, <количество>\n"
        "Например: Доллар США, Рубль, 100\n"
        "Используйте /help для получения справки.\n"
        "Используйте /values для получения справки.\n"
        )

@bot.message_handler(commands=['values'])
def values(message):
    currencies = cv.get_currency_list()
    bot.reply_to(message, f"Доступные валюты:\n{currencies}")

@bot.message_handler(commands=['help'])
def help(message):
    bot.reply_to(
        message, 
        "Инструкция:\n"
        "1. /start - начать работу\n"
        "2. /values - список валют\n"
        "3. <валюта1> <валюта2> <количество> - конвертация"
        )

# Обработка текстовых сообщений
@bot.message_handler(content_types=['text'])
def convert(message):
    if message.chat.id not in users_started:
        bot.reply_to(message, "Для начала работы введите /start")
        return

    try:
        parts = message.text.split(', ')
        if len(parts) != 3:
            raise APIException("Неверный формат запроса")

        base_currency, target_currency, amount_str = parts
        amount = cv.safe_float(amount_str)
        
        result = cv.convert_currency(base_currency, target_currency, amount)
        bot.reply_to(message, f"{amount} {base_currency} = {result} {target_currency}")

    except APIException as e:
        bot.reply_to(message, f"Ошибка: {e}")
    except Exception as e:
        bot.reply_to(message, f"Неизвестная ошибка: {str(e)}")

# Запуск бота
if __name__ == "__main__":
    bot.polling(none_stop=True)