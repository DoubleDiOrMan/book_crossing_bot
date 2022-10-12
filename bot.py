from email.message import Message
from re import L
import telebot 
import sqlite3
from telebot import types

bot = telebot.TeleBot("5758825270:AAFIW5MEJg1nSOSKyMFVyHnuVlYNfrBz8X0")
remove_keyboard = types.ReplyKeyboardRemove()

@bot.message_handler(commands=['start'])
def start(message):

    connect = sqlite3.connect('books.db')
    cursor = connect.cursor()
    man_id = message.chat.id
    cursor.execute("SELECT id FROM users WHERE user_id = ?", (man_id,))

    data = cursor.fetchone()

    if (data is None):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1, one_time_keyboard=True)
        button_1 = types.KeyboardButton("1️⃣ Москва")
        button_2 = types.KeyboardButton("2️⃣ Санкт-Петербург")
        markup.add(button_1, button_2)
        bot.send_message(message.chat.id, "Добро пожаловать!\nВыберите город:", reply_markup=markup)
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1, one_time_keyboard=True)
        btn1 = types.KeyboardButton("Записать книгу")
        btn2 = types.KeyboardButton("Поиск книги по названию")
        btn3 = types.KeyboardButton("Поиск книги по жанру")
        btn4 = types.KeyboardButton("Поиск книги по автору")
        btn5 = types.KeyboardButton("Удалить запись о книге")
        markup.add(btn1, btn2, btn3, btn4, btn5)

        bot.send_message(message.chat.id, f"Привествую тебя снова, {message.from_user.first_name}!", reply_markup=remove_keyboard)
        bot.send_photo(message.chat.id, photo = open('salute.png', 'rb'))
        send = bot.send_message(message.chat.id, "Что вы хотите сделать?", reply_markup=markup)
        bot.register_next_step_handler(send, RSSS_book)

@bot.message_handler(content_types=['text'])
def message_user(message):
    
    connect = sqlite3.connect('books.db')
    cursor = connect.cursor()

    if(message.text == "1️⃣ Москва") or (message.text =="2️⃣ Санкт-Петербург"):
        city = message.text.split(' ')[1]
        man_id = int(message.chat.id)
        username = message.from_user.username
        cursor.execute("SELECT id FROM users WHERE user_id = ?", (man_id,))
        connect.commit()
        data = cursor.fetchone()
        if (data is None):
            cursor.execute("INSERT INTO users (user_id, city, username) VALUES(?, ?, ?);", (man_id, city, username))
            connect.commit()
            
            markup = types.ReplyKeyboardMarkup(row_width=1)
            btn1 = types.KeyboardButton("Записать книгу")
            btn2 = types.KeyboardButton("Поиск книги по названию")
            btn3 = types.KeyboardButton("Поиск книги по жанру")
            btn4 = types.KeyboardButton("Поиск книги по автору")
            btn5 = types.KeyboardButton("Удалить запись о книге")
            markup.add(btn1, btn2, btn3, btn4, btn5)

            bot.send_message(message.chat.id, "Вы успешно зарегистрировались", reply_markup=remove_keyboard)
            send = bot.send_message(message.chat.id, "Что вы хотите сделать?", reply_markup=markup)
            bot.register_next_step_handler(send, RSSS_book)

