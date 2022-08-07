from aiogram import types


def keyboard_add_purchase():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    key_report = types.InlineKeyboardButton(text='Создать отчет', callback_data='Создать отчет')
    key_add = types.InlineKeyboardButton(text='Добавить покупку', callback_data='Добавить покупку')
    keyboard.add(key_report, key_add)
    return keyboard


def keyboard_weigth():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    key_one_piece = types.InlineKeyboardButton(text='1', callback_data='1')
    keyboard.add(key_one_piece)
    return keyboard


def keyboard_tag(user_tags, skip, *active_tags):
    print('iebvfndsfvlksfnvjksnvjlknvjkvjjsfljfl;ajflk;jfljasl')
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, one_time_keyboard=True)
    if user_tags != None:
        user_tags = user_tags.split('.')
        keyboard_tags = user_tags[:]
        print(user_tags)
        if not skip:
            active_tags = active_tags[0].split('.')
            for tag in user_tags:
                print(f'\nif {tag} in {active_tags}')
                if tag in active_tags:
                    print('Ja')
                    keyboard_tags.remove(tag)
        tag_buttons = [
            types.InlineKeyboardButton(text=i, callback_data=i) for i in keyboard_tags if i != ' '
        ]
        keyboard.add(*tag_buttons)
    if skip:
        key_skip = types.InlineKeyboardButton(text='Пропустить', callback_data='-')
    else:
        key_skip = types.InlineKeyboardButton(text='Дальше', callback_data='Дальше')
    keyboard.add(key_skip)
    return keyboard


def keyboard_product_note_check():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    key_note_is_right = types.InlineKeyboardButton(text='Готово', callback_data='Готово')
    keyboard.add(key_note_is_right)
    return keyboard


def keyboard_interval_of_query():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    key_week = types.InlineKeyboardButton(text='Неделя', callback_data='Неделя')
    key_month = types.InlineKeyboardButton(text='Месяц', callback_data='Месяц')
    key_all_time = types.InlineKeyboardButton(text='Все времена', callback_data='Все времена')
    # key_custom = types.InlineKeyboardButton(text='Свой', callback_data='Свой')
    keyboard.add(key_week, key_month, key_all_time)
    return keyboard


def keyboard_yes_no():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    key_yes = types.InlineKeyboardButton(text='Да', callback_data='Да')
    key_no = types.InlineKeyboardButton(text='Нет', callback_data='Нет')
    keyboard.add(key_yes, key_no)
    return keyboard