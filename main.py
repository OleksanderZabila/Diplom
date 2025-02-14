import psycopg2
from config import host, user, password, db_name, port  # Додаємо port

try:
    connection = psycopg2.connect(
        host=host,
        port=port,  # Вказуємо порт
        user=user,
        password=password,
        database=db_name
    )
    connection.autocommit = True

    with connection.cursor() as cursor:
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"SELECT version: {version[0]}")

    with connection.cursor() as cursor:
        cursor.execute(
            """SELECT * FROM public.category
ORDER BY id_category ASC  """
        )
        categories = cursor.fetchall()
        for row in categories:
            print(row)

except Exception as _ex:
    print("[INFO] Error:", _ex)
finally:
    try:
        if connection:
            connection.close()
            print("[INFO] Connection closed")
    except NameError:
        print("[INFO] Connection was not established")
