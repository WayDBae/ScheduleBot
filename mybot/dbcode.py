from bot import bot #импортируем объект бота
from messages import * #Импортируем всё с файла сообщений
import sqlite3
import config
from telebot import types
from datetime import datetime

# Dictionary to store user data
user_data = {}
@bot.message_handler(commands=['start'])
def start_handler(message):
    # Check if user data exists in the database
    try:
        with sqlite3.connect('users.db', check_same_thread=False) as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM users WHERE chat_id={message.chat.id}")
            user = cursor.fetchone()
    except sqlite3.Error as e:
        config.logger.error(f"Error while accessing the database: {e}")
        bot.send_message(message.chat.id, "Произошла ошибка при доступе к базе данных. Попробуйте позже.")
        return

    if user:
        # If user data exists, display a message with the selected data
        selected_data = {"direction": user[2], "course": user[3], "group": user[4]}
        start_message = f"""👋 Привет, {message.from_user.first_name}!

Вы выбрали:
Направление: {selected_data['direction']}
Курс: {selected_data['course']}
Группа: {selected_data['group']}

🛠❤️*Разработчик* — _@{config.DEVELOPER_USERNAME}_
"""
    else:
        # If user data does not exist, display a default message
        start_message = f"""👋 Привет, {message.from_user.first_name}!

Добро пожаловать в *DF NITU MISIS Bot!*

🛠❤️*Разработчик* — _@{config.DEVELOPER_USERNAME}_
"""

    # Create authorization keyboard
    autorize = types.ReplyKeyboardMarkup(resize_keyboard=True)
    confirm_btn = types.KeyboardButton(text="Выбрать расписание")
    reference_btn = types.KeyboardButton(text="Справка")
    profile_btn = types.KeyboardButton(text="Профиль")
    autorize.add(confirm_btn)
    autorize.add(reference_btn, profile_btn)

    # Send message with keyboard
    bot.send_message(message.chat.id, text=start_message, reply_markup=autorize, parse_mode="Markdown")

@bot.message_handler(commands=['add'])
def add_handler(message):
    # Проверяем, что отправитель сообщения - администратор
    if message.from_user.username == config.DEVELOPER_USERNAME:
        # Создаем клавиатуру выбора направления, курса и группы
        add_key = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        for direction in config.DIRECTIONS:
            direction_btn = types.KeyboardButton(direction)
            add_key.add(direction_btn)
        add_key.add(types.KeyboardButton("Отмена"))

        # Отправляем сообщение с клавиатурой
        bot.send_message(message.chat.id, "Выберите направление, для которого хотите добавить расписание", reply_markup=add_key)

        # Регистрируем следующий обработчик
        bot.register_next_step_handler(message, get_schedule_data)
    else:
        bot.send_message(message.chat.id, NO_RULE)

def get_schedule_data(message):
    # Проверяем, что пользователь не нажал кнопку "Отмена"
    if message.text == "Отмена":
        bot.send_message(message.chat.id, "Добавление расписания отменено")
        return

    # Получаем выбранные данные о направлении
    selected_data = message.text
    if selected_data not in config.DIRECTIONS:
        bot.send_message(message.chat.id, NO_CORRECT)
        return

    # Сохраняем выбранные данные в словаре
    user_data[message.chat.id] = {"direction": selected_data}
    # Создаем клавиатуру выбора курса 
    add_key = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    for course in config.COURSES:
        course_btn = types.KeyboardButton(course)
        add_key.add(course_btn)
    add_key.add(types.KeyboardButton("Отмена"))

    # Отправляем сообщение с клавиатурой
    bot.send_message(message.chat.id, "Выберите курс", reply_markup=add_key)

    # Регистрируем следующий обработчик
    bot.register_next_step_handler(message, get_schedule_data2)

