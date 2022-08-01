from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from BotFunctions.keyboards import keyboard_add_purchase, keyboard_interval_of_query, keyboard_product_note_check, keyboard_tag, keyboard_weigth
from BotFunctions.processing import get_product_note_check, get_profile, is_positive_float_number
from Report.PDF import make_report_in_PDF

import DataBase.database as db
import enum

import os
from dotenv import load_dotenv

load_dotenv()
bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher(bot)


class Activity(enum.Enum):
    create_query = -2
    menu = -1
    product_name = 0
    product_count = 1
    product_price = 2
    product_tag = 3
    product_checking = 4


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(msg: types.Message):
    id = msg.from_user.id
    db.check_in_base(id)
    db.change_activity(id, Activity.menu.value)

    message = f'Добрый день, {msg.from_user.first_name}'
    await msg.answer(message, parse_mode="html", reply_markup=keyboard_add_purchase())


@dp.message_handler(commands="menu")
async def go_menu(msg: types.Message):
    id = msg.from_user.id
    db.check_in_base(id)
    db.change_activity(id, Activity.menu.value)

    message = "Возврат в меню"
    await msg.answer(message, parse_mode="html", reply_markup=keyboard_add_purchase())


@dp.message_handler(commands="profile")
async def send_profile(msg: types.Message):
    id = msg.from_user.id
    db.check_in_base(id)
    db.change_activity(id, Activity.menu.value)
    user_data = db.get_data(id)
    if user_data == None:
        return

    message = get_profile(user_data, msg.from_user.username)
    await msg.answer(message, parse_mode="html", reply_markup=keyboard_add_purchase())


@dp.message_handler()
async def get_text_messages(msg: types.Message):
    text = msg.text.lower()
    id = msg.from_user.id
    user_data = db.get_data(id)
    print(user_data)

    if user_data == None:
        message = "Выполните команду /start"
        await msg.answer(message, parse_mode="html")


    elif user_data['activity'] == Activity.menu.value and text == 'добавить покупку':
        db.change_activity(id,    Activity.menu.value + 1)

        message = "Введите название товара"
        await msg.answer(message, parse_mode="html", reply_markup=types.ReplyKeyboardRemove())


    elif user_data['activity']    ==    Activity.product_name.value:
        db.add_to_buffer(id, msg.text,  Activity.product_name.value)
        db.change_activity(id,          Activity.product_name.value + 1)

        message = "Введите количество/вес"
        await msg.answer(message, parse_mode="html", reply_markup=keyboard_weigth())


    elif user_data['activity']    ==    Activity.product_count.value:
        text = text.replace(',', '.').replace(' ', '')
        if not is_positive_float_number(text):
            message = "Введите количество/вес\n(целое или дробное положительное число)"
            await msg.answer(message, parse_mode="html")
            return

        db.add_to_buffer(id, msg.text,  Activity.product_count.value)
        db.change_activity(id,          Activity.product_count.value + 1)
        
        message = "Введите цену за единицу товара"
        await msg.answer(message, parse_mode="html")


    elif user_data['activity']    ==    Activity.product_price.value:
        text = text.replace(',', '.').replace(' ', '')
        if not is_positive_float_number(text):
            message = "Введите цену за единицу товара\n(целое или дробное положительное число)"
            await msg.answer(message, parse_mode="html")
            return

        db.add_to_buffer(id, text,  Activity.product_price.value)
        db.change_activity(id,      Activity.product_price.value + 1)
        
        message = "Назначте тег товару"
        await msg.answer(message, parse_mode="html", reply_markup=keyboard_tag())

    
    elif user_data['activity']    ==    Activity.product_tag.value:
        buffer = user_data['buffer'].split('|')[:-1]
        text = '-' if text == 'пропустить' else msg.text
        buffer += [text]
        print(buffer)
        db.add_to_buffer(id, text,      Activity.product_tag.value)
        db.change_activity(id,          Activity.product_tag.value + 1)
        message = f"Проверьте запись:\n{get_product_note_check(buffer)}"
        await msg.answer(message, parse_mode="html", reply_markup=keyboard_product_note_check())


    elif user_data['activity'] == Activity.product_checking.value and text == 'готово':
        db.add_note(id)
        db.change_activity(id, Activity.menu.value)
        message = "Запись успешно добавлена"
        await msg.answer(message, parse_mode="html", reply_markup=keyboard_add_purchase())


    elif user_data['activity'] == Activity.menu.value and text == 'создать отчет':
        db.change_activity(id,    Activity.menu.value - 1)
        message = "Выберите временной интервал"
        await msg.answer(message, parse_mode="html", reply_markup=keyboard_interval_of_query())


    elif user_data['activity'] == Activity.create_query.value:
        if text == 'неделя':
            days_ago = 7
        elif text == 'месяц':
            days_ago = 30
        elif text == 'все времена':
            days_ago = -1
        else:
            await msg.answer('Не понимаю, что это значит.')
            return
        message, all_notes, (from_date, to_date) = db.get_report(id, days_ago)
        await msg.answer(message, parse_mode="html")
        make_report_in_PDF(id, all_notes, from_date, to_date)
        await msg.reply_document(open(f'{id}.pdf', 'rb'))
        os.remove(f'{id}.pdf')


    else:
        await msg.answer('Не понимаю, что это значит.')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)