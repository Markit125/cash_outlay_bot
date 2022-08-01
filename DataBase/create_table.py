import psycopg2
import psycopg2.extras
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



def create_users_table():
    """ PostgreSQL database"""
    command = (
        """
        CREATE TABLE users (
            user_id         VARCHAR(20)     PRIMARY KEY,
            activity        SMALLINT,
            tags            VARCHAR(200),
            count_notes     NUMERIC(5, 0),
            buffer          VARCHAR(200)
        )
        """
    )

    conn = None
    try:
        conn = connect_to_base()
        with conn.cursor() as cur:
            cur.execute(command)

        conn.commit()
        print("\n[INFO] Table 'users' created sucessfully\n")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print("[INFO] Connection closed\n")

def create_notes_table():
    """ PostgreSQL database"""
    command = (
        """
        CREATE TABLE notes (
            id              SERIAL          PRIMARY KEY,
            name            VARCHAR(40)     NOT NULL,
            count           REAL            NOT NULL,
            price           MONEY           NOT NULL,
            tag             VARCHAR(15)             ,
            date            DATE     NOT NULL,
            fk_notes_users  VARCHAR(20) REFERENCES users(user_id)
        )
        """
    )

    conn = None
    try:
        conn = connect_to_base()
        with conn.cursor() as cur:
            cur.execute(command)

        conn.commit()
        print("\n[INFO] Table 'notes' created sucessfully\n")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print("[INFO] Connection closed\n")


def drop_tables():
    """ PostgreSQL database"""
    command_0 = "DROP TABLE notes;"
    command_1 = "DROP TABLE users;"

    conn = None
    try:
        conn = connect_to_base()
        with conn.cursor() as cur:
            cur.execute(command_0)
            print("\n[INFO] Table 'notes' dropped sucessfully\n")
            cur.execute(command_1)
            print("[INFO] Table 'users' dropped sucessfully\n")

        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print("[INFO] Connection closed\n")


if __name__ == '__main__':
    drop_tables()
    create_users_table()
    create_notes_table()