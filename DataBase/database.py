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
                        INSERT INTO users (user_id, activity, count_notes, buffer)
                        VALUES ('{id}', -1, 0, '|||')
                    """
                )
        conn.commit()
            
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
            buffer = cur.fetchone()['buffer'].split('|')
            buffer[position] = name
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
            command_2 = f"UPDATE users SET count_notes={count + 1}, buffer='|||' WHERE user_id='{id}'"
            cur.execute(command_2)
        conn.commit()
            
    except (Exception, psycopg2.DatabaseError) as error:
        print("def add_note(id):", error)
    finally:
        if conn is not None:
            conn.close()


def get_report(id, days_ago):
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
                return report

            report = ""
            for i in range(len(all_notes)):
                report += (f"{i} | {all_notes[i]['name']} | {all_notes[i]['count']} | "
                        f"{all_notes[i]['price']} | {all_notes[i]['date']}\n"
                )
            if ago_date == None:
                ago_date = all_notes[0]['date']
                
            return report, all_notes, (ago_date, now_date)
            
    except (Exception, psycopg2.DatabaseError) as error:
        print("def add_note(id):", error)
    finally:
        if conn is not None:
            conn.close()


if __name__ == '__main__':
    connect_to_base()