import tkinter as tk
from tkinter import ttk, messagebox, filedialog, Toplevel
import mysql.connector
import datetime
import csv

# --- Constants for Styling ---
BG = "#0d1117"
FG = "#ffffff"
ACCENT = "#2196f3"
SUCCESS = "#28a745"
WARNING = "#ffc107"
DANGER = "#dc3545"
CARD_BG = "#161b22"
INPUT_BG = "#0d1117"
BORDER = "#30363d"

FONT_TITLE = ("Segoe UI", 18, "bold")
FONT_SUBTITLE = ("Segoe UI", 14, "bold")
FONT_TEXT = ("Segoe UI", 10)
FONT_SMALL = ("Segoe UI", 9)

BTN_STYLE = {
    "bg": CARD_BG,
    "fg": FG,
    "activebackground": ACCENT,
    "font": FONT_TEXT,
    "relief": "flat",
    "bd": 0,
    "padx": 15,
    "pady": 8
}

# --- Main Application Window Setup ---
root = tk.Tk()
root.title("MySQL Admin Pro")
root.geometry("1500x900")
root.configure(bg=BG)

# --- Console Log at the bottom ---
console_frame = tk.Frame(root, bg=BG, highlightbackground=BORDER, highlightthickness=1)
console_frame.pack(side="bottom", fill="x", padx=10, pady=10)
console_label = tk.Label(console_frame, text="📋 Console Log", bg=BG, fg=ACCENT, font=FONT_SUBTITLE)
console_label.pack(anchor="w", padx=10, pady=(5, 0))
console = tk.Text(console_frame, height=6, bg=INPUT_BG, fg="#00ff00", insertbackground="#00ff00", 
                  font=("Consolas", 9), relief="flat", bd=0)
console.pack(fill="x", padx=10, pady=(5, 10))

def log(msg, level="INFO"):
    time = datetime.datetime.now().strftime("%H:%M:%S")
    colors = {"INFO": "#00bfff", "SUCCESS": "#00ff00", "ERROR": "#ff4444", "RESULT": "#ffaa00"}
    console.insert("end", f"[{time}] [{level}] {msg}\n")
    console.see("end")

# --- Top Bar ---
topbar = tk.Frame(root, bg=CARD_BG, height=60, highlightbackground=BORDER, highlightthickness=1)
topbar.pack(side="top", fill="x")
topbar.pack_propagate(False)

title_label = tk.Label(topbar, text="🗄️ MySQL Admin Pro", bg=CARD_BG, fg=ACCENT, font=FONT_TITLE)
title_label.pack(side="left", padx=20, pady=10)

current_db = tk.StringVar(value="No Database Selected")
db_label = tk.Label(topbar, textvariable=current_db, bg=CARD_BG, fg=FG, font=FONT_TEXT)
db_label.pack(side="right", padx=20)

# --- Sidebar for Navigation ---
sidebar = tk.Frame(root, bg=CARD_BG, width=240, highlightbackground=BORDER, highlightthickness=1)
sidebar.pack(side="left", fill="y", padx=(10, 5), pady=10)
sidebar.pack_propagate(False)

tk.Label(sidebar, text="Navigation", bg=CARD_BG, fg=ACCENT, font=FONT_SUBTITLE).pack(pady=15)

# --- Content Area ---
content = tk.Frame(root, bg=BG)
content.pack(side="right", expand=True, fill="both", padx=(5, 10), pady=10)

conn = None

def clear_content():
    for widget in content.winfo_children():
        widget.destroy()

def create_card_frame(parent, title=None):
    """Create a styled card frame for better visual organization"""
    card = tk.Frame(parent, bg=CARD_BG, highlightbackground=BORDER, highlightthickness=1)
    if title:
        tk.Label(card, text=title, bg=CARD_BG, fg=ACCENT, font=FONT_SUBTITLE).pack(anchor="w", padx=15, pady=(10, 5))
        ttk.Separator(card, orient="horizontal").pack(fill="x", padx=15, pady=5)
    return card

def sidebar_button(label, cmd, icon=""):
    btn_frame = tk.Frame(sidebar, bg=CARD_BG)
    btn_frame.pack(fill="x", padx=10, pady=3)
    
    btn = tk.Button(btn_frame, text=f"{icon} {label}", command=cmd, 
                    bg=CARD_BG, fg=FG, activebackground=ACCENT, 
                    font=FONT_TEXT, anchor="w", relief="flat", bd=0, padx=15, pady=10)
    btn.pack(fill="x")
    
    def on_enter(e):
        btn.config(bg=ACCENT)
    def on_leave(e):
        btn.config(bg=CARD_BG)
    
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)

def style_widgets():
    style = ttk.Style()
    style.theme_use("default")
    
    style.configure("Treeview", background=INPUT_BG, foreground=FG, rowheight=28, 
                    fieldbackground=INPUT_BG, font=FONT_TEXT, borderwidth=0)
    style.configure("Treeview.Heading", background=CARD_BG, foreground=ACCENT, 
                    font=FONT_TEXT, relief="flat")
    style.map("Treeview", background=[("selected", ACCENT)])
    
    style.configure("TCombobox", fieldbackground=INPUT_BG, background=CARD_BG, 
                    foreground=FG, selectbackground=ACCENT, selectforeground=FG, 
                    borderwidth=1, relief="flat")
    style.map("TCombobox", fieldbackground=[("readonly", INPUT_BG)])
    style.map("TCombobox", background=[("readonly", CARD_BG)])

def styled_button(parent, text, command, bg=ACCENT, fg=BG):
    """Create a styled button"""
    btn = tk.Button(parent, text=text, command=command, bg=bg, fg=fg, 
                    font=FONT_TEXT, relief="flat", bd=0, padx=20, pady=10, cursor="hand2")
    
    def on_enter(e):
        btn.config(bg=lighten_color(bg))
    def on_leave(e):
        btn.config(bg=bg)
    
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    return btn

def lighten_color(color):
    """Simple color lightening for hover effect"""
    if color == ACCENT:
        return "#42a5f5"
    elif color == SUCCESS:
        return "#34ce57"
    elif color == DANGER:
        return "#e55353"
    return color

def styled_entry(parent, width=30, show=""):
    """Create a styled entry widget"""
    entry = tk.Entry(parent, width=width, show=show, bg=INPUT_BG, fg=FG, 
                     insertbackground=FG, font=FONT_TEXT, relief="flat", bd=2,
                     highlightbackground=BORDER, highlightthickness=1)
    return entry

def bind_enter_to_next(entries, final_button=None):
    for i, entry in enumerate(entries):
        if i < len(entries) - 1:
            entry.bind("<Return>", lambda event, next_entry=entries[i+1]: next_entry.focus_set())
        else:
            if final_button:
                entry.bind("<Return>", lambda event, btn=final_button: btn.invoke())

# --- Panel Functions ---

