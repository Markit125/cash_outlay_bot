import psycopg2
import psycopg2.extras
from datetime import datetime, timedelta

import os
from dotenv import load_dotenv


def connect_to_base():
    load_dotenv()
    host = os.getenv("HOST")
    user = os.getenv("USER")
    password = os.getenv("PASSWORD")
    db_name = os.getenv("DB_NAME")
    return psycopg2.connect(
                host=host,
                user=user,
                password=password,
                database=db_name,
                cursor_factory=psycopg2.extras.DictCursor
            )


def check_in_base(id):
    command = f"SELECT * FROM users WHERE user_id='{id}'"
    conn = None
    try:
        conn = connect_to_base()
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(command)
            if cur.fetchone() == None:
                print(id, type(id))
                cur.execute(
                    f"""
                        INSERT INTO users (user_id, activity, count_notes, buffer, tags)
                        VALUES ('{id}', -1, 0, '|||', '')
                    """
                )
        conn.commit()
        # remove_tag_from_user(id, ' ')

    except (Exception, psycopg2.DatabaseError) as error:
        print("def check_in_base(id): ", error)
    finally:
        if conn is not None:
            conn.close()


def get_data(id):
    command = f"SELECT * FROM users WHERE user_id='{id}'"
    conn = None
    try:
        conn = connect_to_base()
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(command)
            data = cur.fetchone()
            if data == None:
                return None
            return data
    
    except (Exception, psycopg2.DatabaseError) as error:
        print("def get_data(id):", error)
    finally:
        if conn is not None:
            conn.close()


def change_activity(id, num):
    command = f"UPDATE users SET activity='{num}' WHERE user_id='{id}'"
    conn = None
    try:
        conn = connect_to_base()
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(command)
        conn.commit()
            
    except (Exception, psycopg2.DatabaseError) as error:
        print("def change_activity(id, num):", error)
    finally:
        if conn is not None:
            conn.close()


def add_to_buffer(id, name, position):
    command_0 = f"SELECT buffer FROM users WHERE user_id='{id}'"
    conn = None
    try:
        conn = connect_to_base()
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(command_0)
            buffer = cur.fetchone()
            if buffer == None:
                return
            buffer = buffer['buffer'].split('|')
            buffer[position] = str(name)
            buffer = '|'.join(buffer)
            command_1 = f"UPDATE users SET buffer='{buffer}' WHERE user_id='{id}'"
            cur.execute(command_1)
        conn.commit()
        
    except (Exception, psycopg2.DatabaseError) as error:
        print("def add_to_buffer(id, name, position):", error)
    finally:
        if conn is not None:
            conn.close()


def add_note(id):
    now_date = datetime.now().strftime("%Y-%m-%d")
    command_0 = f"SELECT buffer, count_notes FROM users WHERE user_id='{id}'"
    
    conn = None
    try:
        conn = connect_to_base()
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(command_0)
            data = cur.fetchone()
            if data == None:
                return
            count = data['count_notes']
            buffer = data['buffer'].split('|')

            command_1 = (
                f"""
                    INSERT INTO notes (name, count, price, tag, date, fk_notes_users) \
                    VALUES ('{buffer[0]}', {buffer[1]}, {buffer[2]}, '{buffer[3]}', \
                            '{now_date}', '{id}')
                """
            )
            cur.execute(command_1)
            command_2 = f"UPDATE users SET count_notes={count + 1} WHERE user_id='{id}'"
            cur.execute(command_2)
        conn.commit()
            
    except (Exception, psycopg2.DatabaseError) as error:
        print("def add_note(id):", error)
    finally:
        if conn is not None:
            conn.close()


def add_from_qr(id, data):
    now_date = datetime.now().strftime("%Y-%m-%d")
    command_0 = f"SELECT count_notes FROM users WHERE user_id='{id}'"
    
    conn = None
    try:
        conn = connect_to_base()
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(command_0)
            user_data = cur.fetchone()
            print(user_data)
            if user_data == None:
                return
            count = user_data['count_notes']
            for item in data:
                command_1 = (
                    f"""
                        INSERT INTO notes (name, count, price, tag, date, fk_notes_users) \
                        VALUES ('{item['name']}', {item['quantity']}, {float(item['sum']) / 100}, '-', \
                                '{now_date}', '{id}')
                    """
                )
                cur.execute(command_1)
                count += 1
                
            command_2 = f"UPDATE users SET count_notes={count} WHERE user_id='{id}'"
            cur.execute(command_2)
        conn.commit()
            
    except (Exception, psycopg2.DatabaseError) as error:
        print("def add_note(id):", error)
    finally:
        if conn is not None:
            conn.close()