def RSSS_book(message):

    if (message.text == "Записать книгу"):
        bot.send_message(message.chat.id, "Необходимо ввести параметры вашей книги")
        send = bot.send_message(message.chat.id, "Введите полное название вашей книги")
        bot.register_next_step_handler(send, title_book)

    elif(message.text == "Поиск книги по названию"):
        send = bot.send_message(message.chat.id, "Введите полное название книги, которую ищете")
        bot.register_next_step_handler(send, search_name)
    elif(message.text == "Поиск книги по автору"):
        send = bot.send_message(message.chat.id, "Введите автора книги, которую ищете")
        bot.register_next_step_handler(send, search_author)
    elif(message.text == "Поиск книги по жанру"):
        send = bot.send_message(message.chat.id, "Введите жанр книги, которую ищете")
        bot.register_next_step_handler(send, search_genre)
    elif(message.text == "Удалить запись о книге"):
        connect = sqlite3.connect('books.db')
        cursor = connect.cursor()

        cursor.execute("SELECT id, book_name, author, genre FROM record_books WHERE user_id = ?", (message.from_user.id,))
        connect.commit()

        records = cursor.fetchall()
        if (records != []):
            for row in records:
                bot.send_message(message.chat.id, f"ID: {row[0]}\nНазвание: {row[1]}\nАвтор: {row[2]}\nЖанр: {row[3]}\n\n")
    
            mark = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
            yes = types.KeyboardButton("Да")
            no = types.KeyboardButton("Нет")
            mark.add(yes, no)

            send = bot.send_message(message.chat.id, "Выбрали какую книгу удалить?", reply_markup=mark)
            bot.register_next_step_handler(send, yes_no_for_delete)
        else:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1, one_time_keyboard=True)
            btn1 = types.KeyboardButton("Записать книгу")
            btn2 = types.KeyboardButton("Поиск книги по названию")
            btn3 = types.KeyboardButton("Поиск книги по жанру")
            btn4 = types.KeyboardButton("Поиск книги по автору")
            btn5 = types.KeyboardButton("Удалить запись о книге")
            markup.add(btn1, btn2, btn3, btn4, btn5)

            send = bot.send_message(message.chat.id, "Видимо такой книги нет\nВозвращаю вас обратно\nЧто вы хотите сделать?", reply_markup=markup)
            bot.register_next_step_handler(send, RSSS_book)
    elif (message.text == "/start"):
        send = bot.send_message(message.chat.id, "Рестарт бота\nНапишите любое сообщение")
        bot.register_next_step_handler(send, start)

def title_book(message):
    name = message.text
    bot.send_message(message.chat.id, f"Название книги: {name}")
    send = bot.send_message(message.chat.id, "Введите автора (фамилию) книги")
    bot.register_next_step_handler(send, author_book, name)
    
def author_book(message, name):
    author = message.text
    bot.send_message(message.chat.id, f"Автор книги: {author}")
    send = bot.send_message(message.chat.id, "Введите жанр книги")
    bot.register_next_step_handler(send, genre_book, name, author)

def genre_book(message, name, author):
    genre = message.text

    mark = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
    yes = types.KeyboardButton("Да")
    no = types.KeyboardButton("Нет")
    close = types.KeyboardButton("Выход")
    mark.add(yes, no, close)

    bot.send_message(message.chat.id, f"Жанр книги: {genre}")
    send = bot.send_message(message.chat.id, f"Параметры вашей книги:\nНазвание - {name}\nАвтор - {author}\nЖанр - {genre}\n\nВерно?", reply_markup=mark)
    bot.register_next_step_handler(send, yes_no, name, author, genre)

def yes_no(message, name, author, genre):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1, one_time_keyboard=True)
    btn1 = types.KeyboardButton("Записать книгу")
    btn2 = types.KeyboardButton("Поиск книги по названию")
    btn3 = types.KeyboardButton("Поиск книги по жанру")
    btn4 = types.KeyboardButton("Поиск книги по автору")
    btn5 = types.KeyboardButton("Удалить запись о книге")
    markup.add(btn1, btn2, btn3, btn4, btn5)

    if (message.text == "Да"):

        connect = sqlite3.connect('books.db')
        cursor = connect.cursor()

        cursor.execute("SELECT city FROM users WHERE user_id = ?", (message.from_user.id,))
        city_new = cursor.fetchone()[0]

        cursor.execute("INSERT INTO record_books (user_id, book_name, author, genre, city) VALUES (?, ?, ?, ?, ?)", (message.from_user.id, name.lower(), author.lower(), genre.lower(), city_new))
        connect.commit()

        done = bot.send_message(message.chat.id, "Запись книги прошла успешно!\nЧто вы хотите сделать?", reply_markup=markup)
        bot.register_next_step_handler(done, RSSS_book)

    elif (message.text == "Нет"):
        send = bot.send_message(message.chat.id, "Ладно, давай по новой\nВведите полное название вашей книги")
        bot.register_next_step_handler(send, title_book)
    elif(message.text == "Выход"):
        send = bot.send_message(message.chat.id, "Нет у вас книги, значит\nЛадно возвращаю вас обратно", reply_markup=markup)
        bot.register_next_step_handler(send, RSSS_book)

