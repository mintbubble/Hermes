import telebot
from bson import ObjectId
from telebot import types
from telebot.types import ReplyKeyboardRemove
from telegram_bot_pagination import InlineKeyboardPaginator

from conf_info.bot import BOT_TOKEN
from conf_info.bot import SUPPORT
from models import User, Profile
from db.read_data import get_smartlab_data, get_predictions
from db.py_mongo_test import find_document
import datetime
import time

bot = telebot.TeleBot(BOT_TOKEN)
known_users = []

global dataset
global stock

class Command:

    PORTFOLIO = "Портфели"
    RENAME_PORTFOLIO = "Изменить имя портфеля"
    DELETE_PORTFOLIO = "Удалить портфель"
    SELECT_PORTFOLIO = "Выбор портфеля для просмотра"
    UPLOAD_PORTFOLIO = "Загрузить существующий портфель"
    CREATE_PORTFOLIO = "Создать новый портфель"
    CREATE_EMPTY_PORTFOLIO = "Пустой портфель"
    GENERATE_PORTFOLIO = "Сгенерировать портфель"

    STOCK = "Поиск акций"
    MARK_FAVOURITE = "Добавить в избранное"
    REMOVE_STOCK = "Удалить бумагу из портфеля"
    ADD_STOCK = "Добавить в портфель"
    STOCK_INFO = "Посмотреть отчёт"

    FAVOURITE = "Избранное"
    TOP_7_DAYS = "Прогноз на 7 дней"
    SUPPORT = "Поддержка"
    BACK = "Главное меню"


button_base = types.KeyboardButton

buttons = [
    [
        button_base(Command.STOCK),
        button_base(Command.PORTFOLIO),
        button_base(Command.TOP_7_DAYS),
        button_base(Command.SUPPORT),
    ],
    [
        button_base(Command.SELECT_PORTFOLIO),
        button_base(Command.CREATE_PORTFOLIO),
        button_base(Command.BACK),
    ],
    [
        button_base(Command.UPLOAD_PORTFOLIO),
        button_base(Command.CREATE_EMPTY_PORTFOLIO),
        button_base(Command.GENERATE_PORTFOLIO),
        button_base(Command.BACK),
    ],
    [
        button_base(Command.REMOVE_STOCK),
        button_base(Command.RENAME_PORTFOLIO),
        button_base(Command.DELETE_PORTFOLIO),
        button_base(Command.ADD_STOCK),
        button_base(Command.BACK),
    ],
]


def classify_volatility(volatility):

    risk = "Риск: "
    if int(volatility) < 12:
        return risk + "низкий"
    elif int(volatility) > 20:
        return risk + "высокий"
    else:
        return risk + "средний"


@bot.message_handler(commands=["start"])
def send_welcome(message):
    chat_id = str(message.chat.id)
    if message.from_user.username == SUPPORT:
        with open("./conf_info/support.py", "w") as f:
            f.write(f"# chat_id of the support body,\n"
                    f"# rewrites itself automatically every time\n"
                    f"# when the support body's tag(conf_info/bot) is changed\nSUPPORT = {message.chat.id}\n")
    user = User(chat_id)
    for known_user in known_users:
        if known_user.chat_id == user.chat_id:
            user = "Already exists"
    if user != "Already exists":
        known_users.append(user)
    markup = types.ReplyKeyboardMarkup(row_width=2)
    markup.add(*buttons[0])
    print("start", datetime.datetime.now(), "user", message.from_user.first_name, message.from_user.username)
    bot.send_message(message.chat.id, f"Привет, {message.from_user.first_name}. Добро пожаловать в бот 'Hermes'",
                     reply_markup=markup)


def find_user(chat_id):
    chat_id = str(chat_id)
    for known_user in known_users:
        if known_user.chat_id == chat_id:
            return known_user
    user = User(chat_id)
    known_users.append(user)
    return user