def show_login():
    clear_content()
    
    login_card = create_card_frame(content, "🔐 Login to MySQL")
    login_card.pack(pady=50, padx=100, fill="x")
    
    form_frame = tk.Frame(login_card, bg=CARD_BG)
    form_frame.pack(pady=20, padx=30)
    
    tk.Label(form_frame, text="Host:", bg=CARD_BG, fg=FG, font=FONT_TEXT).grid(row=0, column=0, sticky="e", padx=10, pady=10)
    host_entry = styled_entry(form_frame, width=35)
    host_entry.grid(row=0, column=1, pady=10)
    host_entry.insert(0, "localhost")
    
    tk.Label(form_frame, text="Username:", bg=CARD_BG, fg=FG, font=FONT_TEXT).grid(row=1, column=0, sticky="e", padx=10, pady=10)
    username_entry = styled_entry(form_frame, width=35)
    username_entry.grid(row=1, column=1, pady=10)
    
    tk.Label(form_frame, text="Password:", bg=CARD_BG, fg=FG, font=FONT_TEXT).grid(row=2, column=0, sticky="e", padx=10, pady=10)
    password_entry = styled_entry(form_frame, width=35, show="*")
    password_entry.grid(row=2, column=1, pady=10)
    
    show_var = tk.BooleanVar()
    def toggle_password():
        password_entry.config(show='' if show_var.get() else '*')
    
    tk.Checkbutton(form_frame, text="Show Password", variable=show_var, command=toggle_password,
                   bg=CARD_BG, fg=FG, activebackground=CARD_BG, selectcolor=INPUT_BG, 
                   font=FONT_SMALL).grid(row=3, column=1, sticky="w", pady=5)
    
    def attempt_login(event=None):
        global conn
        host = host_entry.get().strip()
        user = username_entry.get().strip()
        passwd = password_entry.get()
        try:
            conn = mysql.connector.connect(host=host, user=user, password=passwd, autocommit=False)
            log("✓ Login successful", "SUCCESS")
            load_db_panel()
        except mysql.connector.Error as err:
            messagebox.showerror("Login Failed", str(err))
            log(f"✗ Login failed: {err}", "ERROR")
    
    btn_frame = tk.Frame(login_card, bg=CARD_BG)
    btn_frame.pack(pady=20)
    login_btn = styled_button(btn_frame, "Login", attempt_login)
    login_btn.pack()
    
    bind_enter_to_next([host_entry, username_entry, password_entry], login_btn)

def load_db_panel():
    if conn is None or not conn.is_connected():
        messagebox.showwarning("Not Connected", "Please login to MySQL first.")
        show_login()
        return
    
    clear_content()
    
    # Create Database Card
    create_card = create_card_frame(content, "➕ Create New Database")
    create_card.pack(fill="x", padx=20, pady=10)
    
    create_frame = tk.Frame(create_card, bg=CARD_BG)
    create_frame.pack(pady=15, padx=20)
    
    tk.Label(create_frame, text="Database Name:", bg=CARD_BG, fg=FG, font=FONT_TEXT).pack(side="left", padx=5)
    db_name_entry = styled_entry(create_frame, width=35)
    db_name_entry.pack(side="left", padx=10)
    
    def create_database(event=None):
        dbname = db_name_entry.get().strip()
        if not dbname:
            messagebox.showwarning("Empty Name", "Please enter a database name.")
            return
        try:
            cursor = conn.cursor()
            cursor.execute(f"CREATE DATABASE `{dbname}`")
            conn.commit()
            log(f"✓ Database '{dbname}' created", "SUCCESS")
            refresh_db_list()
            db_name_entry.delete(0, 'end')
        except mysql.connector.Error as e:
            log(f"✗ Error creating DB: {e}", "ERROR")
            messagebox.showerror("Error", str(e))
    
    create_btn = styled_button(create_frame, "Create", create_database, bg=SUCCESS, fg=FG)
    create_btn.pack(side="left", padx=10)
    db_name_entry.bind("<Return>", lambda e: create_btn.invoke())
    
    # Manage Databases Card
    manage_card = create_card_frame(content, "📊 Manage Databases")
    manage_card.pack(fill="x", padx=20, pady=10)
    
    manage_frame = tk.Frame(manage_card, bg=CARD_BG)
    manage_frame.pack(pady=15, padx=20)
    
    tk.Label(manage_frame, text="Select Database:", bg=CARD_BG, fg=FG, font=FONT_TEXT).pack(side="left", padx=5)
    db_list_combo = ttk.Combobox(manage_frame, state="readonly", font=FONT_TEXT, width=35)
    db_list_combo.pack(side="left", padx=10)
    
    def switch_database(event=None):
        selected_db = db_list_combo.get().strip()
        if selected_db:
            try:
                conn.database = selected_db
                current_db.set(f"📁 Database: {selected_db}")
                log(f"Switched to database: {selected_db}", "INFO")
            except mysql.connector.Error as e:
                log(f"✗ Error switching DB: {e}", "ERROR")
                messagebox.showerror("Error", str(e))
    
    db_list_combo.bind("<<ComboboxSelected>>", switch_database)
    
    def drop_selected_db():
        db = db_list_combo.get().strip()
        if not db:
            messagebox.showwarning("Select DB", "Please select a database to drop.")
            return
        confirm = messagebox.askyesno("Confirm Drop", f"Are you sure you want to DROP database '{db}'?")
        if confirm:
            try:
                cursor = conn.cursor()
                cursor.execute(f"DROP DATABASE `{db}`")
                conn.commit()
                log(f"✓ Dropped database: {db}", "SUCCESS")
                refresh_db_list()
                current_db.set("No Database Selected")
            except mysql.connector.Error as e:
                log(f"✗ Error dropping DB: {e}", "ERROR")
                messagebox.showerror("Error", str(e))
    
    styled_button(manage_frame, "Drop Database", drop_selected_db, bg=DANGER, fg=FG).pack(side="left", padx=5)
    
    def refresh_db_list():
        try:
            cursor = conn.cursor()
            cursor.execute("SHOW DATABASES")
            dbs = [row[0] for row in cursor.fetchall()]
            db_list_combo['values'] = dbs
            
            if conn.database and conn.database in dbs:
                db_list_combo.set(conn.database)
            elif dbs:
                db_list_combo.set(dbs[0])
                switch_database()
            else:
                db_list_combo.set("")
                current_db.set("No Database Selected")
        except mysql.connector.Error as e:
            log(f"✗ Error fetching DBs: {e}", "ERROR")
            messagebox.showerror("Error", str(e))
    
    refresh_db_list()