def search_name(message):

    book_name = message.text.lower()
    connect = sqlite3.connect('books.db')
    cursor = connect.cursor()
    cursor.execute("SELECT id, book_name, author, genre FROM record_books WHERE book_name = ?", (book_name,))
    connect.commit()
    records = cursor.fetchall()
    if (records != []):
        for row in records:
            bot.send_message(message.chat.id, f"ID: {row[0]}\nНазвание: {row[1]}\nАвтор: {row[2]}\nЖанр: {row[3]}\n\n")
    
        mark = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
        yes = types.KeyboardButton("Да")
        no = types.KeyboardButton("Нет")
        mark.add(yes, no)

        send = bot.send_message(message.chat.id, "Выбрали что-нибудь?", reply_markup=mark)
        bot.register_next_step_handler(send, yes_no_for_search)
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1, one_time_keyboard=True)
        btn1 = types.KeyboardButton("Записать книгу")
        btn2 = types.KeyboardButton("Поиск книги по названию")
        btn3 = types.KeyboardButton("Поиск книги по жанру")
        btn4 = types.KeyboardButton("Поиск книги по автору")
        btn5 = types.KeyboardButton("Удалить запись о книге")
        markup.add(btn1, btn2, btn3, btn4, btn5)

        send = bot.send_message(message.chat.id, "Видимо такой книги нет\nВозвращаю вас обратно\nЧто вы хотите сделать?", reply_markup=markup)
        bot.register_next_step_handler(send, RSSS_book)

def search_author(message):

    author = message.text.lower()
    connect = sqlite3.connect('books.db')
    cursor = connect.cursor()

    cursor.execute("SELECT id, book_name, author, genre FROM record_books WHERE author = ?", (author,))
    records = cursor.fetchall()
    connect.commit()

    if (records != []):
        for row in records:
            bot.send_message(message.chat.id, f"ID: {row[0]}\nНазвание: {row[1]}\nАвтор: {row[2]}\nЖанр: {row[3]}\n\n")
    
        mark = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
        yes = types.KeyboardButton("Да")
        no = types.KeyboardButton("Нет")
        mark.add(yes, no)

        send = bot.send_message(message.chat.id, "Выбрали что-нибудь?", reply_markup=mark)
        bot.register_next_step_handler(send, yes_no_for_search)
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1, one_time_keyboard=True)
        btn1 = types.KeyboardButton("Записать книгу")
        btn2 = types.KeyboardButton("Поиск книги по названию")
        btn3 = types.KeyboardButton("Поиск книги по жанру")
        btn4 = types.KeyboardButton("Поиск книги по автору")
        btn5 = types.KeyboardButton("Удалить запись о книге")
        markup.add(btn1, btn2, btn3, btn4, btn5)

        send = bot.send_message(message.chat.id, "Видимо такой книги нет\nВозвращаю вас обратно\nЧто вы хотите сделать?", reply_markup=markup)
        bot.register_next_step_handler(send, RSSS_book)
    
def search_genre(message):

    genre = message.text.lower()
    connect = sqlite3.connect('books.db')
    cursor = connect.cursor()

    cursor.execute("SELECT id, book_name, author, genre FROM record_books WHERE genre = ?", (genre,))
    connect.commit()

    records = cursor.fetchall()
    if (records != []):
        for row in records:
            bot.send_message(message.chat.id, f"ID: {row[0]}\nНазвание: {row[1]}\nАвтор: {row[2]}\nЖанр: {row[3]}\n\n")
    
        mark = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
        yes = types.KeyboardButton("Да")
        no = types.KeyboardButton("Нет")
        mark.add(yes, no)

        send = bot.send_message(message.chat.id, "Выбрали что-нибудь?", reply_markup=mark)
        bot.register_next_step_handler(send, yes_no_for_search)
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1, one_time_keyboard=True)
        btn1 = types.KeyboardButton("Записать книгу")
        btn2 = types.KeyboardButton("Поиск книги по названию")
        btn3 = types.KeyboardButton("Поиск книги по жанру")
        btn4 = types.KeyboardButton("Поиск книги по автору")
        btn5 = types.KeyboardButton("Удалить запись о книге")
        markup.add(btn1, btn2, btn3, btn4, btn5)

        send = bot.send_message(message.chat.id, "Видимо такой книги нет\nВозвращаю вас обратно\nЧто вы хотите сделать?", reply_markup=markup)
        bot.register_next_step_handler(send, RSSS_book)

