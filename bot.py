import config
import logging
from datetime import date
import calendar
from datetime import timedelta
from aiogram import Bot, Dispatcher, executor, types

import sqlite3

# задаем уровень логов
logging.basicConfig(level=logging.INFO)

# инициализируем бота
bot = Bot(token=config.API_TOKEN)
dp = Dispatcher(bot)

# инициализируем соединение с БД и объект курсор
conn = sqlite3.connect('db.db')
cur = conn.cursor()

# получаем рассписание звонков
cur.execute("SELECT  пара From timetable_table ")
timetable = cur.fetchall()

# глобальные параметры
group = "group"
day_of_week = ""
my_date = date.today()
week = ((date.today()).strftime("%V"))


# кнопки дней недели
@dp.message_handler(commands="keyboard")
async def intro_function(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "сегодня", "завтра"]
    keyboard.add(*buttons)
    await message.answer("Добро пожаловать! Выберите день: ", reply_markup=keyboard)


@dp.message_handler()
async def message(message: types.Message):
    global group
    global day_of_week
    # если получаем день выводим рассписание
    cur.execute("Select day_of_week from day_of_week_table  where день_недели = ? or ДЕНЬ_НЕДЕЛИ = ?",
                (message.text, message.text))
    get_day_of_week = str(cur.fetchone())
    day_of_week = get_day_of_week[2:-3]
    if message.text == 'Сегодня' or message.text == 'сегодня':
        day_of_week = calendar.day_name[my_date.weekday()]
    if message.text == 'Завтра' or message.text == 'завтра':
        day_of_week = calendar.day_name[(my_date + timedelta(1)).weekday()]
    if group != "group" and day_of_week != "":
        if day_of_week == "Sunday":
            day_of_week = "Monday"
            await message.answer("будет показано рассписание на понедельник")
        cur.execute("SELECT  %s From auditory_table WHERE day_of_week = '%s' " % (group, day_of_week))
        res_auditory = cur.fetchall()
        cur.execute("SELECT  %s From Subject_table WHERE day_of_week = '%s' " % (group, day_of_week))
        res_subject = cur.fetchall()
        cur.execute("SELECT  %s From teacher_table WHERE day_of_week = '%s' " % (group, day_of_week))
        res_teacher = cur.fetchall()
        for item0, item1, item2, item3 in zip(timetable, res_subject, res_auditory, res_teacher):
            if str(item1[0]) != "None":
                await message.answer(str(item0[0]) + str(item1[0]) + "\n" + (str(item2[0]) + '\n' + str(item3[0])))
            else:
                continue
        if int(week) % 2 == 0:
            await message.answer("сейчас неделя над чертой")
        else:
            await message.answer("сейчас неделя над чертой")
        return

    # поиск пар преподователя
    if group != 'group':
        cur.execute("SELECT  para_num From teacher_table where %s Like '%s' " % (group, ('%' + message.text + '%')))
        res_teacher_find = cur.fetchall()
        for item4 in res_teacher_find:
            await message.answer(str(item4[0]))

    # поиск группы
    cur.execute(
        "Select group_lowercase from groups_table  where group_lowercase = ?  or group_uppercase = ? "
        "or group_uppercase1 = ? or group_lowercase1 = ? ",
        (message.text, message.text, message.text, message.text))
    get_groupe = str(cur.fetchone())
    if get_groupe != "None":
        group = get_groupe[2:-3]
        await message.answer("Группа успешна изменена")
    if group == "group":
        await message.answer("Выберите группу.Пример:по21")


# запускаем лонг поллинг
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
