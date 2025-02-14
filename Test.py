import psycopg2
import tkinter as tk
from tkinter import ttk, Entry, Button, Listbox, messagebox
from config import host, user, password, db_name, port

# Підключення до бази даних
try:
    connection = psycopg2.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=db_name
    )
    connection.autocommit = True
    print("[INFO] Підключено до бази даних")
except Exception as _ex:
    print("[ERROR] Помилка підключення:", _ex)
    connection = None


# Функції отримання даних
def fetch_categories():
    if connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT name_category FROM category")
            return [row[0] for row in cursor.fetchall()]
    return []


# Отримуємо список категорій перед створенням UI
categories = fetch_categories()

# Головне вікно
program = tk.Tk()
program.title('Авто під ключ')
program.geometry('1300x600')
program.resizable(width=False, height=False)

# Верхнє меню
upper_frame = tk.Frame(program)
upper_frame.pack(fill='x', padx=10, pady=5)

search_label = tk.Label(upper_frame, text="Пошук за назвою:")
search_label.pack(side='left', padx=5)

search_entry = Entry(upper_frame, width=40)
search_entry.insert(0, "Введіть назву товару")
search_entry.pack(side='left', padx=5)

settings_button = Button(upper_frame, text="Налаштування", command=lambda: print("Налаштування"))
settings_button.pack(side='right', padx=5)

# Головний контейнер
main_frame = tk.Frame(program)
main_frame.pack(fill='both', expand=True)

# Ліва панель (Пошук категорій)
left_frame = tk.Frame(main_frame, width=300, bg="#f0f0f0")
left_frame.pack(side='left', fill='y')

filter_label = tk.Label(left_frame, text="Пошук за категорією:", bg="#f0f0f0")
filter_label.pack(pady=10, padx=10, anchor='w')


def update_category_list(event=None):
    """ Оновлює список категорій відповідно до введеного тексту або виводить всі, якщо поле порожнє """
    search_text = category_entry.get().strip().lower()
    category_listbox.delete(0, tk.END)

    if not search_text:  # Якщо поле пошуку порожнє, вивести всі товари
        for cat in categories:
            category_listbox.insert(tk.END, cat)
        update_table()  # Оновлюємо таблицю без фільтру
    else:
        for cat in categories:
            if search_text in cat.lower():
                category_listbox.insert(tk.END, cat)


def select_category(event):
    """ Оновлює таблицю при виборі категорії або показує всі товари, якщо поле порожнє """
    selected_index = category_listbox.curselection()

    if selected_index:
        selected = category_listbox.get(selected_index[0])
        category_entry.delete(0, tk.END)
        category_entry.insert(0, selected)
        update_table(selected)
    else:
        update_table()  # Відображаємо всі товари, якщо нічого не вибрано


category_entry = Entry(left_frame, width=30)
category_entry.insert(0, "Введіть категорію")
category_entry.bind("<FocusIn>", lambda event: category_entry.delete(0,
                                                                     tk.END) if category_entry.get() == "Введіть категорію" else None)
category_entry.bind("<FocusOut>",
                    lambda event: category_entry.insert(0, "Введіть категорію") if not category_entry.get() else None)
category_entry.bind("<KeyRelease>", update_category_list)
category_entry.pack(pady=5, padx=10, fill='x')

category_listbox = Listbox(left_frame, height=15)
category_listbox.pack(pady=5, padx=10, fill='both', expand=True)
category_listbox.bind("<<ListboxSelect>>", select_category)

# Оновлення списку категорій при старті
update_category_list()

# Права панель (Таблиця)
right_frame = tk.Frame(main_frame)
right_frame.pack(side='right', fill='both', expand=True, padx=10, pady=5)

columns = ("ID", "Назва товару", "Категорія", "Кількість", "Одиниці",
           "Ціна продажу", "Ціна закупівлі", "Постачальник", "Опис товару")

table = ttk.Treeview(right_frame, columns=columns, show="headings", height=15)
for col in columns:
    table.heading(col, text=col)
    table.column(col, anchor="center", width=130)

table.pack(fill="both", expand=True)


def update_table(category=None):
    """ Оновлює таблицю товарів, підтримуючи фільтр за категорією """
    table.delete(*table.get_children())  # Очищаємо таблицю

    query = """
        SELECT g.id_goods, g.name_goods, c.name_category, g.number_goods, u.unit, 
               g.selling_price_goods, g.purchase_price_goods, p.name_provider, g.description_goods
        FROM goods g
        JOIN category c ON g.id_category_goods = c.id_category
        JOIN provider p ON g.id_provider_goods = p.id_provider
        JOIN unit u ON g.units_goods = u.unit
    """
    params = ()

    if category:  # Якщо є фільтр за категорією
        query += " WHERE c.name_category = %s"
        params = (category,)

    if connection:
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            for row in cursor.fetchall():
                table.insert("", tk.END, values=row)


update_table()  # Завантажуємо всі товари при запуску

program.mainloop()

if connection:
    connection.close()
    print("[INFO] Підключення закрито")
