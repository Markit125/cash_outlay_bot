
def is_positive_float_number(num):
    try:
        num = float(num)
        return num > 0
    except:
        return False


def get_product_note_check(buffer):
    return '{} | {} шт. | {} руб. | {}'.format(buffer[0], buffer[1], buffer[2], buffer[3])
    

def get_profile(user_data, username):
    return (f"Пользователь: @{username}\n"
            f"ID: {user_data['user_id']}\n"
            f"Количество записей: {user_data['count_notes']}\n"
            f"Ваши теги: {user_data['tags'] if user_data['tags'] != None else '-'}"
    )