def from_table_panel():
    if conn is None or not conn.is_connected():
        messagebox.showwarning("Not Connected", "Please login to MySQL first.")
        show_login()
        return
    if not conn.database:
        messagebox.showwarning("No Database Selected", "Please select a database first.")
        load_db_panel()
        return
    
    clear_content()
    
    # Create Table Card
    create_card = create_card_frame(content, "➕ Create New Table")
    create_card.pack(fill="x", padx=20, pady=10)
    
    table_frame = tk.Frame(create_card, bg=CARD_BG)
    table_frame.pack(pady=10, padx=20, fill="x")
    
    tk.Label(table_frame, text="Table Name:", bg=CARD_BG, fg=FG, font=FONT_TEXT).pack(side="left", padx=5)
    table_name_entry = styled_entry(table_frame, width=35)
    table_name_entry.pack(side="left", padx=10)
    
    # Scrollable field frame
    canvas_frame = tk.Frame(create_card, bg=CARD_BG, height=200)
    canvas_frame.pack(fill="both", padx=20, pady=10)
    
    canvas = tk.Canvas(canvas_frame, bg=CARD_BG, highlightthickness=0)
    scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
    field_frame = tk.Frame(canvas, bg=CARD_BG)
    
    canvas.create_window((0, 0), window=field_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    field_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    
    field_rows = []
    
    # Header
    header_frame = tk.Frame(field_frame, bg=CARD_BG)
    header_frame.pack(fill="x", pady=5)
    tk.Label(header_frame, text="Column Name", bg=CARD_BG, fg=ACCENT, font=FONT_TEXT, width=15).pack(side="left", padx=5)
    tk.Label(header_frame, text="Data Type", bg=CARD_BG, fg=ACCENT, font=FONT_TEXT, width=12).pack(side="left", padx=5)
    tk.Label(header_frame, text="Len", bg=CARD_BG, fg=ACCENT, font=FONT_TEXT, width=5).pack(side="left", padx=2)
    tk.Label(header_frame, text="PK", bg=CARD_BG, fg=ACCENT, font=FONT_TEXT, width=3).pack(side="left", padx=2)
    tk.Label(header_frame, text="NN", bg=CARD_BG, fg=ACCENT, font=FONT_TEXT, width=3).pack(side="left", padx=2)
    tk.Label(header_frame, text="UQ", bg=CARD_BG, fg=ACCENT, font=FONT_TEXT, width=3).pack(side="left", padx=2)
    
    def add_field_row(event=None):
        row_frame = tk.Frame(field_frame, bg=INPUT_BG, highlightbackground=BORDER, highlightthickness=1)
        row_frame.pack(fill="x", pady=3, padx=5)
        
        fname_entry = styled_entry(row_frame, width=15)
        fname_entry.pack(side="left", padx=5, pady=5)
        
        ftype_combo = ttk.Combobox(row_frame, values=["INT", "VARCHAR", "TEXT", "FLOAT", "DOUBLE", 
                                                       "DATE", "DATETIME", "CHAR", "BIGINT", "DECIMAL"], 
                                   width=12, font=FONT_TEXT)
        ftype_combo.set("VARCHAR")
        ftype_combo.pack(side="left", padx=5)
        
        length_entry = styled_entry(row_frame, width=5)
        
        pk_var = tk.IntVar()
        nn_var = tk.IntVar()
        uq_var = tk.IntVar()
        
        def toggle_length_entry(event=None):
            selected_type = ftype_combo.get()
            if selected_type in ["VARCHAR", "CHAR"]:
                length_entry.pack(side="left", padx=2)
                length_entry.bind("<Return>", add_field_row)
            else:
                length_entry.pack_forget()
                ftype_combo.bind("<Return>", add_field_row)
            
            fname_entry.bind("<Return>", lambda e: ftype_combo.focus_set())
            ftype_combo.bind("<<ComboboxSelected>>", toggle_length_entry)
        
        ftype_combo.bind("<<ComboboxSelected>>", toggle_length_entry)
        toggle_length_entry()
        
        tk.Checkbutton(row_frame, variable=pk_var, bg=INPUT_BG, selectcolor=INPUT_BG,fg=FG).pack(side="left", padx=8)
        tk.Checkbutton(row_frame, variable=nn_var, bg=INPUT_BG, selectcolor=INPUT_BG,fg=FG).pack(side="left", padx=8)
        tk.Checkbutton(row_frame, variable=uq_var, bg=INPUT_BG, selectcolor=INPUT_BG,fg=FG).pack(side="left", padx=8)
        
        field_rows.append((fname_entry, ftype_combo, length_entry, pk_var, nn_var, uq_var, row_frame))
        fname_entry.focus_set()
    
    def create_table():
        name = table_name_entry.get().strip()
        if not name:
            messagebox.showwarning("Empty Name", "Table name cannot be empty.")
            return
        
        fields = []
        for fname_entry, ftype_combo, length_entry, pk_var, nn_var, uq_var, _ in field_rows:
            col = fname_entry.get().strip()
            typ = ftype_combo.get().strip()
            length = length_entry.get().strip()
            
            if not col or not typ:
                continue
            
            full_typ = typ
            if typ in ["VARCHAR", "CHAR"]:
                if length.isdigit() and int(length) > 0:
                    full_typ = f"{typ}({length})"
                else:
                    messagebox.showwarning("Invalid Length", f"Please enter valid length for {typ} column '{col}'.")
                    return
            
            parts = [f"`{col}` {full_typ}"]
            if pk_var.get():
                parts.append("PRIMARY KEY")
            if nn_var.get():
                parts.append("NOT NULL")
            if uq_var.get():
                parts.append("UNIQUE")
            fields.append(" ".join(parts))
        
        if not fields:
            messagebox.showerror("Missing Fields", "Please define at least one column.")
            return
        
        create_stmt = f"CREATE TABLE `{name}` (\n  " + ",\n  ".join(fields) + "\n);"
        
        try:
            cursor = conn.cursor()
            cursor.execute(create_stmt)
            conn.commit()
            log(f"✓ Table '{name}' created", "SUCCESS")
            table_name_entry.delete(0, 'end')
            for _, _, _, _, _, _, r_frame in field_rows:
                r_frame.destroy()
            field_rows.clear()
            add_field_row()
            refresh_table_list()
        except mysql.connector.Error as e:
            log(f"✗ Error creating table: {e}", "ERROR")
            messagebox.showerror("Error", str(e))
    
    btn_frame = tk.Frame(create_card, bg=CARD_BG)
    btn_frame.pack(pady=15)
    
    styled_button(btn_frame, "+ Add Column", add_field_row, bg=CARD_BG, fg=ACCENT).pack(side="left", padx=5)
    create_table_btn = styled_button(btn_frame, "Create Table", create_table, bg=SUCCESS, fg=FG)
    create_table_btn.pack(side="left", padx=5)
    
    add_field_row()
    table_name_entry.bind("<Return>", lambda e: field_rows[0][0].focus_set() if field_rows else None)
    
    # Manage Tables Card
    manage_card = create_card_frame(content, "🔧 Manage Tables")
    manage_card.pack(fill="x", padx=20, pady=10)
    
    manage_frame = tk.Frame(manage_card, bg=CARD_BG)
    manage_frame.pack(pady=15, padx=20)
    
    tk.Label(manage_frame, text="Select Table:", bg=CARD_BG, fg=FG, font=FONT_TEXT).pack(side="left", padx=5)
    table_combo = ttk.Combobox(manage_frame, state="readonly", width=30, font=FONT_TEXT)
    table_combo.pack(side="left", padx=10)
    
    def refresh_table_list():
        try:
            cursor = conn.cursor()
            cursor.execute("SHOW TABLES")
            tables = [row[0] for row in cursor.fetchall()]
            table_combo['values'] = tables
            if tables:
                table_combo.set(tables[0])
            else:
                table_combo.set("")
        except mysql.connector.Error as e:
            log(f"✗ Error loading tables: {e}", "ERROR")
            messagebox.showerror("Error", str(e))
    
    def drop_table():
        tbl = table_combo.get().strip()
        if not tbl:
            messagebox.showwarning("Select Table", "Please select a table to drop.")
            return
        confirm = messagebox.askyesno("Confirm Drop", f"Drop table '{tbl}'?")
        if confirm:
            try:
                cursor = conn.cursor()
                cursor.execute(f"DROP TABLE `{tbl}`")
                conn.commit()
                log(f"✓ Table '{tbl}' dropped", "SUCCESS")
                refresh_table_list()
            except mysql.connector.Error as e:
                log(f"✗ Error dropping table: {e}", "ERROR")
                messagebox.showerror("Error", str(e))
    
    def rename_table():
        tbl = table_combo.get().strip()
        if not tbl:
            messagebox.showwarning("Select Table", "Please select a table to rename.")
            return
        
        new_name = tk.simpledialog.askstring("Rename Table", f"Enter new name for table '{tbl}':")
        if new_name and new_name.strip():
            try:
                cursor = conn.cursor()
                cursor.execute(f"RENAME TABLE `{tbl}` TO `{new_name.strip()}`")
                conn.commit()
                log(f"✓ Table renamed from '{tbl}' to '{new_name.strip()}'", "SUCCESS")
                refresh_table_list()
            except mysql.connector.Error as e:
                log(f"✗ Error renaming table: {e}", "ERROR")
                messagebox.showerror("Error", str(e))
    
    def manage_columns():
        tbl = table_combo.get().strip()
        if not tbl:
            messagebox.showwarning("Select Table", "Please select a table first.")
            return
        show_column_manager(tbl)
    
    styled_button(manage_frame, "Manage Columns", manage_columns, bg=ACCENT, fg=FG).pack(side="left", padx=5)
    styled_button(manage_frame, "Rename Table", rename_table, bg=WARNING, fg=BG).pack(side="left", padx=5)
    styled_button(manage_frame, "Drop Table", drop_table, bg=DANGER, fg=FG).pack(side="left", padx=5)
    
    refresh_table_list()

def show_column_manager(table_name):
    """Advanced column management window"""
    col_window = Toplevel(root)
    col_window.title(f"Column Manager - {table_name}")
    col_window.geometry("900x600")
    col_window.configure(bg=BG)
    
    title = tk.Label(col_window, text=f"🔧 Managing Columns for: {table_name}", 
                     bg=BG, fg=ACCENT, font=FONT_TITLE)
    title.pack(pady=15)
    
    # Treeview for columns
    tree_frame = tk.Frame(col_window, bg=BG)
    tree_frame.pack(fill="both", expand=True, padx=20, pady=10)
    
    columns = ("Field", "Type", "Null", "Key", "Default", "Extra")
    tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=10)
    
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=140)
    
    vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=vsb.set)
    
    tree.pack(side="left", fill="both", expand=True)
    vsb.pack(side="right", fill="y")
    
    def refresh_columns():
        for item in tree.get_children():
            tree.delete(item)
        try:
            cursor = conn.cursor()
            cursor.execute(f"DESCRIBE `{table_name}`")
            for row in cursor.fetchall():
                tree.insert("", "end", values=row)
        except mysql.connector.Error as e:
            messagebox.showerror("Error", str(e))
    
    refresh_columns()
    
    # Action buttons
    btn_frame = tk.Frame(col_window, bg=BG)
    btn_frame.pack(pady=15)
    
    def add_column():
        add_win = Toplevel(col_window)
        add_win.title("Add Column")
        add_win.geometry("500x400")
        add_win.configure(bg=BG)
        
        tk.Label(add_win, text="Add New Column", bg=BG, fg=ACCENT, font=FONT_SUBTITLE).pack(pady=15)
        
        form = tk.Frame(add_win, bg=BG)
        form.pack(pady=10, padx=20)
        
        tk.Label(form, text="Column Name:", bg=BG, fg=FG, font=FONT_TEXT).grid(row=0, column=0, sticky="e", padx=10, pady=10)
        col_name = styled_entry(form, width=25)
        col_name.grid(row=0, column=1, pady=10)
        
        tk.Label(form, text="Data Type:", bg=BG, fg=FG, font=FONT_TEXT).grid(row=1, column=0, sticky="e", padx=10, pady=10)
        col_type = ttk.Combobox(form, values=["INT", "VARCHAR", "TEXT", "FLOAT", "DOUBLE", "DATE", "DATETIME", "CHAR", "BIGINT", "DECIMAL"], width=23)
        col_type.set("VARCHAR")
        col_type.grid(row=1, column=1, pady=10)
        
        tk.Label(form, text="Length:", bg=BG, fg=FG, font=FONT_TEXT).grid(row=2, column=0, sticky="e", padx=10, pady=10)
        col_length = styled_entry(form, width=25)
        col_length.grid(row=2, column=1, pady=10)
        
        tk.Label(form, text="Position:", bg=BG, fg=FG, font=FONT_TEXT).grid(row=3, column=0, sticky="e", padx=10, pady=10)
        position_var = tk.StringVar(value="LAST")
        position_frame = tk.Frame(form, bg=BG)
        position_frame.grid(row=3, column=1, pady=10)
        tk.Radiobutton(position_frame, text="First", variable=position_var, value="FIRST", bg=BG, fg=FG, selectcolor=INPUT_BG).pack(side="left")
        tk.Radiobutton(position_frame, text="Last", variable=position_var, value="LAST", bg=BG, fg=FG, selectcolor=INPUT_BG).pack(side="left")
        tk.Radiobutton(position_frame, text="After:", variable=position_var, value="AFTER", bg=BG, fg=FG, selectcolor=INPUT_BG).pack(side="left")
        
        after_col = ttk.Combobox(form, width=23)
        after_col.grid(row=4, column=1, pady=5)
        try:
            cursor = conn.cursor()
            cursor.execute(f"DESCRIBE `{table_name}`")
            after_col['values'] = [row[0] for row in cursor.fetchall()]
        except:
            pass
        
        tk.Label(form, text="Default Value:", bg=BG, fg=FG, font=FONT_TEXT).grid(row=5, column=0, sticky="e", padx=10, pady=10)
        default_val = styled_entry(form, width=25)
        default_val.grid(row=5, column=1, pady=10)
        
        not_null_var = tk.BooleanVar()
        tk.Checkbutton(form, text="NOT NULL", variable=not_null_var, bg=BG, fg=FG, selectcolor=INPUT_BG).grid(row=6, column=1, sticky="w", pady=5)
        
        def execute_add():
            name = col_name.get().strip()
            dtype = col_type.get().strip()
            length = col_length.get().strip()
            
            if not name or not dtype:
                messagebox.showwarning("Missing Info", "Column name and type required.")
                return
            
            full_type = dtype
            if dtype in ["VARCHAR", "CHAR"] and length:
                full_type = f"{dtype}({length})"
            
            sql = f"ALTER TABLE `{table_name}` ADD COLUMN `{name}` {full_type}"
            
            if not_null_var.get():
                sql += " NOT NULL"
            
            if default_val.get().strip():
                sql += f" DEFAULT '{default_val.get().strip()}'"
            
            pos = position_var.get()
            if pos == "FIRST":
                sql += " FIRST"
            elif pos == "AFTER" and after_col.get():
                sql += f" AFTER `{after_col.get()}`"
            
            try:
                cursor = conn.cursor()
                cursor.execute(sql)
                conn.commit()
                log(f"✓ Column '{name}' added to '{table_name}'", "SUCCESS")
                refresh_columns()
                add_win.destroy()
            except mysql.connector.Error as e:
                log(f"✗ Error adding column: {e}", "ERROR")
                messagebox.showerror("Error", str(e))
        
        styled_button(add_win, "Add Column", execute_add, bg=SUCCESS, fg=FG).pack(pady=20)
    
    def modify_column():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a column to modify.")
            return
        
        old_col_name = tree.item(selected[0])['values'][0]
        
        mod_win = Toplevel(col_window)
        mod_win.title("Modify Column")
        mod_win.geometry("500x400")
        mod_win.configure(bg=BG)
        
        tk.Label(mod_win, text=f"Modify Column: {old_col_name}", bg=BG, fg=ACCENT, font=FONT_SUBTITLE).pack(pady=15)
        
        form = tk.Frame(mod_win, bg=BG)
        form.pack(pady=10, padx=20)
        
        tk.Label(form, text="New Name:", bg=BG, fg=FG, font=FONT_TEXT).grid(row=0, column=0, sticky="e", padx=10, pady=10)
        new_name = styled_entry(form, width=25)
        new_name.insert(0, old_col_name)
        new_name.grid(row=0, column=1, pady=10)
        
        tk.Label(form, text="Data Type:", bg=BG, fg=FG, font=FONT_TEXT).grid(row=1, column=0, sticky="e", padx=10, pady=10)
        new_type = ttk.Combobox(form, values=["INT", "VARCHAR", "TEXT", "FLOAT", "DOUBLE", "DATE", "DATETIME", "CHAR", "BIGINT", "DECIMAL"], width=23)
        new_type.set("VARCHAR")
        new_type.grid(row=1, column=1, pady=10)
        
        tk.Label(form, text="Length:", bg=BG, fg=FG, font=FONT_TEXT).grid(row=2, column=0, sticky="e", padx=10, pady=10)
        new_length = styled_entry(form, width=25)
        new_length.grid(row=2, column=1, pady=10)
        
        tk.Label(form, text="Default Value:", bg=BG, fg=FG, font=FONT_TEXT).grid(row=3, column=0, sticky="e", padx=10, pady=10)
        default_val = styled_entry(form, width=25)
        default_val.grid(row=3, column=1, pady=10)
        
        not_null_var = tk.BooleanVar()
        tk.Checkbutton(form, text="NOT NULL", variable=not_null_var, bg=BG, fg=FG, selectcolor=INPUT_BG).grid(row=4, column=1, sticky="w", pady=5)
        
        def execute_modify():
            new_col_name = new_name.get().strip()
            dtype = new_type.get().strip()
            length = new_length.get().strip()
            
            if not new_col_name or not dtype:
                messagebox.showwarning("Missing Info", "Column name and type required.")
                return
            
            full_type = dtype
            if dtype in ["VARCHAR", "CHAR"] and length:
                full_type = f"{dtype}({length})"
            
            # Use CHANGE to rename and modify
            sql = f"ALTER TABLE `{table_name}` CHANGE `{old_col_name}` `{new_col_name}` {full_type}"
            
            if not_null_var.get():
                sql += " NOT NULL"
            
            if default_val.get().strip():
                sql += f" DEFAULT '{default_val.get().strip()}'"
            
            try:
                cursor = conn.cursor()
                cursor.execute(sql)
                conn.commit()
                log(f"✓ Column '{old_col_name}' modified", "SUCCESS")
                refresh_columns()
                mod_win.destroy()
            except mysql.connector.Error as e:
                log(f"✗ Error modifying column: {e}", "ERROR")
                messagebox.showerror("Error", str(e))
        
        styled_button(mod_win, "Modify Column", execute_modify, bg=WARNING, fg=BG).pack(pady=20)
    
    def delete_column():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a column to delete.")
            return
        
        col_name = tree.item(selected[0])['values'][0]
        confirm = messagebox.askyesno("Confirm Delete", f"Delete column '{col_name}'?")
        
        if confirm:
            try:
                cursor = conn.cursor()
                cursor.execute(f"ALTER TABLE `{table_name}` DROP COLUMN `{col_name}`")
                conn.commit()
                log(f"✓ Column '{col_name}' deleted", "SUCCESS")
                refresh_columns()
            except mysql.connector.Error as e:
                log(f"✗ Error deleting column: {e}", "ERROR")
                messagebox.showerror("Error", str(e))
    
    def reorder_column():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a column to reorder.")
            return
        
        col_name = tree.item(selected[0])['values'][0]
        col_type = tree.item(selected[0])['values'][1]
        
        order_win = Toplevel(col_window)
        order_win.title("Reorder Column")
        order_win.geometry("400x250")
        order_win.configure(bg=BG)
        
        tk.Label(order_win, text=f"Reorder: {col_name}", bg=BG, fg=ACCENT, font=FONT_SUBTITLE).pack(pady=15)
        
        position_var = tk.StringVar(value="FIRST")
        tk.Radiobutton(order_win, text="Move to First", variable=position_var, value="FIRST", bg=BG, fg=FG, selectcolor=INPUT_BG, font=FONT_TEXT).pack(pady=10)
        tk.Radiobutton(order_win, text="Move After:", variable=position_var, value="AFTER", bg=BG, fg=FG, selectcolor=INPUT_BG, font=FONT_TEXT).pack(pady=10)
        
        after_combo = ttk.Combobox(order_win, width=30)
        after_combo.pack(pady=10)
        
        try:
            cursor = conn.cursor()
            cursor.execute(f"DESCRIBE `{table_name}`")
            cols = [row[0] for row in cursor.fetchall() if row[0] != col_name]
            after_combo['values'] = cols
        except:
            pass
        
        def execute_reorder():
            sql = f"ALTER TABLE `{table_name}` MODIFY COLUMN `{col_name}` {col_type}"
            
            if position_var.get() == "FIRST":
                sql += " FIRST"
            elif position_var.get() == "AFTER" and after_combo.get():
                sql += f" AFTER `{after_combo.get()}`"
            
            try:
                cursor = conn.cursor()
                cursor.execute(sql)
                conn.commit()
                log(f"✓ Column '{col_name}' reordered", "SUCCESS")
                refresh_columns()
                order_win.destroy()
            except mysql.connector.Error as e:
                log(f"✗ Error reordering column: {e}", "ERROR")
                messagebox.showerror("Error", str(e))
        
        styled_button(order_win, "Reorder", execute_reorder, bg=ACCENT, fg=FG).pack(pady=15)
    
    styled_button(btn_frame, "Add Column", add_column, bg=SUCCESS, fg=FG).pack(side="left", padx=5)
    styled_button(btn_frame, "Modify Column", modify_column, bg=WARNING, fg=BG).pack(side="left", padx=5)
    styled_button(btn_frame, "Reorder Column", reorder_column, bg=ACCENT, fg=FG).pack(side="left", padx=5)
    styled_button(btn_frame, "Delete Column", delete_column, bg=DANGER, fg=FG).pack(side="left", padx=5)
    styled_button(btn_frame, "Refresh", refresh_columns, bg=CARD_BG, fg=FG).pack(side="left", padx=5)

