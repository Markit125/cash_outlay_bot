from aiogram.dispatcher.filters import Text
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from BotFunctions.keyboards import report_tag_keyboard, keyboard_add_purchase, keyboard_interval_of_query, keyboard_product_note_check, keyboard_tag, keyboard_weigth, keyboard_yes_no, remove_tag_keyboard
from BotFunctions.processing import get_new_tag, get_product_note_check, get_profile, is_positive_float_number
from Report.PDF import make_report_in_PDF

import DataBase.database as db
import enum

import os
from dotenv import load_dotenv

load_dotenv()
bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher(bot)

commands_view = open('TextFiles/send_commands.txt', 'r').read()


class Activity(enum.Enum):
    remove_tag = -4
    save_tag = -3
    create_report = -2
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


@dp.message_handler(commands="commands")
async def send_commands(msg: types.Message):
    await msg.answer(commands_view, parse_mode="html")


@dp.message_handler(commands="menu")
async def go_menu(msg: types.Message):
    id = msg.from_user.id
    db.check_in_base(id)
    db.change_activity(id, Activity.menu.value)
    db.clear_buffer(id)

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


@dp.message_handler(commands="remove_tags")
async def remove_tag_from_profile_interface(msg: types.Message):
    id = msg.from_user.id
    db.check_in_base(id)
    db.change_activity(id, Activity.remove_tag.value)
    user_data = db.get_data(id)
    if user_data == None:
        return
    tags = user_data['tags'].split('.')
    message = f"Нажмите на тег, чтобы удалить его\nВернуться в меню -> /menu"
    await msg.answer(message, parse_mode="html", reply_markup=remove_tag_keyboard(tags))


@dp.callback_query_handler(Text(startswith="tag_remove_"))
async def remove_tag_from_profile(call: types.CallbackQuery):
    id = call.from_user.id
    db.check_in_base(id)
    user_data = db.get_data(id)
    if user_data == None:
        return

    await call.message.delete()
    if Activity.remove_tag.value != user_data['activity']:
        await call.answer()
        return
        
    tag = call.data[11:]
    
    tags = db.remove_tag_from_user(id, tag)
    message = f'Тег {tag} удалён!\nВернуться в меню -> /menu'
    
    await call.message.answer(message, parse_mode="html", reply_markup=remove_tag_keyboard(tags))
    await call.answer()


