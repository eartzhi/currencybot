import telebot
import logging
from extensions import UserInputCheck, Requester, my_formatter
from settings import TOKEN

bot = telebot.TeleBot(TOKEN)

info_logger = logging.getLogger()
info_logger.setLevel(logging.INFO)
info_handler = logging.FileHandler('bot.log', 'w', 'utf-8')
info_handler.setFormatter(my_formatter)
info_logger.addHandler(info_handler)

markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
btn1 = telebot.types.KeyboardButton("EUR RUR")
btn2 = telebot.types.KeyboardButton("USD RUR")
btn3 = telebot.types.KeyboardButton("TRY RUR")
btn4 = telebot.types.KeyboardButton("USD TRY")
btn5 = telebot.types.KeyboardButton("EUR TRY")
markup.add(btn1, btn2, btn3, btn4, btn5)


@bot.message_handler(commands=['start', 'help'])
def rules_getter(message):
    info_logger.info(f'Боту пришло сообщение: "{message.text}"')
    answer = f'Приветствую, {message.from_user.first_name}! ' \
             f'Я помогу тебе перевести валюту по курсу ЦБ. ' \
             f'Введи код валюты, из которой хочешь конвертировать,' \
             f' и код валюты, в которую хочешь конвертировать, через пробел. ' \
             f'Например: EUR USD.При необходимости добавь количество ' \
             f'конвертируемой валюты. Например:  RUR EUR 100. \n' \
             f'Для того, чтобы посмотреть доступные валюты введи /values'
    bot.reply_to(message, answer, reply_markup=markup)
    info_logger.info(f'Бот ответил: "{answer}"')


@bot.message_handler(commands=['values'])
def values_getter(message):                                            # Так как ЦБ меняет курс раз в день,
    info_logger.info(f'Боту пришло сообщение: "{message.text}"')       # можно было бы сохранять запрос один раз в день
    current_table, wrong_input = Requester.get_request()               # и обновлять его только при наступлении следующего дня.
    if wrong_input is None:                                            # Но это пойдет в разрез со смыслом д.з.
        current_list = Requester.currency_list_maker(current_table)    # (работы с запросами как таковой бы не было)
        answer = current_list                                          # поэтому от этой идеи пришлось отказатья.
        bot.reply_to(message, answer, reply_markup=markup)
        info_logger.info(f'Бот ответил: "{answer}"')
    else:
        bot.reply_to(message, wrong_input)
        info_logger.info(f'Бот ответил: "{wrong_input}"')


@bot.message_handler(content_types=['text'])
def exchange_rate(message):
    info_logger.info(f'Боту пришло сообщение: "{message.text}"')
    currency_1, currency_2, quantity, wrong_input = \
        UserInputCheck.first_check(message.text)
    if wrong_input is None:
        current_table, wrong_input = Requester.get_request()
        if wrong_input is None:
            currency1_rate, wrong_input, nominal1 = UserInputCheck.second_check(
                currency_1, current_table)
            if wrong_input is None:
                currency2_rate, wrong_input, nominal2 = \
                    UserInputCheck.second_check(currency_2, current_table)
                if wrong_input is None:
                    answer = str(quantity) + ' ' + currency_1.upper() + ' = ' +\
                             str(round(
                                 ((currency1_rate * nominal2)/
                                  (currency2_rate * nominal1)) * quantity,
                                 2)) \
                             + ' ' + currency_2.upper() + ' по курсу ЦБ'
                    bot.reply_to(message, answer, reply_markup=markup)
                    info_logger.info(f'Бот ответил: "{answer}"')
    if wrong_input:
        bot.reply_to(message, wrong_input, reply_markup=markup)
        info_logger.info(f'Бот ответил: "{wrong_input}"')


bot.infinity_polling()