def get_schedule_data2(message):
    # Проверяем, что пользователь не нажал кнопку "Отмена"
    if message.text == "Отмена":
        bot.send_message(message.chat.id, CANCEL_MSG)
        return

    # Получаем выбранные данные о курсе и группе
    selected_data = message.text
    if selected_data not in config.COURSES:
        bot.send_message(message.chat.id, NO_CORRECT)
        return

    # Добавляем выбранные данные в словарь
    user_data[message.chat.id]["course"] = selected_data
    group_key = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    # Отправляем сообщение с просьбой ввести расписание
    if user_data[message.chat.id]["direction"] in ["Информатика"] and user_data[message.chat.id]["course"] in ["1 курс", "2 курс","3 курс"]:
       group_a_btn = types.KeyboardButton("Группа А")
       group_b_btn = types.KeyboardButton("Группа Б")
       group_key.add(group_a_btn, group_b_btn)
    elif user_data[message.chat.id]["direction"] in ["Металлургия"] and user_data[message.chat.id]["course"] in ["1 курс", "2 курс"]:
        group_a_btn = types.KeyboardButton("Группа А")
        group_b_btn = types.KeyboardButton("Группа Б")
        group_key.add(group_a_btn, group_b_btn)
    else:
        group_a_btn = types.KeyboardButton("Группа А")
        group_key.add(group_a_btn)

    # Отправляем сообщение с клавиатурой
    bot.send_message(message.chat.id, "Выберите вашу группу", reply_markup=group_key)

    bot.register_next_step_handler(message, get_schedule_data3)

def get_schedule_data3(message):
    if message.text == "Отмена":
        bot.send_message(message.chat.id, CANCEL_MSG)
        return
    else:
        user_data[message.chat.id]["group_name"] = message.text
        print(user_data[message.chat.id]["direction"],user_data[message.chat.id]["group_name"])
        for key, value in config.GROUPS.items():
            print(key,value)
            if user_data[message.chat.id]["direction"] == key and user_data[message.chat.id]["group_name"] in value:
                bot.send_message(message.chat.id, f"Введите расписание в формате, который вы используете для хранения расписания")
                bot.register_next_step_handler(message, save_student_data)
                break
def save_student_data(message):
    schedule = message.text
        # Получаем данные о направлении, курсе и группе из словаря
    direction = user_data[message.chat.id]["direction"]
    course = user_data[message.chat.id]["course"]
    group_name = user_data[message.chat.id]["group_name"]

    # Сохраняем данные в базу данных
    try:
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (direction, course, group_name, schedule, created_at) VALUES (?, ?, ?, ?, ?)",
                   (direction, course, group_name, schedule, datetime.now()))
        conn.commit()
        bot.send_message(message.chat.id, "Расписание успешно добавлено в базу данных")
    except Exception as e:
        config.logger.error(f"Error while saving schedule data: {e}")
        bot.send_message(message.chat.id, f"Произошла ошибка при добавлении расписания в базу данных. Пожалуйста, попробуйте еще раз или обратитесь к @{config.DEVELOPER_USERNAME} для получения помощи")
    finally:
        conn.close()

    # Удаляем данные о пользователе из словаря
    del user_data[message.chat.id]