@dp.callback_query_handler(Text(startswith="tag_report_"))
async def add_tag_to_report(call: types.CallbackQuery):
    
    await call.answer()
    id = call.from_user.id
    db.check_in_base(id)
    user_data = db.get_data(id)
    if user_data == None:
        return
    
    await call.message.delete()
    if Activity.create_report.value != user_data['activity']:
        return
        
    tag = call.data[11:]
    days_ago = int(user_data['buffer'].split('|')[0])

    message = f'Отчёт о покупках за '
    if days_ago == -1:
        message += '<b>все времена</b> '
    else:
        message += f'<b>{days_ago} суток</b> '
    if tag != 'empty':
        message += f'с тегом <b>{tag}</b> '
    message += 'будет готов через некоторое количество секунд'
    
    await call.message.answer(message, parse_mode="html")

    message, all_notes, (from_date, to_date) = db.get_report(id, days_ago, tag)
    await call.message.answer(message, parse_mode="html")

    wait_message = await call.message.answer('<b>Processing...</b>', parse_mode="html")
    make_report_in_PDF(id, all_notes, from_date, to_date)
    await bot.send_document(id, open(f'{id}.pdf', 'rb'), reply_markup=keyboard_add_purchase())
    await wait_message.delete()
    db.change_activity(id, Activity.menu.value)
    
    os.remove(f'{id}.pdf')
    

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

        db.add_to_buffer  (id, text,    Activity.product_count.value)
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
        
        message = "Назначте теги товару"
        await msg.answer(message, parse_mode="html", reply_markup=keyboard_tag(user_data['tags'], True))

    
    elif user_data['activity']    ==    Activity.product_tag.value and text == 'дальше':
        buffer = user_data['buffer'].split('|')
        db.change_activity(id,          Activity.product_tag.value + 1)
        
        message = f"Проверьте запись:\n{get_product_note_check(buffer)}"
        await msg.answer(message, parse_mode="html", reply_markup=keyboard_product_note_check())


    elif user_data['activity']    ==    Activity.product_tag.value:
        active_tags = user_data['buffer'].split('|')[-1]
        text = '-' if text == 'пропустить' else msg.text
        if len(active_tags) == 0:
            active_tags = text
        else:
            if text not in active_tags.split('.'):
                active_tags += f'.{text}'
        db.add_to_buffer(id, active_tags,      Activity.product_tag.value)
        if text != '-':
            message = f'Добавьте ещё тег или нажмите <b>Дальше</b>'
            await msg.answer(message, parse_mode="html", reply_markup=keyboard_tag(user_data['tags'], False, active_tags))

        else:
            db.change_activity(id,          Activity.product_tag.value + 1)
            buffer = user_data['buffer'].split('|')
            buffer[-1] = '-'
            message = f"Проверьте запись:\n{get_product_note_check(buffer)}"
            await msg.answer(message, parse_mode="html", reply_markup=keyboard_product_note_check())


    elif user_data['activity'] == Activity.product_checking.value and text in ('готово', 'да', 'нет'):
        db.add_note(id)
        message = "Запись успешно добавлена"
        
        active_tags = user_data['buffer'].split('|')[-1].split('.')
        user_tags = user_data['tags'].split('.')
        new_tag = get_new_tag(active_tags, user_tags)

        if active_tags != ['-'] and new_tag != None:
            db.change_activity(id, Activity.save_tag.value)
            message += f'\nСохранить тег {new_tag}?'
            await msg.answer(message, parse_mode="html", reply_markup=keyboard_yes_no())
        else:
            db.change_activity(id, Activity.menu.value)
            db.clear_buffer(id)
            await msg.answer(message, parse_mode="html", reply_markup=keyboard_add_purchase())


    elif user_data['activity'] == Activity.save_tag.value and text in ('да', 'нет'):
        active_tags = user_data['buffer'].split('|')[-1].split('.')
        user_tags = user_data['tags'].split('.')
        new_tag = get_new_tag(active_tags, user_tags)
        db.remove_active_tag(id, new_tag)
        
        message = f'Тег {new_tag} не сохранен'
        if text == 'да':
            message = db.save_tag(id, new_tag)

        new_tag = get_new_tag(active_tags, user_tags, 1)
        if new_tag != None:
            message += f'\nСохранить тег {new_tag}?'
            await msg.answer(message, parse_mode="html", reply_markup=keyboard_yes_no())
        else:
            db.change_activity(id, Activity.menu.value)
            db.clear_buffer(id)
            await msg.answer(message, parse_mode="html", reply_markup=keyboard_add_purchase())


    elif user_data['activity'] == Activity.menu.value and text == 'создать отчет':
        db.change_activity(id,    Activity.menu.value - 1)
        message = "Выберите временной интервал"
        await msg.answer(message, parse_mode="html", reply_markup=keyboard_interval_of_query())


    elif user_data['activity'] == Activity.create_report.value and text in ('неделя', 'месяц', 'все времена'):
        days_ago = -1
        if text == 'неделя':
            days_ago = 7
        elif text == 'месяц':
            days_ago = 30
        # elif text == 'все времена':
        #     days_ago = -1

        db.add_to_buffer(id, days_ago, 0)
        tags = user_data['tags'].split('.')
        
        message = f'Выберите покупки с каким тегом включать в отчёт'
        await msg.answer(message, parse_mode="html", reply_markup=report_tag_keyboard(tags))

        
    else:
        await msg.answer('Вернитесь в меню -> /menu')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)