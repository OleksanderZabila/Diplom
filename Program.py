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

def fetch_units():
    if connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT unit FROM unit")
            return [row[0] for row in cursor.fetchall()]
    return []

def fetch_providers():
    if connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT name_provider FROM provider")
            return [row[0] for row in cursor.fetchall()]
    return []

# Функція додавання товару
def add_product():
    def submit():
        name = name_entry.get()
        category = category_combobox.get()
        quantity = quantity_entry.get()
        unit = unit_combobox.get()
        selling_price = selling_price_entry.get()
        purchase_price = purchase_price_entry.get()
        provider = provider_combobox.get()
        description = description_entry.get("1.0", "end-1c")  # Виправлена помилка

        if not all([name, category, quantity, unit, selling_price, purchase_price, provider]):
            messagebox.showerror("Помилка", "Усі поля обов'язкові для заповнення!")
            return

        try:
            quantity = int(quantity)
            selling_price = float(selling_price)
            purchase_price = float(purchase_price)
        except ValueError:
            messagebox.showerror("Помилка", "Некоректні числові значення!")
            return

        if connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO goods (name_goods, id_category_goods, number_goods, units_goods, 
                                       selling_price_goods, purchase_price_goods, id_provider_goods, description_goods)
                    VALUES (
                        %s, (SELECT id_category FROM category WHERE name_category = %s),
                        %s, (SELECT unit FROM unit WHERE unit = %s),
                        %s, %s, (SELECT id_provider FROM provider WHERE name_provider = %s), %s)
                """, (name, category, quantity, unit, selling_price, purchase_price, provider, description))
                messagebox.showinfo("Успіх", "Товар додано успішно!")
                add_window.destroy()
                update_table()

    add_window = tk.Toplevel(program)
    add_window.title("Додати товар")
    add_window.geometry("720x200")  # Оптимальний розмір вікна

    frame = tk.Frame(add_window, padx=10, pady=10)
    frame.pack(fill="both", expand=True)

    # Верхній ряд
    tk.Label(frame, text="Назва товару:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
    name_entry = Entry(frame, width=20)
    name_entry.grid(row=0, column=1, padx=5, pady=2)

    tk.Label(frame, text="Категорія:").grid(row=0, column=2, sticky="w", padx=5, pady=2)
    category_combobox = ttk.Combobox(frame, values=fetch_categories(), width=20)
    category_combobox.grid(row=0, column=3, padx=5, pady=2)
    category_combobox.bind("<KeyRelease>", lambda event: filter_combobox(category_combobox, fetch_categories()))

    tk.Label(frame, text="Кількість:").grid(row=0, column=4, sticky="w", padx=5, pady=2)
    quantity_entry = Entry(frame, width=10)
    quantity_entry.grid(row=0, column=5, padx=5, pady=2)

    # Середній ряд
    tk.Label(frame, text="Одиниця вимірювання:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
    unit_combobox = ttk.Combobox(frame, values=fetch_units(), state="readonly", width=12)
    unit_combobox.grid(row=1, column=1, padx=5, pady=2)

    tk.Label(frame, text="Ціна продажу:").grid(row=1, column=2, sticky="w", padx=5, pady=2)
    selling_price_entry = Entry(frame, width=10)
    selling_price_entry.grid(row=1, column=3, padx=5, pady=2)

    tk.Label(frame, text="Ціна закупівлі:").grid(row=1, column=4, sticky="w", padx=5, pady=2)
    purchase_price_entry = Entry(frame, width=10)
    purchase_price_entry.grid(row=1, column=5, padx=5, pady=2)

    # Нижній ряд (Постачальник + Опис)
    tk.Label(frame, text="Постачальник:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
    provider_combobox = ttk.Combobox(frame, values=fetch_providers(), width=25)
    provider_combobox.grid(row=2, column=1, columnspan=2, padx=5, pady=2)
    provider_combobox.bind("<KeyRelease>", lambda event: filter_combobox(provider_combobox, fetch_providers()))

    tk.Label(frame, text="Опис товару:").grid(row=3, column=0, sticky="nw", padx=5, pady=2)
    description_entry = tk.Text(frame, width=65, height=3)  # Збільшено поле опису
    description_entry.grid(row=3, column=1, columnspan=5, padx=5, pady=2)

    # Кнопки
    button_frame = tk.Frame(frame)
    button_frame.grid(row=4, column=0, columnspan=6, pady=10)

    submit_button = Button(button_frame, text="Додати", command=submit, width=12)
    submit_button.pack(side="left", padx=5)

    cancel_button = Button(button_frame, text="Скасувати", command=add_window.destroy, width=12)
    cancel_button.pack(side="left", padx=5)

def add_settings():
    add_window_settings = tk.Toplevel(program)
    add_window_settings.title("Нaлаштування")
    add_window_settings.geometry("900x500")

    notebook = ttk.Notebook(add_window_settings)

    tab1 = ttk.Frame(notebook)  # Категорії
    tab2 = ttk.Frame(notebook)  # Клієнти
    tab3 = ttk.Frame(notebook)  # Звіт (поки не чіпаємо)
    tab4 = ttk.Frame(notebook)  # Постачальники
    tab5 = ttk.Frame(notebook)  # Одиниці
    tab6 = ttk.Frame(notebook)  # Списане

    # Додавання вкладок до `Notebook`
    notebook.add(tab1, text="Категорії")
    notebook.add(tab2, text="Клієнти")
    notebook.add(tab3, text="Звіт")
    notebook.add(tab4, text="Постачальники")
    notebook.add(tab5, text="Одиниці")
    notebook.add(tab6, text="Списане")


    notebook.pack(expand=True, fill="both")  # Робимо `Notebook` розтягнутим

    # Функції для отримання даних
    def fetch_categories():
        with connection.cursor() as cursor:
            cursor.execute("SELECT id_category, name_category FROM category")
            return cursor.fetchall()

    def fetch_clients():
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id_client, name_client, telephone_client, mail_client, 
                       legaladdress_client, legalforms_client, iban_client FROM client
            """)
            return cursor.fetchall()

    def fetch_providers():
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id_provider, name_provider, telephote_provider, mail_provider, 
                       menedger_provider, legaladdress_provider, legalform_provider, iban_provider 
                FROM provider
            """)
            return cursor.fetchall()

    def fetch_units():
        with connection.cursor() as cursor:
            cursor.execute("SELECT unit FROM unit")
            return cursor.fetchall()

    def fetch_winteff():
        with connection.cursor() as cursor:
            cursor.execute("""SELECT id_goods, name_goods, id_category_goods, number_goods, units_goods, 
                                Selling_price_goods, purchase_price_goods, id_provider_goods, description_goods
                            FROM goods""")
            return  cursor.fetchall()

    # Функція створення таблиці
    def create_table(tab, columns, fetch_function, add_function):
        frame = ttk.Frame(tab)
        frame.pack(expand=True, fill="both")

        tree = ttk.Treeview(frame, columns=columns, show="headings")

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150, anchor="center")

        tree.pack(expand=True, fill="both", side="top")

        def update_table():
            for row in tree.get_children():
                tree.delete(row)
            for row in fetch_function():
                tree.insert("", "end", values=row)

        update_table()  # Заповнюємо таблицю при створенні

        # Додаємо кнопку "Додати"
        add_button = tk.Button(frame, text="Додати", command=lambda: add_function(update_table))
        add_button.pack(pady=5)

        return tree

    # Функція для додавання нових записів
    def add_entry(title, fields, insert_query, update_func):
        add_window = tk.Toplevel(add_window_settings)
        add_window.title(title)
        add_window.geometry("400x300")

        entries = {}

        for i, field in enumerate(fields):
            tk.Label(add_window, text=field).grid(row=i, column=0, padx=10, pady=5, sticky="w")
            entry = tk.Entry(add_window, width=30)
            entry.grid(row=i, column=1, padx=10, pady=5)
            entries[field] = entry

        def save_entry():
            values = [entry.get() for entry in entries.values()]
            if not all(values):
                messagebox.showerror("Помилка", "Усі поля повинні бути заповнені!")
                return

            with connection.cursor() as cursor:
                cursor.execute(insert_query, values)
                connection.commit()

            messagebox.showinfo("Успіх", "Дані додано!")
            add_window.destroy()
            update_func()  # Оновлення таблиці

        tk.Button(add_window, text="Зберегти", command=save_entry).grid(row=len(fields), column=0, columnspan=2, pady=10)

    # Створюємо таблиці у вкладках
    create_table(
        tab1,
        ("ID", "Назва Категорії"),
        fetch_categories,
        lambda update: add_entry("Додати категорію", ["Назва Категорії"],
                                 "INSERT INTO category (name_category) VALUES (%s)", update)
    )

    create_table(
        tab2,
        ("ID", "Назва", "Телефон", "Email", "Юр. адреса", "Правова форма", "IBAN"),
        fetch_clients,
        lambda update: add_entry("Додати клієнта", ["Назва", "Телефон", "Email", "Юр. адреса", "Правова форма", "IBAN"],
                                 "INSERT INTO client (name_client, telephone_client, mail_client, legaladdress_client, legalforms_client, iban_client) VALUES (%s, %s, %s, %s, %s, %s)", update)
    )

    create_table(
        tab4,
        ("ID", "Назва", "Телефон", "Email", "Менеджер", "Юр. адреса", "Правова форма", "IBAN"),
        fetch_providers,
        lambda update: add_entry("Додати постачальника", ["Назва", "Телефон", "Email", "Менеджер", "Юр. адреса", "Правова форма", "IBAN"],
                                 "INSERT INTO provider (name_provider, telephone_provider, mail_provider, menedger_provider, legaladdress_provider, legalfrom_provider, iban_provider) VALUES (%s, %s, %s, %s, %s, %s, %s)", update)
    )

    create_table(
        tab5,
        ("Одиниця вимірювання",),
        fetch_units,
        lambda update: add_entry("Додати одиницю вимірювання", ["Одиниця вимірювання"],
                                 "INSERT INTO unit (unit) VALUES (%s)", update)
    )
    create_table(
        tab6,
        ("ID", "Назва товару", "Категорія", "Кількість", "Одиниці",
           "Ціна продажу", "Ціна закупівлі", "Постачальник","Опис товару", "Дії",),
        fetch_winteff,
        lambda update: add_entry("Видалить зі списаного", ["Видалення"],
                             "INSERT INTO unit (unit) VALUES (%s)", update)
    )
# Функція для фільтрації категорій і постачальників
def filter_combobox(combobox, data_source):
    search_text = combobox.get().lower()
    filtered_data = [item for item in data_source if search_text in item.lower()]
    combobox["values"] = filtered_data
    combobox.event_generate("<Down>")  # Автоматично відкриває список
def edit_product(product_id):
    def update_product():
        if not messagebox.askyesno("Підтвердження", "Ви впевнені, що хочете зберегти зміни?"):
            return

        new_name = name_entry.get()
        new_category = category_combobox.get()
        new_quantity = quantity_entry.get()
        new_unit = unit_combobox.get()
        new_selling_price = selling_price_entry.get()
        new_purchase_price = purchase_price_entry.get()
        new_provider = provider_combobox.get()
        new_description = description_entry.get("1.0", "end-1c")

        try:
            new_quantity = int(new_quantity)
            new_selling_price = float(new_selling_price)
            new_purchase_price = float(new_purchase_price)
        except ValueError:
            messagebox.showerror("Помилка", "Некоректні числові значення!")
            return

        if connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE goods 
                    SET name_goods=%s, id_category_goods=(SELECT id_category FROM category WHERE name_category=%s),
                        number_goods=%s, units_goods=(SELECT unit FROM unit WHERE unit=%s),
                        selling_price_goods=%s, purchase_price_goods=%s,
                        id_provider_goods=(SELECT id_provider FROM provider WHERE name_provider=%s),
                        description_goods=%s
                    WHERE id_goods=%s
                """, (new_name, new_category, new_quantity, new_unit, new_selling_price,
                      new_purchase_price, new_provider, new_description, product_id))
                connection.commit()
                messagebox.showinfo("Успіх", "Зміни успішно збережені!")
                edit_window.destroy()
                update_table()

    # Отримання поточних даних товару
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT name_goods, (SELECT name_category FROM category WHERE id_category=id_category_goods), 
                   number_goods, (SELECT unit FROM unit WHERE unit=units_goods),
                   selling_price_goods, purchase_price_goods, 
                   (SELECT name_provider FROM provider WHERE id_provider=id_provider_goods),
                   description_goods
            FROM goods WHERE id_goods=%s
        """, (product_id,))
        product_data = cursor.fetchone()

    if not product_data:
        messagebox.showerror("Помилка", "Не вдалося отримати дані товару!")
        return

    edit_window = tk.Toplevel(program)
    edit_window.title("Редагувати товар")
    edit_window.geometry("600x300")

    frame = tk.Frame(edit_window, padx=10, pady=10)
    frame.pack(fill="both", expand=True)

    # Поля для редагування (вже заповнені)
    tk.Label(frame, text="Назва товару:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
    name_entry = Entry(frame, width=20)
    name_entry.insert(0, product_data[0])
    name_entry.grid(row=0, column=1, padx=5, pady=2)

    tk.Label(frame, text="Категорія:").grid(row=0, column=2, sticky="w", padx=5, pady=2)
    category_combobox = ttk.Combobox(frame, values=fetch_categories(), width=20)
    category_combobox.set(product_data[1])
    category_combobox.grid(row=0, column=3, padx=5, pady=2)
    category_combobox.bind("<KeyRelease>", lambda event: filter_combobox(category_combobox, fetch_categories()))

    tk.Label(frame, text="Кількість:").grid(row=0, column=4, sticky="w", padx=5, pady=2)
    quantity_entry = Entry(frame, width=10)
    quantity_entry.insert(0, product_data[2])
    quantity_entry.grid(row=0, column=5, padx=5, pady=2)

    tk.Label(frame, text="Одиниця вимірювання:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
    unit_combobox = ttk.Combobox(frame, values=fetch_units(), state="readonly", width=12)
    unit_combobox.set(product_data[3])
    unit_combobox.grid(row=1, column=1, padx=5, pady=2)

    tk.Label(frame, text="Ціна продажу:").grid(row=1, column=2, sticky="w", padx=5, pady=2)
    selling_price_entry = Entry(frame, width=10)
    selling_price_entry.insert(0, product_data[4])
    selling_price_entry.grid(row=1, column=3, padx=5, pady=2)

    tk.Label(frame, text="Ціна закупівлі:").grid(row=1, column=4, sticky="w", padx=5, pady=2)
    purchase_price_entry = Entry(frame, width=10)
    purchase_price_entry.insert(0, product_data[5])
    purchase_price_entry.grid(row=1, column=5, padx=5, pady=2)

    tk.Label(frame, text="Постачальник:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
    provider_combobox = ttk.Combobox(frame, values=fetch_providers(), width=25)
    provider_combobox.set(product_data[6])
    provider_combobox.grid(row=2, column=1, columnspan=2, padx=5, pady=2)
    provider_combobox.bind("<KeyRelease>", lambda event: filter_combobox(provider_combobox, fetch_providers()))

    tk.Label(frame, text="Опис товару:").grid(row=3, column=0, sticky="nw", padx=5, pady=2)
    description_entry = tk.Text(frame, width=65, height=3)
    description_entry.insert("1.0", product_data[7])
    description_entry.grid(row=3, column=1, columnspan=5, padx=5, pady=2)

    # Кнопки
    button_frame = tk.Frame(frame)
    button_frame.grid(row=4, column=0, columnspan=6, pady=10)

    save_button = Button(button_frame, text="Зберегти", command=update_product, width=12)
    save_button.pack(side="left", padx=5)

    cancel_button = Button(button_frame, text="Скасувати", command=edit_window.destroy, width=12)
    cancel_button.pack(side="left", padx=5)

# Оновлення головної таблиці (додаємо поле "Опис товару" і кнопку редагування)
def update_table(category=None):
    for item in table.get_children():
        table.delete(item)

    with connection.cursor() as cursor:
        cursor.execute("SELECT id_goods, name_goods, id_category_goods, number_goods, units_goods, selling_price_goods, purchase_price_goods, id_provider_goods, description_goods FROM goods")
        for row in cursor.fetchall():
            table.insert("", "end", values=row)

    add_edit_button_to_table()


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

add_product_button = Button(upper_frame, text="Додати товар", command=add_product)
add_product_button.pack(side='right', padx=5)

settings_button = Button(upper_frame, text="Налаштування", command=add_settings)
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
    selected_index = category_listbox.curselection()
    if selected_index:
        selected = category_listbox.get(selected_index[0])
        category_entry.delete(0, tk.END)
        category_entry.insert(0, selected)
        update_table(category=selected)  # Передаємо параметр правильно
    else:
        update_table()  # Відображаємо всі товари

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
right_frame.pack(side='right', fill='both', expand=True, padx=10, pady=5)

columns = ("ID", "Назва товару", "Категорія", "Кількість", "Одиниці",
           "Ціна продажу", "Ціна закупівлі", "Постачальник","Опис товару", "Дії")

table = ttk.Treeview(right_frame, columns=columns, show="headings", height=15)
for col in columns:
    table.heading(col, text=col)
    table.column(col, anchor="center", width=130)

table.pack(fill="both", expand=True)

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

# Додаємо поведінку до існуючого search_entry
search_entry.bind("<FocusIn>", on_search_entry_focus_in)
search_entry.bind("<FocusOut>", on_search_entry_focus_out)
search_entry.bind("<KeyRelease>", on_search_entry_change)  # Залишаємо вашу функцію пошуку

update_table()
program.mainloop()

if connection:
    connection.close()
    print("[INFO] Підключення закрито")
