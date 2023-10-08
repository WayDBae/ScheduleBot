from bot import bot #импортируем объект бота
from messages import * #Импортируем всё с файла сообщений
import config
from telebot import types
from datetime import datetime

# Dictionary to store user data
user_data = {}
@bot.message_handler(commands=['start'])
def start_handler(message):
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
    week = ""
    # Получаем текущую дату
    current_date = datetime.now()

    # Проверяем четность недели
    week_parity = current_date.isocalendar()[1] % 2
    
    if week_parity == 0:
        week = "Числитель"
    else:  # Нечетная неделя
        week = "Знаменатель"
    
        # Отправляем сообщение с подтверждением выбранных данных
    selected_data = user_data[message.chat.id]
    start_message = f"""👋 Привет, {message.from_user.first_name}!

Вы выбрали:
Направление: {selected_data['direction']}
Курс: {selected_data['course']}
Группа: {selected_data['group']}

Текущая неделя: {week}


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
    if user_data[message.chat.id]["direction"] == "Информатика" and user_data[message.chat.id]['course'] == "2 курс" and user_data[message.chat.id]["group"] == "Группа Б":
        bot.send_message(message.chat.id, format_schedule(get_today_schedule()))
def get_today_schedule():
    current_day = datetime.now().strftime("%A")  # current_day получает ответ в виде дня недели на английском языке с помощью библиотеки datetime
    week_number = datetime.now().isocalendar()[1]
    if week_number % 2 == 0 and current_day in schedule2: # Если условие (деление номера недели на 2 без остатка) верно и в списке есть день, который совпадает с текущим,
        return schedule2[current_day]                     # функция вернёт ответ в виде списка Schedule 2
    elif current_day in schedule1:                        # Если условие деления не верно, функция вернёт ответ в виде списка Schedule 1
        return schedule1[current_day]
    else:                                                 # Если в списке нет текущего дня недели, функция вернёт пустой ответ
        return []

# Функция для форматированного вывода расписания в текстовом формате
def format_schedule(schedule):
    if not schedule:                                                     # Если функция get_today_schedule вернула пустой ответ,
        return "Сегодня пар нет!"                                        # функиця format_schedule вернёт ответ "Сегодня пар нет!"
    else:                                                                # Если функция get_today_schedule вернула ответ в виде одного из списков, format_schedule вернёт ответ в виде переменной result
        result = "Расписание на сегодня:\n"                              # переменная result имеет вид string (по русски = строка), Символ новой строки в Python — это \n . Он используется для обозначения окончания строки текста
        for lesson in schedule:                                          # for in - это цикл. Общий синтаксис for... in в python выглядит следующим образом: for <переменная> in <последовательность>:< действие> else:< действие>. 
            result += f"{lesson['Время']} - {lesson['Предмет']}\n"       # Элементы «последовательности» перебираются один за другим «переменной» цикла; если быть точным, переменная указывает на элементы.
        return result                                                    # "+-" - это инкрементальные конкатенации в цикле. Тема не самая простая, об этом позже. f-строки позволяют форматировать информацию в нужном нам виде

    
    
    
# Список с расписанием занятий (в моём случае списка 2, т.к. у меня есть неделя-числитель и знаменатель) Знаменатель = Schedule 2, Числитель  Schedule 1
schedule1 = {
    'Monday': [
        {'Время': '08:00-09:20', 'Предмет': 'Л-309, Автоматизация систем электроснабжения(лек)'}, # "перое знач.":"второе знач." - меняем только второе значение, под свои задачи. 
        {'Время': '09:30-10:50', 'Предмет': 'Л-301, Транспортная безопасность(пр)'},
        {'Время': '11:00-12:20', 'Предмет': 'Л-510, Телемеханизация в системе электроснабжения(доп)'}
    ],
    'Tuesday': [
        {'Время': '11:50', 'Предмет': 'А-413, Анализ и оценка деятельности предприятий (организаций) транспорта (доп.зан.)'},
        {'Время': '13:50', 'Предмет': 'Л-506, Электроснабжение железных дорог (пр)'},
        {'Время': '15:40', 'Предмет': 'Л-305, Экономика и управление проектами (пр)'},
        {'Время': '17:30', 'Предмет': 'А-222, Учет деятельности предприятий (организаций) транспорта (доп.зан.)'}
    ],
    'Wednesday': [
        {'Время': '09:50', 'Предмет': 'Л-409, Планирование деятельности предприятий (организаций) транспорта (доп.зан.)'},
        {'Время': '11:50', 'Предмет': 'Л-506, Электрические сети и системы (лек)'},
        {'Время': '13:50', 'Предмет': 'Л-502, Электроснабжение железных дорог (лек)'},
        {'Время': '15:40', 'Предмет': 'Л-512, Электроснабжение нетяговых потребителей (л/р)'}
    ],
    'Thursday': [
        {'Время': '09:50', 'Предмет': 'А-306, Инструменты финансового управления на транспорте (доп.зан.)'},
        {'Время': '11:50', 'Предмет': 'Т-44, Экономика предприятия (лек)'},
        {'Время': '13:50', 'Предмет': 'А-221, Экономика предприятия (пр)'}
    ],
    'Friday': [
        {'Время': '11:50', 'Предмет': 'Л Л-512, Автоматизация систем электроснабжения (л/р)'},
        {'Время': '13:50', 'Предмет': 'Л-510, Эксплуатация систем обеспечения движения поездов (лек)'},
        {'Время': '15:40', 'Предмет': 'Л-502, Эксплуатация систем обеспечения движения поездов (пр)'}
    ]
}

 # Дни недели можно удалять или добавлять. Главное сохранить синтаксис списка, не потерять символы. Название дня недели должно быть на английском языке.

schedule2 = {
    'Monday': [
        {'Время': '10:00', 'Предмет': 'Математика'},
        {'Время': '12:00', 'Предмет': 'Информатика'}
    ],
    'Tuesday': [
        {'Время': '14:57', 'Предмет': 'Физика'},
        {'Время': '14:59', 'Предмет': 'Иностранный язык'}
    ],
    'Wednesday': [
        {'Время': '09:00', 'Предмет': 'Физра'},
        {'Время': '13:00', 'Предмет': 'Математика'}
    ],
    'Thursday': [
        {'Время': '10:00', 'Предмет': 'Химия'},
        {'Время': '12:00', 'Предмет': 'География'}
    ],
    'Friday': [
        {'Время': '11:00', 'Предмет': 'Обществознание'},
        {'Время': '14:00', 'Предмет': 'Физкультура'}
    ]
}
bot.infinity_polling(none_stop=True)