def get_report(id, days_ago, tag):
    now_date = datetime.now().strftime("%Y-%m-%d")
    ago_date = None
    if days_ago == -1:
        command =  f"SELECT * FROM notes WHERE '{id}'=fk_notes_users"
    else:
        d = datetime.now() - timedelta(days_ago)
        ago_date = d.strftime("%Y-%m-%d")
        command =  f"""
                        SELECT name, count, price, tag, date
                        FROM notes WHERE (date BETWEEN '{ago_date}' AND '{now_date}')
                        AND '{id}'=fk_notes_users
                    """
    
    conn = None
    try:
        conn = connect_to_base()
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(command)
            all_notes = cur.fetchall()
            
            if all_notes == []:
                report = "У вас нет ни одной записи за данный временной интервал!"
                # print('No notes\n\n\n\n')
                return report, 0, (0, 0)
            report = ''
            notes = []
            for i in range(len(all_notes)):
                if tag in all_notes[i]['tag'] or tag == 'empty':
                    report += (f"{i} | {all_notes[i]['name']} | {all_notes[i]['count']} | "
                            f"{all_notes[i]['price']} | {all_notes[i]['tag']} |{all_notes[i]['date']}\n"
                    )
                    notes.append(all_notes[i])
            if ago_date == None:
                ago_date = all_notes[0]['date']
                
            return report, notes, (ago_date, now_date)
            
    except (Exception, psycopg2.DatabaseError) as error:
        print("def get_report(id):", error)
        return 0, 0, (0, 0)
    # finally:
    #     if conn is not None:
    #         conn.close()


def save_tag(id, tag):
    print(tag)
    command_0 = f"SELECT tags FROM users WHERE user_id='{id}'"
    
    conn = None
    try:
        conn = connect_to_base()
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(command_0)
            tags = cur.fetchone()
            if tags == None:
                return
            tags = tags['tags']
            print(tags)
            if tags == '':
                tags = f'{tag}'
            else:
                tags += f'.{tag}'
            if len(tags) > 200:
                return 'Удалите лишние теги, память заполнена'
            command_1 = f"UPDATE users SET tags='{tags}' WHERE user_id='{id}'"
            cur.execute(command_1)
            
        conn.commit()
        return f'Тег {tag} успешно сохранён!'
            
    except (Exception, psycopg2.DatabaseError) as error:
        print("def save_tag(id):", error)
    finally:
        if conn is not None:
            conn.close()


def clear_buffer(id):
    command = f"UPDATE users SET buffer='|||' WHERE user_id='{id}'"
    conn = None
    try:
        conn = connect_to_base()
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(command)
        conn.commit()
            
    except (Exception, psycopg2.DatabaseError) as error:
        print("def clear_buffer(id):", error)
    finally:
        if conn is not None:
            conn.close()


def remove_active_tag(id, tag):
    command_0 = f"SELECT buffer FROM users WHERE user_id='{id}'"
    conn = None
    try:
        conn = connect_to_base()
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(command_0)
            buffer = cur.fetchone()
            if buffer == None:
                return
            buffer = buffer['buffer'].split('|')
            active_tags = buffer[-1].split('.')
            active_tags.remove(tag)
            buffer[-1] = '.'.join(active_tags)
            buffer = '|'.join(buffer)

            command_1 = f"UPDATE users SET buffer='{buffer}' WHERE user_id='{id}'"
            cur.execute(command_1)

        conn.commit()
            
    except (Exception, psycopg2.DatabaseError) as error:
        print("def remove_active_tag(id, tag):", error)
    finally:
        if conn is not None:
            conn.close()
            

def remove_tag_from_user(id, tag):
    command_0 = f"SELECT tags FROM users WHERE user_id='{id}'"
    conn = None
    try:
        conn = connect_to_base()
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(command_0)
            tags = cur.fetchone()
            if tags == None:
                return
            tags = tags['tags'].split('.')
            if tag in tags:
                tags.remove(tag)
            new_tags = '.'.join(tags)

            command_1 = f"UPDATE users SET tags='{new_tags}' WHERE user_id='{id}'"
            cur.execute(command_1)

        conn.commit()
        return tags
            
    except (Exception, psycopg2.DatabaseError) as error:
        print("def remove_tag_from_user(id, tag):", error)
    finally:
        if conn is not None:
            conn.close()


def get_note_with_position(id, position):
    command =  f"""
                    SELECT name, count, price, date
                    FROM notes WHERE '{id}'=fk_notes_users
                """
    
    conn = None
    try:
        conn = connect_to_base()
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(command)
            all_notes = cur.fetchall()
            
            if all_notes == []:
                note = "У вас нет ни одной записи за данный временной интервал!"
                # print('No notes\n\n\n\n')
                return note
            note = ''
            note_with_position = all_notes[-position]

            note += (f"{note_with_position['name']} | {note_with_position['count']} | "
                    f"{note_with_position['price']} | {note_with_position['date']}"
            )
            print(f'\nnote\n{note}')
            
            return note
            
    except (Exception, psycopg2.DatabaseError) as error:
        print("def get_note_with_position(id, position):", error)
        return -1
    # finally:
    #     if conn is not None:
    #         conn.close()


def update_tag(id, note, tags):
    data = note.split(' | ')
    print(f'\ndata\n{data}')
    print(f'\ntags\n{tags}')
    command =  f"""
                    UPDATE notes SET tag='{tags}'
                    WHERE name='{data[0]}' and count='{data[1]}' and price='{data[2]}' and date='{data[3]}'
                    and fk_notes_users='{id}'
                """
    
    conn = None
    try:
        conn = connect_to_base()
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(command)
        conn.commit()

            
    except (Exception, psycopg2.DatabaseError) as error:
        print("def update_tag(id, note, tags):", error)

    # finally:
    #     if conn is not None:
    #         conn.close()



if __name__ == '__main__':
    connect_to_base()