def record_management_panel():
    if conn is None or not conn.is_connected():
        messagebox.showwarning("Not Connected", "Please login to MySQL first.")
        show_login()
        return
    if not conn.database:
        messagebox.showwarning("No Database Selected", "Please select a database first.")
        load_db_panel()
        return
    
    clear_content()
    
    header_card = create_card_frame(content, f"📝 Record Management - {conn.database}")
    header_card.pack(fill="x", padx=20, pady=10)
    
    table_frame = tk.Frame(header_card, bg=CARD_BG)
    table_frame.pack(pady=15, padx=20)
    
    tk.Label(table_frame, text="Select Table:", bg=CARD_BG, fg=FG, font=FONT_TEXT).pack(side="left", padx=5)
    table_combo = ttk.Combobox(table_frame, state="readonly", font=FONT_TEXT, width=35)
    table_combo.pack(side="left", padx=10)
    
    # Form card
    form_card = create_card_frame(content, "Entry Form")
    form_card.pack(fill="x", padx=20, pady=10)
    
    form_frame = tk.Frame(form_card, bg=CARD_BG)
    form_frame.pack(pady=15, padx=20, fill="x")
    
    entry_widgets = {}
    not_null_info = {}
    pk_field_name = [None]
    current_record_pk_value = [None]
    
    # Data view card
    data_card = create_card_frame(content, "Table Data")
    data_card.pack(fill="both", expand=True, padx=20, pady=10)
    
    tree_frame = tk.Frame(data_card, bg=CARD_BG)
    tree_frame.pack(fill="both", expand=True, padx=15, pady=15)
    
    tree = ttk.Treeview(tree_frame)
    vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    
    tree.pack(side="left", fill="both", expand=True)
    vsb.pack(side="right", fill="y")
    hsb.pack(side="bottom", fill="x")
    
    tree.bind("<ButtonRelease-1>", lambda e: populate_form_from_tree())
    
    def load_table_fields():
        for widget in form_frame.winfo_children():
            widget.destroy()
        entry_widgets.clear()
        not_null_info.clear()
        pk_field_name[0] = None
        current_record_pk_value[0] = None
        
        tbl = table_combo.get().strip()
        if not tbl:
            return
        
        try:
            cursor = conn.cursor()
            cursor.execute(f"DESCRIBE `{tbl}`")
            entries_for_binding = []
            
            for row in cursor.fetchall():
                field_name = row[0]
                is_nullable = row[2] == 'YES'
                is_pk = row[3] == 'PRI'
                
                not_null_info[field_name] = not is_nullable
                
                row_frame = tk.Frame(form_frame, bg=CARD_BG)
                row_frame.pack(fill="x", pady=5)
                
                label_text = f"{field_name}:"
                if is_pk:
                    label_text += " 🔑"
                if not is_nullable:
                    label_text += " *"
                
                tk.Label(row_frame, text=label_text, bg=CARD_BG, fg=FG, font=FONT_TEXT, width=20, anchor="w").pack(side="left", padx=5)
                entry = styled_entry(row_frame, width=50)
                entry.pack(side="left", fill="x", expand=True, padx=5)
                entry_widgets[field_name] = entry
                entries_for_binding.append(entry)
                
                if is_pk:
                    pk_field_name[0] = field_name
            
            if entries_for_binding:
                bind_enter_to_next(entries_for_binding, insert_btn)
            
        except mysql.connector.Error as e:
            log(f"✗ Error describing table: {e}", "ERROR")
            messagebox.showerror("Error", str(e))
        
        refresh_records()
    
    def refresh_records():
        tbl = table_combo.get().strip()
        if not tbl:
            return
        
        for item in tree.get_children():
            tree.delete(item)
        
        try:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM `{tbl}`")
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            
            tree['columns'] = columns
            tree['show'] = 'headings'
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=120, anchor="center")
            for row in rows:
                tree.insert('', 'end', values=row)
        except mysql.connector.Error as e:
            log(f"✗ Error loading records: {e}", "ERROR")
    
    def populate_form_from_tree():
        selected_item = tree.focus()
        if not selected_item:
            return
        
        values = tree.item(selected_item)['values']
        for entry in entry_widgets.values():
            entry.delete(0, 'end')
        
        for i, (field_name, entry_widget) in enumerate(entry_widgets.items()):
            if i < len(values):
                entry_widget.insert(0, str(values[i]))
        
        if pk_field_name[0] and pk_field_name[0] in entry_widgets:
            current_record_pk_value[0] = entry_widgets[pk_field_name[0]].get()
        elif values:
            current_record_pk_value[0] = str(values[0])
    
    def insert_record():
        tbl = table_combo.get().strip()
        if not tbl:
            messagebox.showwarning("No Table", "Please select a table.")
            return
        
        fields = []
        values = []
        
        for field, entry in entry_widgets.items():
            value = entry.get()
            if not_null_info.get(field, False) and not value.strip():
                messagebox.showerror("Validation Error", f"'{field}' cannot be empty (NOT NULL).")
                return
            
            fields.append(f"`{field}`")
            values.append(value)
        
        if not fields:
            messagebox.showwarning("No Data", "Please enter data.")
            return
        
        try:
            placeholders = ','.join(['%s'] * len(values))
            sql = f"INSERT INTO `{tbl}` ({','.join(fields)}) VALUES ({placeholders})"
            cursor = conn.cursor()
            cursor.execute(sql, values)
            conn.commit()
            log(f"✓ Record inserted into '{tbl}'", "SUCCESS")
            for entry in entry_widgets.values():
                entry.delete(0, 'end')
            refresh_records()
        except mysql.connector.Error as e:
            log(f"✗ Insert error: {e}", "ERROR")
            messagebox.showerror("Error", str(e))
    
    def update_record():
        tbl = table_combo.get().strip()
        if not tbl or not current_record_pk_value[0] or not pk_field_name[0]:
            messagebox.showwarning("No Selection", "Please select a record to update.")
            return
        
        updates = []
        values = []
        
        for field, entry in entry_widgets.items():
            value = entry.get()
            if not_null_info.get(field, False) and not value.strip():
                messagebox.showerror("Validation Error", f"'{field}' cannot be empty.")
                return
            updates.append(f"`{field}` = %s")
            values.append(value)
        
        values.append(current_record_pk_value[0])
        
        try:
            sql = f"UPDATE `{tbl}` SET {', '.join(updates)} WHERE `{pk_field_name[0]}` = %s"
            cursor = conn.cursor()
            cursor.execute(sql, values)
            conn.commit()
            log(f"✓ Record updated in '{tbl}'", "SUCCESS")
            refresh_records()
        except mysql.connector.Error as e:
            log(f"✗ Update error: {e}", "ERROR")
            messagebox.showerror("Error", str(e))
    
    def delete_record():
        tbl = table_combo.get().strip()
        if not tbl or not current_record_pk_value[0] or not pk_field_name[0]:
            messagebox.showwarning("No Selection", "Please select a record to delete.")
            return
        
        confirm = messagebox.askyesno("Confirm Delete", "Delete selected record?")
        if not confirm:
            return
        
        try:
            sql = f"DELETE FROM `{tbl}` WHERE `{pk_field_name[0]}` = %s"
            cursor = conn.cursor()
            cursor.execute(sql, (current_record_pk_value[0],))
            conn.commit()
            log(f"✓ Record deleted from '{tbl}'", "SUCCESS")
            for entry in entry_widgets.values():
                entry.delete(0, 'end')
            current_record_pk_value[0] = None
            refresh_records()
        except mysql.connector.Error as e:
            log(f"✗ Delete error: {e}", "ERROR")
            messagebox.showerror("Error", str(e))
    
    # Horizontal button layout
    btn_frame = tk.Frame(form_card, bg=CARD_BG)
    btn_frame.pack(pady=15)
    
    styled_button(btn_frame, "Load Table", load_table_fields, bg=CARD_BG, fg=ACCENT).pack(side="left", padx=5)
    insert_btn = styled_button(btn_frame, "Insert", insert_record, bg=SUCCESS, fg=FG)
    insert_btn.pack(side="left", padx=5)
    styled_button(btn_frame, "Update", update_record, bg=WARNING, fg=BG).pack(side="left", padx=5)
    styled_button(btn_frame, "Delete", delete_record, bg=DANGER, fg=FG).pack(side="left", padx=5)
    
    def refresh_table_list():
        try:
            cursor = conn.cursor()
            cursor.execute("SHOW TABLES")
            tables = [row[0] for row in cursor.fetchall()]
            table_combo['values'] = tables
            if tables:
                table_combo.set(tables[0])
                load_table_fields()
            else:
                table_combo.set("")
        except mysql.connector.Error as e:
            log(f"✗ Error loading tables: {e}", "ERROR")
    
    table_combo.bind("<<ComboboxSelected>>", lambda e: load_table_fields())
    refresh_table_list()