def save_schedule(message):
    # Получаем выбранные данные о типе недели, дне недели, временных слотах, аудитории и преподавателе
    selected_data = message.text.split()
    if len(selected_data) != 5 or selected_data[0] not in ["Числитель", "Знаменатель"] or selected_data[1] not in ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница"] or selected_data[2] not in ["8:00-9:20", "9:30-10:50", "11:10-12:30"]:
        bot.send_message(message.chat.id, "Некорректные данные. Пожалуйста, выберите тип недели, день недели и временные слоты с помощью клавиатуры")
        return

    # Сохраняем выбранные данные в базу данных
    try:
        with sqlite3.connect('users.db', check_same_thread=False) as conn:
            cursor = conn.cursor()
            cursor.execute(f"INSERT INTO users (chat_id, status, direction, course, group_name, auditory, time_slot, upper_week, lower_week) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (message.chat.id, "active", user_data[message.chat.id]['direction'], user_data[message.chat.id]['course'], user_data[message.chat.id]['group_name'], selected_data[3], selected_data[2], selected_data[0], selected_data[0]))
            conn.commit()
    except sqlite3.Error as e:
        config.logger.error(f"Error while accessing the database: {e}")
        bot.send_message(message.chat.id, "Произошла ошибка при доступе к базе данных. Попробуйте позже.")
        return

    # Отправляем сообщение о том, что расписание было успешно добавлено
    bot.send_message(message.chat.id, "Расписание успешно добавлено!")

# Обработчик любых сообщений
@bot.message_handler(func=lambda message: message.text in ["Выбрать расписание", "Справка", "Профиль", "Назад","Отмена"])
def menu_handler(message):
    if message.text == "Выбрать расписание":
        # Создаем клавиатуру выбора статуса (студент/преподаватель)
        status_key = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        student_btn = types.KeyboardButton(text="Студент")
        teacher_btn = types.KeyboardButton(text="Преподаватель")
        back_btn = types.KeyboardButton(text="Назад")
        status_key.add(student_btn, teacher_btn, back_btn)
        # Отправляем сообщение с клавиатурой
        bot.send_message(message.chat.id, text="Выберите роль", reply_markup=status_key)

    elif message.text == "Справка":
        # Удаляем предыдущее сообщение пользователя
        bot.send_message(message.chat.id, HELP_MESSAGE)
    
    elif message.text == "Профиль":
        # Отправляем сообщение с профилем пользователя
        bot.send_message(message.chat.id, f"⚙️ Ваш *Telegram ID* — {message.chat.id}", parse_mode="Markdown")
    elif message.text == "Назад":
        start_handler(message)
    
    elif message.text == "Отмена":
        status_key = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        student_btn = types.KeyboardButton(text="Студент")
        teacher_btn = types.KeyboardButton(text="Преподаватель")
        back_btn = types.KeyboardButton(text="Назад")
        status_key.add(student_btn, teacher_btn, back_btn)
        bot.send_message(message.chat.id, text="Выберите роль", reply_markup=status_key)

    else:

        # Отправляем сообщение с просьбой выбрать одну из кнопок
        bot.send_message(message.chat.id, text="Пожалуйста выберите одну из кнопок. *НЕ СТОИТ* писать что-то лишнее!",
                         parse_mode="Markdown")


@bot.message_handler(func=lambda message: message.text in ["Студент", "Преподаватель"])
def user_type_handler(message):
    # Сохраняем выбранный статус пользователя
    user_data[message.chat.id] = {"status": message.text}

    if message.text == "Студент":
        # Создаем клавиатуру выбора направления
        direction_key = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        it_btn = types.KeyboardButton("Информатика")
        economy_btn = types.KeyboardButton("Экономика")
        metallygry_btn = types.KeyboardButton("Металлургия")
        cancel_btn = types.KeyboardButton("Отмена")
        direction_key.add(it_btn, economy_btn, metallygry_btn, cancel_btn)

        # Отправляем сообщение с клавиатурой
        bot.send_message(message.chat.id, "Выберите направление", reply_markup=direction_key)

        # Регистрируем следующий обработчик
        bot.register_next_step_handler(message, get_students_direction)

    elif message.text == "Преподаватель":
        key = types.ReplyKeyboardMarkup(resize_keyboard=True)
        cancel_btn = types.KeyboardButton("Отмена")
        key.add(cancel_btn)
        bot.send_message(message.chat.id, "Введите фамилию", reply_markup=key)

        # Регистрируем следующий обработчик
        bot.register_next_step_handler(message, get_teachers_schedule)
    
def get_teachers_schedule(message):
    if message.text == "Отмена":
        bot.send_message(message.chat.id, "Выбор отменён.")
        menu_handler(message)
    else:
        # Проверяем, есть ли введенная фамилия в списке
        surname = message.text.strip().title()
        surnames = ["Табаров", "Сафаров"]
        if surname in surnames:
            autorize = types.ReplyKeyboardMarkup(resize_keyboard=True)
            confirm_btn = types.KeyboardButton(text="Выбрать расписание")
            reference_btn = types.KeyboardButton(text="Справка")
            profile_btn = types.KeyboardButton(text="Профиль")
            autorize.add(confirm_btn)
            autorize.add(reference_btn, profile_btn)
            bot.send_message(message.chat.id, f"Здравствуйте, {surname}\nВот ваше расписание:",reply_markup=autorize)
        else:
            # Если фамилии нет в списке, то выводим сообщение об ошибке
            autorize = types.ReplyKeyboardMarkup(resize_keyboard=True)
            confirm_btn = types.KeyboardButton(text="Выбрать расписание")
            reference_btn = types.KeyboardButton(text="Справка")
            profile_btn = types.KeyboardButton(text="Профиль")
            autorize.add(confirm_btn)
            autorize.add(reference_btn, profile_btn)
            bot.send_message(message.chat.id, "Вашей фамилии нет в списке...", reply_markup=autorize)

def get_students_direction(message):
    if message.text == "Отмена":
        bot.send_message(message.chat.id, "Выбор отменён.")
        menu_handler(message)
    else:
        # Сохраняем выбранное направление пользователя
        user_data[message.chat.id]["direction"] = message.text

        # Создаем клавиатуру выбора курса
        course_key = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        first_crs = types.KeyboardButton("1 курс")
        second_crs = types.KeyboardButton("2 курс")
        third_crs = types.KeyboardButton("3 курс")
        fourth_crs = types.KeyboardButton("4 курс")
        course_key.add(first_crs, second_crs, third_crs, fourth_crs)

        # Отправляем сообщение с клавиатурой
        bot.send_message(message.chat.id, "Выберите ваш курс", reply_markup=course_key)

        # Регистрируем следующий обработчик
        bot.register_next_step_handler(message, get_students_course)


def get_students_course(message):
    # Сохраняем выбранный курс пользователя
    user_data[message.chat.id]["course"] = message.text

    # Создаем клавиатуру выбора группы
    group_key = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)

    # Проверяем направление и курс пользователя
    if user_data[message.chat.id]["direction"] == "Информатика" and message.text in ["1 курс", "2 курс", "3 курс"]:
        group_a_btn = types.KeyboardButton("Группа А")
        group_b_btn = types.KeyboardButton("Группа Б")
        group_key.add(group_a_btn, group_b_btn)
    elif user_data[message.chat.id]["direction"] == "Металлургия" and message.text in ["1 курс", "2 курс"]:
        group_a_btn = types.KeyboardButton("Группа А")
        group_b_btn = types.KeyboardButton("Группа Б")
        group_key.add(group_a_btn, group_b_btn)
    else:
        group_a_btn = types.KeyboardButton("Группа А")
        group_key.add(group_a_btn)

    # Отправляем сообщение с клавиатурой
    bot.send_message(message.chat.id, "Выберите вашу группу", reply_markup=group_key)

    # Сохраняем выбранную группу пользователя
    bot.register_next_step_handler(message, save_user_data)