@bot.message_handler(func=lambda message: message.text == Command.TOP_7_DAYS)
def analytics_7_days(message):
    global dataset
    pre_dataset = [f"*{i+1}. {p['symbol']}*" for i, p in
               enumerate(get_predictions())]
    n = 5
    dataset = ["\n".join(pre_dataset[i:i + n]) for i in range(0, len(pre_dataset), n)]
    dataset.append("None")
    text = f"По нашим прогнозам, следующие бумаги наиболее вероятно принесут прибыль:"
    bot.reply_to(message, text, parse_mode="Markdown")
    pagination(message)


def append_portfolio_by_message(message):
    global dataset
    dataset = []
    chat_id = str(message.chat.id)
    user = find_user(chat_id)
    profiles = user.profiles
    if not profiles:
        dataset.append("Пока у Вас нет портфелей")
        dataset.append("None")
    else:
        for profile in profiles:
            name = profile.name
            text = [f"*{name}*\n", ]
            stocks = profile.stocks
            if not stocks:
                text.append("Пока тут пусто")
            else:
                for s in stocks:
                    text.append(f"- {s['symbol']}")
            dataset.append("\n".join(text))
        dataset.append("False")


def add_to_portfolio(message):
    append_portfolio_by_message(message)


def define_buttons(message):
    letter = message.text.upper()
    global dataset
    dataset = []
    print(letter)
    # stocks = {'_id': ObjectId('67472dd0eb151d67d708ab72'), 'Report_date': '28.08.2024', 'Report_currency': 'RUB', 'Revenue': 1.5, 'Operating_profit': 0.337, 'EBITDA': 0.197, 'Operating_cashflow': 0.496, 'CAPEX': 0.216, 'FCF': 0.273, 'Dividend_payout': 0.111, 'Dividend': '1,2', 'Dividends_profit': '11%', 'Oper_expenses': 1.16, 'Depreciation': 0.1, 'Interest_expenses': 0.053, 'Assets': 2.51, 'Net_assets': 0.433, 'Debt': 0.61, 'Cash': 0.37, 'Net_debt': 0.24, 'JSC_share_price': 74.4, 'JSC_share_number': 92.6, 'Capitalization': 6.89, 'EV': 7.13, 'Balancesheet_value': -0.39, 'EPS': 10.4, 'FCF_share': 2.94, 'BV_share': -4.19, 'EBITDA_return': '13.2%', 'Net_return': '64.7%', 'FCF_yield': '4.0%', 'ROE': '223.6%', 'ROA': '38.6%', 'PE': 7.12, 'PFCF': 25.3, 'PS': 4.61, 'PBV': -17.8, 'EVEBITDA': 36.2, 'DebtEBITDA': 1.22, 'RD_CAPEX': 0, 'CAPEX_Revenue': '14%', 'symbol': 'ABIO'}
    try:
        stocks = find_document({'symbol': letter}, "smartlab_data")
        # print(stocks)
        if type(stocks) is list:
            for stock_ in stocks:
                name = stock_["symbol"]
                risk_stock = find_document({"symbol": stock_["symbol"]}, "risk")
                volatility = risk_stock["volatility"]
                downside_dev = risk_stock["downside_dev"]
                risk_level = classify_volatility(volatility)
                dataset.append(f"{name}\n{risk_level}(volatility: {volatility}, downside_dev: {downside_dev})")
        else:
            name = stocks["symbol"]
            risk_stock = find_document({'ticker':{'$regex':letter}}, "risk")
            # print(risk_stock)

            ### Mock ###
            # risk_stock = {'_id': ObjectId("6737fbaf0cf4067423696fc1"), 'isin': 'RU000A0JNAB6', 'return_ann': -34.7221736386219, 'volatility': 40.4792067847041, 'downside_dev': 0.273899710339255, 'count_unique_prices': 244, 'count_unique_dividend': 1, 'ticker': 'ABIO RX', 'name': 'iАРТГЕН ао'}

            if len(risk_stock) > 0 and risk_stock is not None:
                if "volatility" in risk_stock.keys() and "downside_dev" in risk_stock.keys():
                    volatility = risk_stock["volatility"]
                    downside_dev = risk_stock["downside_dev"]
                    risk_level = classify_volatility(volatility)
                    dataset.append(f"*{name}*\n{risk_level} (volatility: {str(round(volatility, 2))}, downside dev: {str(round(downside_dev, 2))})")
                else:
                    dataset.append(f"*{name}*\nнет информации о волатильности")
            else:
                dataset.append(f"*{name}*\nнет информации о волатильности")
    except Exception as e:
        print(e)
        dataset.append(f"*{letter}*\nне найден")
    finally:
        dataset.append("True")
        pagination(message)