def sql_terminal_panel():
    if conn is None or not conn.is_connected():
        messagebox.showwarning("Not Connected", "Please login first.")
        show_login()
        return
    
    clear_content()
    
    terminal_card = create_card_frame(content, "💻 SQL Terminal")
    terminal_card.pack(fill="both", expand=True, padx=20, pady=10)
    
    input_frame = tk.Frame(terminal_card, bg=CARD_BG)
    input_frame.pack(fill="both", expand=True, padx=15, pady=15)
    
    tk.Label(input_frame, text="Enter SQL Query:", bg=CARD_BG, fg=FG, font=FONT_TEXT).pack(anchor="w", pady=(0, 5))
    
    input_box = tk.Text(input_frame, height=12, bg=INPUT_BG, fg=FG, insertbackground=FG, 
                        font=("Consolas", 11), relief="flat", bd=2, 
                        highlightbackground=BORDER, highlightthickness=1)
    input_box.pack(fill="both", expand=True)
    
    def execute_query():
        sql = input_box.get("1.0", "end").strip()
        if not sql:
            return
        
        result_win = Toplevel(root)
        result_win.title("Query Results")
        result_win.geometry("1000x600")
        result_win.configure(bg=BG)
        
        tk.Label(result_win, text="📊 Query Results", bg=BG, fg=ACCENT, font=FONT_TITLE).pack(pady=15)
        
        # Query display
        query_frame = tk.Frame(result_win, bg=CARD_BG, highlightbackground=BORDER, highlightthickness=1)
        query_frame.pack(fill="x", padx=20, pady=(0, 10))
        tk.Label(query_frame, text="Executed Query:", bg=CARD_BG, fg=ACCENT, font=FONT_TEXT).pack(anchor="w", padx=10, pady=5)
        query_text = tk.Text(query_frame, height=4, bg=INPUT_BG, fg=FG, font=("Consolas", 9), wrap="word")
        query_text.pack(fill="x", padx=10, pady=(0, 10))
        query_text.insert("1.0", sql)
        query_text.config(state="disabled")
        
        # Results frame
        result_frame = tk.Frame(result_win, bg=BG)
        result_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        try:
            cursor = conn.cursor()
            cursor.execute(sql)
            
            if cursor.with_rows:
                # Display results in treeview
                tree = ttk.Treeview(result_frame, show="headings")
                vsb = ttk.Scrollbar(result_frame, orient="vertical", command=tree.yview)
                hsb = ttk.Scrollbar(result_frame, orient="horizontal", command=tree.xview)
                tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
                
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                
                tree['columns'] = columns
                for col in columns:
                    tree.heading(col, text=col)
                    tree.column(col, width=150, anchor="center")
                
                for row in rows:
                    tree.insert("", "end", values=row)
                
                tree.pack(side="left", fill="both", expand=True)
                vsb.pack(side="right", fill="y")
                hsb.pack(side="bottom", fill="x")
                
                status = tk.Label(result_win, text=f"✓ {len(rows)} rows returned", 
                                 bg=BG, fg=SUCCESS, font=FONT_TEXT)
                status.pack(pady=10)
                
                log(f"✓ Query returned {len(rows)} rows", "RESULT")
            else:
                conn.commit()
                affected = cursor.rowcount
                
                result_label = tk.Label(result_frame, 
                                       text=f"✓ Query executed successfully\n\nRows affected: {affected}", 
                                       bg=BG, fg=SUCCESS, font=FONT_SUBTITLE)
                result_label.pack(expand=True)
                
                log(f"✓ Query executed. Rows affected: {affected}", "SUCCESS")
        
        except mysql.connector.Error as e:
            error_text = tk.Text(result_frame, height=10, bg=INPUT_BG, fg="#ff6b6b", 
                                font=("Consolas", 10), wrap="word")
            error_text.pack(fill="both", expand=True)
            error_text.insert("1.0", f"Error executing query:\n\n{str(e)}")
            error_text.config(state="disabled")
            
            log(f"✗ SQL Error: {e}", "ERROR")
    
    btn_frame = tk.Frame(terminal_card, bg=CARD_BG)
    btn_frame.pack(pady=15)
    
    styled_button(btn_frame, "▶ Execute Query", execute_query, bg=SUCCESS, fg=FG).pack(side="left", padx=5)
    styled_button(btn_frame, "Clear", lambda: input_box.delete("1.0", "end"), bg=DANGER, fg=FG).pack(side="left", padx=5)

