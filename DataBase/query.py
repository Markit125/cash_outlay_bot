import psycopg2

import os
from dotenv import load_dotenv

def query():
    conn = None
    try:

        load_dotenv()
        host = os.getenv("HOST")
        user = os.getenv("USER")
        password = os.getenv("PASSWORD")
        db_name = os.getenv("DB_NAME")
        conn = psycopg2.connect(
                host=host,
                user=user,
                password=password,
                database=db_name,
            )

        command = input("Create query:\n")
        while command != '':
            # print(f'"{command}"')
            with conn.cursor() as cur:
                cur.execute(command)
                if "SELECT" in command.upper():
                    print(cur.fetchall())

            conn.commit()
            command = input("Create query:\n")
                
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print("[INFO] Connection closed\n")


if __name__ == '__main__':
    query()