def pagination(message, page=1):
    cut_dataset = dataset[:-1]
    paginator = InlineKeyboardPaginator(
        len(cut_dataset),
        current_page=page,
        data_pattern="elements#{page}"
    )
    if dataset[-1] == "False":
        paginator.add_before(
            types.InlineKeyboardButton("Добавить сюда", callback_data="addhere#{}".format(page))
        )
    elif dataset[-1] == "True":
        paginator.add_before(
            types.InlineKeyboardButton(Command.MARK_FAVOURITE, callback_data="favourite#{}".format(page)),
            types.InlineKeyboardButton(Command.ADD_STOCK, callback_data="toprofile#{}".format(page)),
        )
        paginator.add_after(
            types.InlineKeyboardButton(Command.STOCK_INFO, callback_data="stockinfo#{}".format(page)),
            types.InlineKeyboardButton(Command.BACK, callback_data="home#{}".format(page)),
        )
    elif dataset[-1] == "None":
        paginator.add_before(
            types.InlineKeyboardButton(Command.BACK, callback_data="home#{}".format(page))
        )
    bot.send_message(message.chat.id, cut_dataset[page - 1], reply_markup=paginator.markup, parse_mode='Markdown')


def more_info(message, page):
    markup = types.InlineKeyboardMarkup()
    back_ = types.InlineKeyboardButton('Назад', callback_data='back_#{}'.format(page))
    markup.add(back_)
    symbol = dataset[page-1].replace('*', '')
    text = get_smartlab_data(symbol)
    if len(text) > 0:
        text = text.split('\n')
        for i in [2, -2]:
            text.insert(i, '\n')
        text = '\n'.join(text)
    else:
        text = 'нет данных'
    bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode='Markdown')


def stock_to_portfolio(message, page):
    profile_name = dataset[page - 1].split('\n\n')[0].replace('*', '')
    chat_id = str(message.chat.id)
    user = find_user(chat_id)
    for prof in user.profiles:
        if prof.name == profile_name:
            profile = prof
            stocks = profile.stocks
            if stocks is None:
                profile.stocks = []
            profile.stocks.append(stock)
            return {"status_code": 200}


def add_to_favourites(message, symbol, chat_id):
    stock_ = find_document(symbol, "smartlab_data")
    user = find_user(chat_id)
    favourite_stocks = user.favourite_stocks
    if favourite_stocks is None:
        favourite_stocks = []
    favourite_stocks.append(stock_)
    bot.send_message(message.chat.id, 'Бумага добавлена в избранные')
    return {"status_code": 200}


@bot.callback_query_handler(func=lambda call: True)
def characters_page_callback(call, delete=True):
    message = call.message
    page = int(call.data.split('#')[1])
    chat_id = str(message.chat.id)
    data = call.data.split('#')[0]
    if data == 'favourite':
        symbol = dataset[page-1][1:5]
        add_to_favourites(message, symbol, chat_id)
    elif data == 'toprofile':
        global stock
        symbol = dataset[page-1][1:5]
        stock = find_document(symbol, "smartlab_data")
        add_to_portfolio(message)
        page = 1
    elif data == 'stockinfo':
        more_info(call.message, page)
        return bot.delete_message(message.chat.id, message.message_id)
    elif data == 'back':
        delete = False
    elif data == 'home':
        return home(message)
    elif data == 'addhere':
        markup = telebot.types.ReplyKeyboardMarkup(row_width=2)
        markup.add(*buttons[0])
        stock_to_portfolio(message, page)
        bot.delete_message(message.chat.id, message.message_id)
        return bot.send_message(message.chat.id, 'Готово. Выбранная бумага добавлена в Ваш портфель',
                                reply_markup=markup)
    if delete:
        bot.delete_message(message.chat.id, message.message_id)
    pagination(message, page)