def yes_no_for_delete(message):
    if (message.text == "Да"):
        send = bot.send_message(message.chat.id, "Введите ID книги, которую нужно удалить")
        bot.register_next_step_handler(send, id_book_delete)
    elif (message.text == "Нет"):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1, one_time_keyboard=True)
        btn1 = types.KeyboardButton("Записать книгу")
        btn2 = types.KeyboardButton("Поиск книги по названию")
        btn3 = types.KeyboardButton("Поиск книги по жанру")
        btn4 = types.KeyboardButton("Поиск книги по автору")
        btn5 = types.KeyboardButton("Удалить запись о книге")
        markup.add(btn1, btn2, btn3, btn4, btn5)

        send = bot.send_message(message.chat.id, "Ладно возвращаю вас обратно\nЧто вы хотите сделать?", reply_markup=markup)
        bot.register_next_step_handler(send, RSSS_book)

def yes_no_for_search(message):
    if (message.text == "Да"):
        send = bot.send_message(message.chat.id, "Введите ID книги, которую выбрали")
        bot.register_next_step_handler(send, id_book_message)
    elif (message.text == "Нет"):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1, one_time_keyboard=True)
        btn1 = types.KeyboardButton("Записать книгу")
        btn2 = types.KeyboardButton("Поиск книги по названию")
        btn3 = types.KeyboardButton("Поиск книги по жанру")
        btn4 = types.KeyboardButton("Поиск книги по автору")
        btn5 = types.KeyboardButton("Удалить запись о книге")
        markup.add(btn1, btn2, btn3, btn4, btn5)

        send = bot.send_message(message.chat.id, "Ладно возвращаю вас обратно\nЧто вы хотите сделать?", reply_markup=markup)
        bot.register_next_step_handler(send, RSSS_book)

def id_book_delete(message):
    id = message.text
    connect = sqlite3.connect('books.db')
    cursor = connect.cursor()

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1, one_time_keyboard=True)
    btn1 = types.KeyboardButton("Записать книгу")
    btn2 = types.KeyboardButton("Поиск книги по названию")
    btn3 = types.KeyboardButton("Поиск книги по жанру")
    btn4 = types.KeyboardButton("Поиск книги по автору")
    btn5 = types.KeyboardButton("Удалить запись о книге")
    markup.add(btn1, btn2, btn3, btn4, btn5)    

    cursor.execute("DELETE FROM record_books WHERE id = ?", (id,))
    connect.commit()

    send = bot.send_message(message.chat.id, "Книга успешно удалена!\nЧто вы хотите сделать?", reply_markup=markup)
    bot.register_next_step_handler(send, RSSS_book)

def id_book_message(message):
    id = message.text
    connect = sqlite3.connect('books.db')
    cursor = connect.cursor()

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1, one_time_keyboard=True)
    btn1 = types.KeyboardButton("Записать книгу")
    btn2 = types.KeyboardButton("Поиск книги по названию")
    btn3 = types.KeyboardButton("Поиск книги по жанру")
    btn4 = types.KeyboardButton("Поиск книги по автору")
    btn5 = types.KeyboardButton("Удалить запись о книге")
    markup.add(btn1, btn2, btn3, btn4, btn5)    

    cursor.execute("SELECT user_id FROM record_books WHERE id = ?", (id,))
    user = cursor.fetchone()[0]

    cursor.execute("SELECT username FROM users WHERE user_id = ?", (user,))
    dota2 = cursor.fetchone()[0]
    connect.commit()

    send = bot.send_message(message.chat.id, f"Контакты для связи:\n@{dota2}", reply_markup=markup)
    bot.register_next_step_handler(send, RSSS_book)

if __name__ == '__main__':
    bot.polling(non_stop="True", interval=0)