def save_user_data(message):
    # Сохраняем выбранную группу пользователя
    user_data[message.chat.id]["group"] = message.text

    # Отправляем сообщение с подтверждением выбранных данных
    selected_data = user_data[message.chat.id]
    start_message = f"""👋 Привет, {message.from_user.first_name}!

Вы выбрали:
Направление: {selected_data['direction']}
Курс: {selected_data['course']}
Группа: {selected_data['group']}

🛠❤️*Разработчик* — _@{config.DEVELOPER_USERNAME}_"""

    # Создаем клавиатуру авторизации
    autorize = types.ReplyKeyboardMarkup(resize_keyboard=True)
    confirm_btn = types.KeyboardButton(text="Выбрать расписание")
    reference_btn = types.KeyboardButton(text="Справка")
    profile_btn = types.KeyboardButton(text="Профиль")
    autorize.add(confirm_btn)
    autorize.add(reference_btn, profile_btn)

    # Отправляем сообщение с клавиатурой
    bot.send_message(message.chat.id, text=start_message, reply_markup=autorize, parse_mode="Markdown")

@bot.message_handler(commands=['schedule'])
def schedule_handler(message):
    # Получаем данные пользователя из базы данных
    try:
        with sqlite3.connect('users.db', check_same_thread=False) as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM users WHERE chat_id={message.chat.id}")
            user = cursor.fetchone()
    except sqlite3.Error as e:
        config.logger.error(f"Error while accessing the database: {e}")
        bot.send_message(message.chat.id, "Произошла ошибка при доступе к базе данных. Попробуйте позже.")
        return

    if not user:
        # Если данные пользователя не найдены, отправляем сообщение с просьбой выбрать данные
        bot.send_message(message.chat.id, "Пожалуйста, выберите направление, курс и группу с помощью команды /start")
        return

    # Получаем данные о группе из данных пользователя
    direction = user[2]
    course = user[3]
    group_name = user[4]

    # Получаем расписание для выбранной группы
    schedule = get_schedule(direction, course, group_name)

    if not schedule:
        # Если расписание не найдено, отправляем сообщение об ошибке
        bot.send_message(message.chat.id, "Расписание не найдено")
        return

    # Отправляем расписание пользователю
    bot.send_message(message.chat.id, schedule)

bot.infinity_polling(none_stop=True)
