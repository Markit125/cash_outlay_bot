
def is_positive_float_number(num):
    try:
        return float(num) > 0
    except:
        return False


def get_product_note_check(buffer):
    return '{} | {} шт. | {} руб. | {}'.format(buffer[0], buffer[1], buffer[2], ', '.join(buffer[3].split('.')))
    

def get_profile(user_data, username):
    return (f"Пользователь: @{username}\n"
            f"ID: {user_data['user_id']}\n"
            f"Количество записей: {user_data['count_notes']}\n"
            f"Ваши теги: {user_data['tags'].replace('.', ', ') if user_data['tags'] != None else '-'}"
    )

def get_new_tag(active_tags, user_tags, offset=0):
    for tag in active_tags:
        if tag not in user_tags:
            if offset:
                offset -= 1
                continue
            return tag
    return None