import telebot
from threading import Timer
from datetime import datetime, timedelta
import requests

# Создаем экземпляр бота
bot = telebot.TeleBot("Ваш токен ")

API = '3bc01ac5bd3c54d9202761907c5e5283'

# Словари для хранения задач и напоминаний
user_tasks = {}
user_reminders = {}

# Команда /start
@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        f"Привет {message.from_user.first_name} ! Я твой To-Do бот с напоминаниями. Используй команды:\n"
        "/add [задача] - Добавить задачу\n"
        "/list - Посмотреть список задач\n"
        "/done [номер] - Удалить задачу\n"
        "/remind [задача] [время HH:MM] - Напомнить в указанное время\n"
        "/cancel [номер] - Отменить напоминание\n"
        "/reminders - Посмотреть активные напоминания\n"
        "/cody - Сайт с большим выбором курсов \n"
        "/weather - Узнать погоду в вашем городе "
    )

# Добавление задачи
@bot.message_handler(commands=["add"])
def add_task(message):
    user_id = message.chat.id
    task = message.text[5:].strip()

    if not task:
        bot.send_message(user_id, "Пожалуйста, укажите задачу после команды /add.")
        return

    user_tasks.setdefault(user_id, []).append(task)
    bot.send_message(user_id, f"Задача добавлена: {task}")

# Список задач
@bot.message_handler(commands=["list"])
def list_tasks(message):
    user_id = message.chat.id
    tasks = user_tasks.get(user_id, [])

    if not tasks:
        bot.send_message(user_id, "Ваш список задач пуст.")
    else:
        tasks_text = "\n".join([f"{i + 1}. {task}" for i, task in enumerate(tasks)])
        bot.send_message(user_id, f"Ваши задачи:\n{tasks_text}")

# Удаление задачи
@bot.message_handler(commands=["done"])
def done_task(message):
    user_id = message.chat.id
    tasks = user_tasks.get(user_id, [])

    if not tasks:
        bot.send_message(user_id, "Ваш список задач пуст.")
        return

    try:
        task_number = int(message.text[6:].strip()) - 1
        if task_number < 0 or task_number >= len(tasks):
            raise ValueError
        task = tasks.pop(task_number)
        bot.send_message(user_id, f"Задача выполнена: {task}")
    except (ValueError, IndexError):
        bot.send_message(user_id, "Пожалуйста, укажите правильный номер задачи после команды /done.")

# Напоминание
@bot.message_handler(commands=["remind"])
def remind(message):
    user_id = message.chat.id
    args = message.text[8:].strip().split(" ")

    if len(args) < 2:
        bot.send_message(user_id, "Пожалуйста, укажите задачу и время в формате HH:MM. Пример: /remind [задача] [время].")
        return

    try:
        task = " ".join(args[:-1])
        time_str = args[-1]
        reminder_time = datetime.strptime(time_str, "%H:%M").time()
        now = datetime.now()
        reminder_datetime = datetime.combine(now.date(), reminder_time)

        # Если время уже прошло, устанавливаем на следующий день
        if reminder_datetime < now:
            reminder_datetime += timedelta(days=1)

        delay = (reminder_datetime - now).total_seconds()

        # Создаем напоминание
        def send_reminder():
            bot.send_message(user_id, f"Напоминание: {task}")

        timer = Timer(delay, send_reminder)
        timer.start()

        # Сохраняем напоминание
        user_reminders.setdefault(user_id, []).append({"task": task, "time": reminder_datetime, "timer": timer})

        bot.send_message(user_id, f"Напоминание установлено: '{task}' в {reminder_time}.")
    except ValueError:
        bot.send_message(user_id, "Пожалуйста, укажите корректное время в формате HH:MM.")

# Список напоминаний
@bot.message_handler(commands=["reminders"])
def list_reminders(message):
    user_id = message.chat.id
    reminders = user_reminders.get(user_id, [])

    if not reminders:
        bot.send_message(user_id, "У вас нет активных напоминаний.")
    else:
        reminders_text = "\n".join(
            [f"{i + 1}. {reminder['task']} в {reminder['time'].strftime('%H:%M')}" for i, reminder in enumerate(reminders)]
        )
        bot.send_message(user_id, f"Ваши напоминания:\n{reminders_text}")

# Отмена напоминания
@bot.message_handler(commands=["cancel"])
def cancel_reminder(message):
    user_id = message.chat.id
    reminders = user_reminders.get(user_id, [])

    if not reminders:
        bot.send_message(user_id, "У вас нет активных напоминаний.")
        return

    try:
        reminder_number = int(message.text[8:].strip()) - 1
        if reminder_number < 0 or reminder_number >= len(reminders):
            raise ValueError

        reminder = reminders.pop(reminder_number)
        reminder["timer"].cancel()  # Останавливаем таймер
        bot.send_message(user_id, f"Напоминание отменено: {reminder['task']}")

        # Удаляем список напоминаний, если он пуст
        if not reminders:
            del user_reminders[user_id]

    except (ValueError, IndexError):
        bot.send_message(user_id, "Пожалуйста, укажите правильный номер напоминания. Команда: /cancel [номер].")

@bot.message_handler(commands=['gay'])
def gay(message):
    bot.send_message(message.chat.id , "https://www.youtubekids.com/")

@bot.message_handler(commands=["cody"])
def cody(message):
    bot.send_message(message.chat.id , "https://coddy.tech/courses")


@bot.message_handler(commands=['weather'])
def request_city(message):
    bot.send_message(message.chat.id, f'{message.from_user.first_name}, напиши название города, чтобы узнать погоду.')

@bot.message_handler(content_types=['text'])
def get_weather(message):
    city = message.text.strip().lower()
    url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API}&units=metric&lang=ru'
    
    try:
        res = requests.get(url)
        if res.status_code != 200:
            # Если API возвращает ошибку (например, город не найден)
            error_message = res.json().get("message", "Неизвестная ошибка.")
            bot.reply_to(message, "Не удалось найти команду")
            return
        
        data = res.json()
        # Проверяем, содержит ли ответ нужные данные
        if "main" in data and "temp" in data["main"] and "weather" in data:
            temp = data["main"]["temp"]
            weather_desc = data["weather"][0]["description"].capitalize()
            city_name = data.get("name", city.capitalize())
            bot.reply_to(
                message,
                f"Погода в городе {city_name}\n"
                f"Температура: {temp}°C\n"
                f"Описание: {weather_desc}"
            )
        else:
            bot.reply_to(message, "Не удалось получить корректные данные о погоде. Попробуйте позже.")
    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка при получении данных: {str(e)}")



# Запуск бота
bot.polling(none_stop=True)