def user_management_panel():
    if conn is None or not conn.is_connected():
        messagebox.showwarning("Not Connected", "Please login first.")
        show_login()
        return
    
    clear_content()
    
    # Create User
    create_card = create_card_frame(content, "👤 Create New User")
    create_card.pack(fill="x", padx=20, pady=10)
    
    create_form = tk.Frame(create_card, bg=CARD_BG)
    create_form.pack(pady=15, padx=20)
    
    tk.Label(create_form, text="Username:", bg=CARD_BG, fg=FG, font=FONT_TEXT).grid(row=0, column=0, sticky="e", padx=10, pady=10)
    create_username = styled_entry(create_form, width=35)
    create_username.grid(row=0, column=1, pady=10)
    
    tk.Label(create_form, text="Password:", bg=CARD_BG, fg=FG, font=FONT_TEXT).grid(row=1, column=0, sticky="e", padx=10, pady=10)
    create_password = styled_entry(create_form, width=35, show="*")
    create_password.grid(row=1, column=1, pady=10)
    
    def create_user():
        user = create_username.get().strip()
        pwd = create_password.get()
        if not user or not pwd:
            messagebox.showwarning("Missing Info", "Username and password required.")
            return
        try:
            cursor = conn.cursor()
            cursor.execute(f"CREATE USER '{user}'@'localhost' IDENTIFIED BY '{pwd}'")
            conn.commit()
            log(f"✓ User '{user}' created", "SUCCESS")
            create_username.delete(0, 'end')
            create_password.delete(0, 'end')
        except mysql.connector.Error as e:
            log(f"✗ User creation error: {e}", "ERROR")
            messagebox.showerror("Error", str(e))
    
    create_btn = styled_button(create_form, "Create User", create_user, bg=SUCCESS, fg=FG)
    create_btn.grid(row=2, column=0, columnspan=2, pady=15)
    bind_enter_to_next([create_username, create_password], create_btn)
    
    # Grant Privileges
    grant_card = create_card_frame(content, "🔑 Grant Privileges")
    grant_card.pack(fill="x", padx=20, pady=10)
    
    grant_form = tk.Frame(grant_card, bg=CARD_BG)
    grant_form.pack(pady=15, padx=20)
    
    tk.Label(grant_form, text="Username:", bg=CARD_BG, fg=FG, font=FONT_TEXT).grid(row=0, column=0, sticky="e", padx=10, pady=10)
    grant_username = styled_entry(grant_form, width=35)
    grant_username.grid(row=0, column=1, pady=10)
    
    def grant_all():
        user = grant_username.get().strip()
        if not user:
            messagebox.showwarning("Missing Username", "Please enter a username.")
            return
        try:
            cursor = conn.cursor()
            cursor.execute(f"GRANT ALL PRIVILEGES ON *.* TO '{user}'@'localhost' WITH GRANT OPTION")
            conn.commit()
            log(f"✓ All privileges granted to '{user}'", "SUCCESS")
        except mysql.connector.Error as e:
            log(f"✗ Grant error: {e}", "ERROR")
            messagebox.showerror("Error", str(e))
    
    def revoke_all():
        user = grant_username.get().strip()
        if not user:
            messagebox.showwarning("Missing Username", "Please enter a username.")
            return
        confirm = messagebox.askyesno("Confirm Revoke", f"Revoke all privileges from '{user}'?")
        if confirm:
            try:
                cursor = conn.cursor()
                cursor.execute(f"REVOKE ALL PRIVILEGES ON *.* FROM '{user}'@'localhost'")
                conn.commit()
                log(f"✓ All privileges revoked from '{user}'", "SUCCESS")
            except mysql.connector.Error as e:
                log(f"✗ Revoke error: {e}", "ERROR")
                messagebox.showerror("Error", str(e))
    
    btn_frame = tk.Frame(grant_card, bg=CARD_BG)
    btn_frame.pack(pady=15)
    
    styled_button(btn_frame, "Grant All Privileges", grant_all, bg=SUCCESS, fg=FG).pack(side="left", padx=5)
    styled_button(btn_frame, "Revoke All Privileges", revoke_all, bg=DANGER, fg=FG).pack(side="left", padx=5)
    
    grant_username.bind("<Return>", lambda e: grant_all())
    
    # Remove User
    remove_card = create_card_frame(content, "🗑️ Remove User")
    remove_card.pack(fill="x", padx=20, pady=10)
    
    remove_form = tk.Frame(remove_card, bg=CARD_BG)
    remove_form.pack(pady=15, padx=20)
    
    tk.Label(remove_form, text="Username:", bg=CARD_BG, fg=FG, font=FONT_TEXT).grid(row=0, column=0, sticky="e", padx=10, pady=10)
    remove_username = styled_entry(remove_form, width=35)
    remove_username.grid(row=0, column=1, pady=10)
    
    def remove_user():
        user = remove_username.get().strip()
        if not user:
            messagebox.showwarning("Missing Username", "Please enter a username.")
            return
        confirm = messagebox.askyesno("Confirm Removal", f"Drop user '{user}'?")
        if confirm:
            try:
                cursor = conn.cursor()
                cursor.execute(f"DROP USER '{user}'@'localhost'")
                conn.commit()
                log(f"✓ User '{user}' removed", "SUCCESS")
                remove_username.delete(0, 'end')
            except mysql.connector.Error as e:
                log(f"✗ User removal error: {e}", "ERROR")
                messagebox.showerror("Error", str(e))
    
    remove_btn = styled_button(remove_form, "Remove User", remove_user, bg=DANGER, fg=FG)
    remove_btn.grid(row=1, column=0, columnspan=2, pady=15)
    remove_username.bind("<Return>", lambda e: remove_btn.invoke())

