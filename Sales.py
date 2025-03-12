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

def update_table(category=None, name_filter=None):
    table.delete(*table.get_children())  # Очищуємо таблицю перед оновленням
    if connection:
        with connection.cursor() as cursor:
            query = """
                SELECT g.id_goods, g.name_goods, c.name_category, g.number_goods, u.unit, 
                       g.selling_price_goods, g.purchase_price_goods, p.name_provider, g.description_goods
                FROM goods g
                JOIN category c ON g.id_category_goods = c.id_category
                JOIN provider p ON g.id_provider_goods = p.id_provider
                JOIN unit u ON g.units_goods = u.unit
            """
            params = []

            if category:
                query += " WHERE c.name_category = %s"
                params.append(category)

            if name_filter:
                query += " AND g.name_goods ILIKE %s" if category else " WHERE g.name_goods ILIKE %s"
                params.append(f"%{name_filter}%")

            cursor.execute(query, params)

            for row in cursor.fetchall():
                table.insert("", tk.END, values=row)

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
    selected_index = category_listbox.curselection()
    if selected_index:
        selected = category_listbox.get(selected_index[0])
        category_entry.delete(0, tk.END)
        category_entry.insert(0, selected)
        update_table(category=selected)  # Передаємо параметр правильно
    else:
        update_table()  # Відображаємо всі товари

def fetch_categories():
    if connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT name_category FROM category")
            return [row[0] for row in cursor.fetchall()]
    return []

# Головне вікно
program = tk.Tk()
program.title('Авто під ключ')
program.geometry('1300x600')
program.resizable(width=False, height=False)

# Верхнє меню
upper_frame = tk.Frame(program)
upper_frame.pack(fill='x', padx=10, pady=5)

search_label = tk.Label(upper_frame, text="Фільтр за назвою:")
search_label.pack(side='left', padx=5)

search_entry = Entry(upper_frame, width=40)
search_entry.insert(0, "Введіть назву товару")
search_entry.pack(side='left', padx=5)


# Головний контейнер
main_frame = tk.Frame(program)
main_frame.pack(fill='both', expand=True)

# Ліва панель (Пошук категорій)
left_frame = tk.Frame(main_frame, width=300, bg="#f0f0f0")
left_frame.pack(side='left', fill='y')

filter_label = tk.Label(left_frame, text="Пошук за категорією:", bg="#f0f0f0")
filter_label.pack(pady=10, padx=10, anchor='w')

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

# Завантаження категорій
categories = fetch_categories()
update_category_list(None)

# Таблиця
right_frame = tk.Frame(main_frame)
right_frame.place(x=210, y=0, relwidth=0.83, height=250)

columns = ("ID", "Назва товару", "Категорія", "Кількість", "Одиниці",
           "Ціна продажу", "Ціна закупівлі", "Постачальник", "Опис товару", "Дії")

# Словник зі своїми ширинами для колонок
column_widths = {
    "ID": 30,
    "Назва товару": 150,
    "Категорія": 120,
    "Кількість": 80,
    "Одиниці": 80,
    "Ціна продажу": 100,
    "Ціна закупівлі": 100,
    "Постачальник": 150,
    "Опис товару": 200,
    "Дії": 50
}

table = ttk.Treeview(right_frame, columns=columns, show="headings", height=15)

for col in columns:
    table.heading(col, text=col)
    table.column(col, anchor="center", width=column_widths.get(col, 100))  # Використовуємо значення зі словника

table.pack(fill="both", expand=True)

down_frame = tk.Frame(main_frame)
down_frame.place(x=210, y=260, relwidth=0.50, height=300)

columns = ("ID", "Назва товару", "Кількість", "Одиниці","Ціна ",)

# Словник зі своїми ширинами для колонок
column_widths = {
    "ID": 30,
    "Назва товару": 150,
    "Кількість": 80,
    "Одиниці": 80,
    "Ціна ": 100,
}
table_down = ttk.Treeview(down_frame, columns=columns, show="headings", height=15)

for col in columns:
    table_down.heading(col, text=col)
    table_down.column(col, anchor="center", width=column_widths.get(col, 100))  # Використовуємо значення зі словника

table_down.pack(fill="both", expand=True)

def on_search_entry_change(event):
    name_filter = search_entry.get().strip()
    update_table(name_filter=name_filter)

search_entry.bind("<KeyRelease>", on_search_entry_change)

# Функція для очищення тексту при фокусі
def on_search_entry_focus_in(event):
    if search_entry.get() == "Введіть назву товару":
        search_entry.delete(0, tk.END)
        search_entry.config(fg="black")  # Робимо текст чорним

# Функція для повернення тексту, якщо поле залишилось порожнім
def on_search_entry_focus_out(event):
    if not search_entry.get():
        search_entry.insert(0, "Введіть назву товару")
        search_entry.config(fg="gray")  # Робимо текст сірим

search_entry.bind("<FocusIn>", on_search_entry_focus_in)
search_entry.bind("<FocusOut>", on_search_entry_focus_out)
search_entry.bind("<KeyRelease>", on_search_entry_change)  # Залишаємо вашу функцію пошуку

update_table()
program.mainloop()

if connection:
    connection.close()
    print("[INFO] Підключення закрито")
