import psycopg2
from config import host, user, password, db_name

def query():
    conn = None
    try:
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
                if "INSERT" not in command.upper():
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