def view_table_panel():
    if conn is None or not conn.is_connected():
        messagebox.showwarning("Not Connected", "Please login first.")
        show_login()
        return
    if not conn.database:
        messagebox.showwarning("No Database Selected", "Please select a database first.")
        load_db_panel()
        return
    
    clear_content()
    
    header_card = create_card_frame(content, f"👁️ Table Viewer - {conn.database}")
    header_card.pack(fill="x", padx=20, pady=10)
    
    control_frame = tk.Frame(header_card, bg=CARD_BG)
    control_frame.pack(pady=15, padx=20)
    
    tk.Label(control_frame, text="Select Table:", bg=CARD_BG, fg=FG, font=FONT_TEXT).pack(side="left", padx=5)
    table_combo = ttk.Combobox(control_frame, state="readonly", font=FONT_TEXT, width=35)
    table_combo.pack(side="left", padx=10)
    
    # Data display
    data_frame = tk.Frame(content, bg=BG)
    data_frame.pack(fill="both", expand=True, padx=20, pady=10)
    
    tree_container = tk.Frame(data_frame, bg=CARD_BG, highlightbackground=BORDER, highlightthickness=1)
    tree_container.pack(fill="both", expand=True)
    
    tree = ttk.Treeview(tree_container)
    vsb = ttk.Scrollbar(tree_container, orient="vertical", command=tree.yview)
    hsb = ttk.Scrollbar(tree_container, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    
    tree.pack(side="left", fill="both", expand=True, padx=15, pady=15)
    vsb.pack(side="right", fill="y", pady=15)
    hsb.pack(side="bottom", fill="x", padx=15)
    
    # Pagination
    nav_frame = tk.Frame(content, bg=BG)
    nav_frame.pack(pady=10)
    
    per_page = 20
    current_page = [0]
    
    page_label = tk.Label(nav_frame, text="Page 1 of 1", bg=BG, fg=FG, font=FONT_TEXT)
    
    def load_table_data():
        tbl = table_combo.get().strip()
        if not tbl:
            return
        
        for item in tree.get_children():
            tree.delete(item)
        
        try:
            cursor = conn.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM `{tbl}`")
            total_rows = cursor.fetchone()[0]
            offset = current_page[0] * per_page
            
            if offset < 0:
                offset = 0
                current_page[0] = 0
            
            cursor.execute(f"SELECT * FROM `{tbl}` LIMIT {per_page} OFFSET {offset}")
            rows = cursor.fetchall()
            cols = [desc[0] for desc in cursor.description]
            
            tree['columns'] = cols
            tree['show'] = 'headings'
            for col in cols:
                tree.heading(col, text=col)
                tree.column(col, anchor="center", width=140)
            for row in rows:
                tree.insert("", "end", values=row)
            
            total_pages = ((total_rows - 1) // per_page) + 1 if total_rows > 0 else 0
            page_label.config(text=f"Page {current_page[0] + 1} of {total_pages} (Total: {total_rows} rows)")
            
        except mysql.connector.Error as e:
            log(f"✗ Error viewing table: {e}", "ERROR")
            messagebox.showerror("Error", str(e))
    
    def next_page():
        current_page[0] += 1
        load_table_data()
    
    def prev_page():
        if current_page[0] > 0:
            current_page[0] -= 1
            load_table_data()
    
    def export_to_csv():
        tbl = table_combo.get().strip()
        if not tbl:
            messagebox.showwarning("No Table", "Please select a table to export.")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"{tbl}_data.csv"
        )
        
        if not file_path:
            return
        
        try:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM `{tbl}`")
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerow(columns)
                csv_writer.writerows(rows)
            
            log(f"✓ Exported '{tbl}' to CSV", "SUCCESS")
            messagebox.showinfo("Export Successful", f"Table exported to:\n{file_path}")
            
        except Exception as e:
            log(f"✗ Export error: {e}", "ERROR")
            messagebox.showerror("Export Failed", str(e))
    
    styled_button(control_frame, "Export to CSV", export_to_csv, bg=SUCCESS, fg=FG).pack(side="right", padx=5)
    
    styled_button(nav_frame, "⬅ Previous", prev_page, bg=CARD_BG, fg=FG).pack(side="left", padx=5)
    page_label.pack(side="left", padx=15)
    styled_button(nav_frame, "Next ➡", next_page, bg=CARD_BG, fg=FG).pack(side="left", padx=5)
    
    def refresh_tables():
        try:
            cursor = conn.cursor()
            cursor.execute("SHOW TABLES")
            tables = [row[0] for row in cursor.fetchall()]
            table_combo['values'] = tables
            if tables:
                table_combo.set(tables[0])
                current_page[0] = 0
                load_table_data()
            else:
                table_combo.set("")
        except mysql.connector.Error as e:
            log(f"✗ Error loading tables: {e}", "ERROR")
    
    table_combo.bind("<<ComboboxSelected>>", lambda e: (current_page.__setitem__(0, 0), load_table_data()))
    refresh_tables()

def show_console_log_panel():
    clear_content()
    info_card = create_card_frame(content, "ℹ️ Console Log Information")
    info_card.pack(pady=50, padx=100)
    
    info_text = tk.Label(info_card, 
                        text="The console log is always visible at the bottom of the window.\n\n"
                             "It displays real-time information about all operations,\n"
                             "including successes, errors, and general information.",
                        bg=CARD_BG, fg=FG, font=FONT_TEXT, justify="center")
    info_text.pack(pady=30, padx=30)
    
    log("Console viewer panel loaded", "INFO")

# Initialize styling
style_widgets()

# Sidebar menu
sidebar_button("Login", show_login, "🔐")
sidebar_button("Database", load_db_panel, "🗄️")
sidebar_button("Tables", from_table_panel, "📋")
sidebar_button("Records", record_management_panel, "📝")
sidebar_button("Terminal", sql_terminal_panel, "💻")
sidebar_button("Users", user_management_panel, "👥")
sidebar_button("Table Viewer", view_table_panel, "👁️")
sidebar_button("Console Log", show_console_log_panel, "📊")

# Start application
show_login()
log("🚀 MySQL Admin Pro started", "INFO")
root.mainloop()