@bot.message_handler(func=lambda message: message.text == Command.STOCK)
def stock(message):
    sent = bot.send_message(message.chat.id,
                            'Введите торговый код акции, или буквы, с которых он начинается, пример: "AB"',
                            reply_markup=ReplyKeyboardRemove())
    bot.register_next_step_handler(sent, define_buttons)


def create_empty_profile(message):
    markup = types.ReplyKeyboardMarkup(row_width=2)
    markup.add(*buttons[0])
    name = message.text
    chat_id = message.chat.id
    profile = Profile(
        user_id=chat_id,
        name=name
    )
    user = find_user(chat_id)
    if user.profiles is None:
        user.profiles = []
    user.profiles.append(profile)
    bot.reply_to(message, 'Сохранено', reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == Command.CREATE_EMPTY_PORTFOLIO)
def empty_portfolio(message):
    sent = bot.reply_to(message, 'Введите имя...', reply_markup=ReplyKeyboardRemove())
    bot.register_next_step_handler(sent, create_empty_profile)


@bot.message_handler(func=lambda message: message.text == Command.SELECT_PORTFOLIO)
def select_portfolio(message):
    global dataset
    append_portfolio_by_message(message)
    dataset[-1] = 'None'
    pagination(message)


@bot.message_handler(func=lambda message: message.text == Command.BACK)
def home(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2)
    markup.add(*buttons[0])
    bot.send_message(message.chat.id, "Главное меню", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == Command.PORTFOLIO)
def portfolio(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2)
    markup.add(*buttons[1])
    bot.reply_to(message, "выбор из списка...", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == Command.CREATE_PORTFOLIO)
def create_portfolio(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2)
    markup.add(*buttons[2])
    bot.reply_to(message, "создание...", reply_markup=markup)


def reach_support(message):
    from conf_info.support import SUPPORT
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2)
    markup.add(*buttons[0])
    bot.reply_to(message, "Отправляю Ваш запрос в поддержку...", reply_markup=markup)
    bot.send_message(SUPPORT, f"@{message.from_user.username} нуждается в помощи: {message.text}")


@bot.message_handler(func=lambda message: message.text == Command.SUPPORT)
def support(message):
    sent = bot.reply_to(message,
                        "Опишите, пожалуйста, вашу проблему или вопрос. Вернемся к вам максимально оперативно 🙏",
                        reply_markup=ReplyKeyboardRemove())
    bot.register_next_step_handler(sent, reach_support)


@bot.message_handler(func=lambda message: message.text == Command.FAVOURITE)
def favourites(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2)
    markup.add(*buttons[0])
    bot.reply_to(message, "Высылаю Ваш список избранных...", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == Command.REMOVE_STOCK)
def delete_from_portfolio(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2)
    markup.add(*buttons[0])
    bot.reply_to(message, "Удаляю бумагу(из портфеля)...", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == Command.RENAME_PORTFOLIO)
def update_portfolio_name(message):
    bot.reply_to(message, "Введите новое имя", reply_markup=ReplyKeyboardRemove())


@bot.message_handler(func=lambda message: message.text == Command.DELETE_PORTFOLIO)
def delete_portfolio(message):
    bot.reply_to(message, "Вы уверены?", reply_markup=ReplyKeyboardRemove())


@bot.message_handler(func=lambda message: message.text == Command.UPLOAD_PORTFOLIO)
def upload_portfolio(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2)
    markup.add(*buttons[0])
    bot.reply_to(message, text='Кидаю ссылку на загрузку...', reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == Command.GENERATE_PORTFOLIO)
def generate_portfolio(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2)
    markup.add(*buttons[0])
    bot.reply_to(message, text='Генерирую портфель...', reply_markup=markup)


if __name__ == '__main__':
    print('*' * 25, '\nBOT STARTED')
    while True:
        try:
            bot.polling(none_stop=True, timeout=90)
        except Exception as e:
            print(datetime.datetime.now(), e)
            time.sleep(5)
            continue
    # bot.infinity_polling()
    # print(known_users[0].profiles.stocks)
    # print('*' * 25, '\nBOT STOPPED')
