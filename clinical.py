import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

# ----------------- DATABASE SETUP -----------------
login_conn = sqlite3.connect("login.db")
login_cur = login_conn.cursor()

login_cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT NOT NULL,
    role TEXT NOT NULL
)
""")
login_conn.commit()

clinic_conn = sqlite3.connect("clinic.db")
clinic_cur = clinic_conn.cursor()

# Patients table
clinic_cur.execute("""
CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    age INTEGER,
    gender TEXT,
    contact TEXT
)
""")

# Extra columns if missing
try:
    clinic_cur.execute("ALTER TABLE patients ADD COLUMN address TEXT")
except sqlite3.OperationalError:
    pass
try:
    clinic_cur.execute("ALTER TABLE patients ADD COLUMN medical_history TEXT")
except sqlite3.OperationalError:
    pass

clinic_conn.commit()

# Appointments table
clinic_cur.execute("""
CREATE TABLE IF NOT EXISTS appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER,
    date TEXT,
    time TEXT,
    doctor TEXT,
    reason TEXT,
    FOREIGN KEY (patient_id) REFERENCES patients(id)
)
""")

clinic_conn.commit()

# ----------------- DOCTOR LIST -----------------
DOCTORS = [
    ("kumar",  "Dr. Kumar - General"),
    ("rani",   "Dr. Rani - Pediatrician"),
    ("bharagv","Dr. Bharagv - Cardiologist"),
    ("mehta",  "Dr. Mehta - Orthopedic"),
    ("komal",  "Dr. Komal - Dermatologist"),
    ("manju",  "Dr. Manju - Neurologist")
]

# ----------------- DB HELPER FUNCTIONS -----------------
def db_add_user(username, password, role):
    try:
        login_cur.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            (username, password, role)
        )
        login_conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def db_get_user(username, password):
    login_cur.execute(
        "SELECT username, role FROM users WHERE username=? AND password=?",
        (username, password)
    )
    return login_cur.fetchone()

def db_add_patient(name, age, gender, contact, address, medical_history):
    clinic_cur.execute(
        "INSERT INTO patients (name, age, gender, contact, address, medical_history) VALUES (?, ?, ?, ?, ?, ?)",
        (name, age, gender, contact, address, medical_history)
    )
    clinic_conn.commit()

def db_add_appointment(patient_id, date, time, doctor, reason):
    clinic_cur.execute(
        "INSERT INTO appointments (patient_id, date, time, doctor, reason) VALUES (?, ?, ?, ?, ?)",
        (patient_id, date, time, doctor, reason)
    )
    clinic_conn.commit()

def db_get_appointments_for_doctor(doctor_username):
    clinic_cur.execute("""
        SELECT a.id, p.name, a.date, a.time, a.reason
        FROM appointments a
        JOIN patients p ON a.patient_id = p.id
        WHERE a.doctor = ?
        ORDER BY a.date, a.time
    """, (doctor_username,))
    return clinic_cur.fetchall()

def db_list_all_patients():
    clinic_cur.execute(
        "SELECT id, name, age, gender, contact FROM patients ORDER BY id"
    )
    return clinic_cur.fetchall()

def db_list_all_appointments():
    clinic_cur.execute("""
        SELECT a.id, p.name, a.date, a.time, a.doctor, a.reason
        FROM appointments a
        JOIN patients p ON a.patient_id = p.id
        ORDER BY a.date, a.time
    """)
    return clinic_cur.fetchall()

# NEW DELETE FUNCTIONS
def db_delete_patient(patient_id):
    # First delete related appointments
    clinic_cur.execute("DELETE FROM appointments WHERE patient_id=?", (patient_id,))
    clinic_cur.execute("DELETE FROM patients WHERE id=?", (patient_id,))
    clinic_conn.commit()

def db_delete_appointment(appointment_id):
    clinic_cur.execute("DELETE FROM appointments WHERE id=?", (appointment_id,))
    clinic_conn.commit()

# ----------------- AUTH / GUI FUNCTIONS -----------------
def register():
    username = reg_username_entry.get().strip()
    password = reg_password_entry.get().strip()
    role = role_var.get()
    if username and password:
        success = db_add_user(username, password, role)
        if success:
            messagebox.showinfo("Success", f"Registration successful! Role: {role}")
            registration_window.destroy()
        else:
            messagebox.showerror("Error", "Username already exists!")
    else:
        messagebox.showerror("Error", "Please fill all fields!")

def login():
    username = username_entry.get().strip()
    password = password_entry.get().strip()
    user = db_get_user(username, password)
    if user:
        uname, role = user
        messagebox.showinfo("Login Successful", f"Welcome {uname} ({role})!")
        root.withdraw()
        open_dashboard(uname, role)
    else:
        messagebox.showerror("Login Failed", "Invalid username or password")

def open_registration():
    global registration_window, reg_username_entry, reg_password_entry, role_var
    registration_window = tk.Toplevel(root)
    registration_window.title("Register")
    registration_window.geometry("300x260")

    tk.Label(registration_window, text="Register New User",
             font=("Arial", 14, "bold")).pack(pady=10)

    tk.Label(registration_window, text="Username:").pack()
    reg_username_entry = tk.Entry(registration_window)
    reg_username_entry.pack()

    tk.Label(registration_window, text="Password:").pack()
    reg_password_entry = tk.Entry(registration_window, show="*")
    reg_password_entry.pack()

    tk.Label(registration_window, text="Role:").pack()
    role_var = tk.StringVar(value="user")
    tk.Radiobutton(registration_window, text="User",
                   variable=role_var, value="user").pack()
    tk.Radiobutton(registration_window, text="Admin",
                   variable=role_var, value="admin").pack()
    tk.Radiobutton(registration_window, text="Doctor",
                   variable=role_var, value="doctor").pack()

    tk.Button(registration_window, text="Register",
              command=register).pack(pady=10)

# ----------------- SHARED GUI FUNCTIONS (AVAILABLE TO ALL ROLES) -----------------
current_dashboard = None

def gui_add_patient_and_appointment():
    win = tk.Toplevel(current_dashboard)
    win.title("Add Patient & Appointment")
    win.geometry("500x450")

    tk.Label(win, text="Patient Name:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
    name_entry = tk.Entry(win)
    name_entry.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(win, text="Age:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
    age_entry = tk.Entry(win)
    age_entry.grid(row=1, column=1, padx=10, pady=5)

    tk.Label(win, text="Gender:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
    gender_entry = tk.Entry(win)
    gender_entry.grid(row=2, column=1, padx=10, pady=5)

    tk.Label(win, text="Contact:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
    contact_entry = tk.Entry(win)
    contact_entry.grid(row=3, column=1, padx=10, pady=5)

    tk.Label(win, text="Address:").grid(row=4, column=0, padx=10, pady=5, sticky="w")
    address_entry = tk.Entry(win)
    address_entry.grid(row=4, column=1, padx=10, pady=5)

    tk.Label(win, text="Medical History:").grid(row=5, column=0, padx=10, pady=5, sticky="w")
    medical_history_entry = tk.Entry(win)
    medical_history_entry.grid(row=5, column=1, padx=10, pady=5)

    tk.Label(win, text="Appointment Date (YYYY-MM-DD):").grid(row=6, column=0, padx=10, pady=5, sticky="w")
    date_entry = tk.Entry(win)
    date_entry.grid(row=6, column=1, padx=10, pady=5)

    tk.Label(win, text="Appointment Time (HH:MM):").grid(row=7, column=0, padx=10, pady=5, sticky="w")
    time_entry = tk.Entry(win)
    time_entry.grid(row=7, column=1, padx=10, pady=5)

    tk.Label(win, text="Reason:").grid(row=8, column=0, padx=10, pady=5, sticky="w")
    reason_entry = tk.Entry(win)
    reason_entry.grid(row=8, column=1, padx=10, pady=5)

    tk.Label(win, text="Select Doctor:").grid(row=9, column=0, padx=10, pady=5, sticky="w")
    doctor_map = {disp: login for login, disp in DOCTORS}
    display_names = list(doctor_map.keys())
    selected_doctor_display = tk.StringVar(win)
    selected_doctor_display.set(display_names[0])
    tk.OptionMenu(win, selected_doctor_display, *display_names).grid(row=9, column=1, padx=10, pady=5)

    def save_both():
        name = name_entry.get().strip()
        age = age_entry.get().strip()
        gender = gender_entry.get().strip()
        contact = contact_entry.get().strip()
        address = address_entry.get().strip()
        medical_history = medical_history_entry.get().strip()
        date = date_entry.get().strip()
        time = time_entry.get().strip()
        reason = reason_entry.get().strip()

        doctor_display = selected_doctor_display.get()
        doctor_username = doctor_map[doctor_display]

        if not name:
            messagebox.showerror("Error", "Patient name is required.")
            return

        try:
            age_val = int(age)
        except (ValueError, TypeError):
            messagebox.showerror("Error", "Age must be a number.")
            return

        if not date or not time:
            messagebox.showerror("Error", "Appointment date and time are required.")
            return

        clinic_cur.execute(
            "INSERT INTO patients (name, age, gender, contact, address, medical_history) VALUES (?, ?, ?, ?, ?, ?)",
            (name, age_val, gender, contact, address, medical_history)
        )
        clinic_conn.commit()
        pid = clinic_cur.lastrowid

        clinic_cur.execute(
            "INSERT INTO appointments (patient_id, date, time, doctor, reason) VALUES (?, ?, ?, ?, ?)",
            (pid, date, time, doctor_username, reason)
        )
        clinic_conn.commit()

        messagebox.showinfo("Success", f"Patient '{name}' and appointment added successfully!")
        win.destroy()

    tk.Button(win, text="Save Both", command=save_both).grid(row=10, column=1, pady=10)
    tk.Button(win, text="Cancel", command=win.destroy).grid(row=10, column=0, pady=10)

# ENHANCED PATIENTS VIEW WITH DELETE (SHARED BY ALL ROLES)
def show_patients_treeview(parent_win=None):
    win = tk.Toplevel(parent_win or current_dashboard)
    win.title("All Patients List - With Delete Option")
    win.geometry("900x600")

    # Buttons frame
    btn_frame = tk.Frame(win)
    btn_frame.pack(pady=10)
    
    tk.Button(btn_frame, text="Refresh", command=lambda: refresh_patients_tree(tree)).pack(side="left", padx=5)
    tk.Button(btn_frame, text="View Details", command=lambda: view_selected_patient(tree)).pack(side="left", padx=5)
    tk.Button(btn_frame, text="Delete Selected", command=lambda: delete_selected_patient(tree), bg="red", fg="white").pack(side="left", padx=5)
    tk.Button(btn_frame, text="Close", command=win.destroy).pack(side="right", padx=5)

    tree = ttk.Treeview(win, columns=("S.No", "ID", "Name", "Age", "Gender", "Contact"), show="headings")
    tree.heading("S.No", text="S.No")
    tree.heading("ID", text="ID")
    tree.heading("Name", text="Name")
    tree.heading("Age", text="Age")
    tree.heading("Gender", text="Gender")
    tree.heading("Contact", text="Contact")
    tree.pack(expand=True, fill="both", padx=10, pady=10)

    # Scrollbar
    scrollbar = ttk.Scrollbar(win, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    def refresh_patients_tree(tree_widget):
        # Clear existing items
        for item in tree_widget.get_children():
            tree_widget.delete(item)
        # Load fresh data
        patients = db_list_all_patients()
        for idx, p in enumerate(patients, start=1):
            tree_widget.insert("", "end", values=(idx, p[0], p[1], p[2], p[3], p[4]))

    def view_selected_patient(tree_widget):
        selected = tree_widget.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a patient first.")
            return
        patient_id = tree_widget.item(selected[0], "values")[1]
        view_patient_details(patient_id)

    def delete_selected_patient(tree_widget):
        selected = tree_widget.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a patient first.")
            return
        
        patient_id = tree_widget.item(selected[0], "values")[1]
        patient_name = tree_widget.item(selected[0], "values")[2]
        
        if messagebox.askyesno("Confirm Delete", f"Delete patient '{patient_name}' and all their appointments?"):
            db_delete_patient(patient_id)
            refresh_patients_tree(tree_widget)
            messagebox.showinfo("Success", "Patient and related appointments deleted successfully!")

    # Load initial data
    refresh_patients_tree(tree)

# ENHANCED APPOINTMENTS VIEW WITH DELETE (SHARED BY ALL ROLES)
def show_appointments_treeview(parent_win=None):
    win = tk.Toplevel(parent_win or current_dashboard)
    win.title("All Appointments List - With Delete Option")
    win.geometry("1000x600")

    # Buttons frame
    btn_frame = tk.Frame(win)
    btn_frame.pack(pady=10)
    
    tk.Button(btn_frame, text="Refresh", command=lambda: refresh_appts_tree(tree)).pack(side="left", padx=5)
    tk.Button(btn_frame, text="View Patient Details", command=lambda: view_selected_appt_patient(tree)).pack(side="left", padx=5)
    tk.Button(btn_frame, text="Delete Selected Appt", command=lambda: delete_selected_appt(tree), bg="red", fg="white").pack(side="left", padx=5)
    tk.Button(btn_frame, text="Close", command=win.destroy).pack(side="right", padx=5)

    tree = ttk.Treeview(win, columns=("ID", "Patient", "Date", "Time", "Doctor", "Reason"), show="headings")
    tree.heading("ID", text="ID")
    tree.heading("Patient", text="Patient")
    tree.heading("Date", text="Date")
    tree.heading("Time", text="Time")
    tree.heading("Doctor", text="Doctor (username)")
    tree.heading("Reason", text="Reason")
    tree.pack(expand=True, fill="both", padx=10, pady=10)

    # Scrollbar
    scrollbar = ttk.Scrollbar(win, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    def refresh_appts_tree(tree_widget):
        # Clear existing items
        for item in tree_widget.get_children():
            tree_widget.delete(item)
        # Load fresh data
        appts = db_list_all_appointments()
        for a in appts:
            tree_widget.insert("", "end", values=a)

    def view_selected_appt_patient(tree_widget):
        selected = tree_widget.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an appointment first.")
            return
        appt_id = tree_widget.item(selected[0], "values")[0]
        clinic_cur.execute("SELECT patient_id FROM appointments WHERE id=?", (appt_id,))
        row = clinic_cur.fetchone()
        if row:
            view_patient_details(row[0])

    def delete_selected_appt(tree_widget):
        selected = tree_widget.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an appointment first.")
            return
        
        appt_id = tree_widget.item(selected[0], "values")[0]
        patient_name = tree_widget.item(selected[0], "values")[1]
        
        if messagebox.askyesno("Confirm Delete", f"Delete appointment for '{patient_name}'?"):
            db_delete_appointment(appt_id)
            refresh_appts_tree(tree_widget)
            messagebox.showinfo("Success", "Appointment deleted successfully!")

    # Load initial data
    refresh_appts_tree(tree)

def view_patient_details(patient_id):
    clinic_cur.execute("SELECT name, age, gender, contact, address, medical_history FROM patients WHERE id=?", (patient_id,))
    p = clinic_cur.fetchone()
    if not p:
        messagebox.showerror("Error", "Patient not found.")
        return

    win = tk.Toplevel(current_dashboard)
    win.title(f"Patient Details: {p[0]}")
    win.geometry("500x400")

    tk.Label(win, text="Patient Details", font=("Arial", 16, "bold")).pack(pady=10)
    tk.Label(win, text=f"Name: {p[0]}").pack(anchor="w", padx=20, pady=5)
    tk.Label(win, text=f"Age: {p[1]}").pack(anchor="w", padx=20, pady=5)
    tk.Label(win, text=f"Gender: {p[2]}").pack(anchor="w", padx=20, pady=5)
    tk.Label(win, text=f"Contact: {p[3]}").pack(anchor="w", padx=20, pady=5)
    tk.Label(win, text=f"Address: {p[4]}").pack(anchor="w", padx=20, pady=5)
    tk.Label(win, text=f"Medical History: {p[5] or 'None'}").pack(anchor="w", padx=20, pady=5)

    tk.Button(win, text="Close", command=win.destroy).pack(pady=10)

# ----------------- DASHBOARD & MAIN WINDOW -----------------
def open_dashboard(username, role):
    global current_dashboard
    current_dashboard = tk.Toplevel(root)
    current_dashboard.title(f"Clinic Management System - {role.title()} Dashboard")
    current_dashboard.geometry("600x700")
    current_dashboard.configure(bg="#f8f9fa")

    # Header
    header_frame = tk.Frame(current_dashboard, bg="#f8f9fa")
    header_frame.pack(pady=20)
    tk.Label(header_frame, text=f"Welcome, {username}!",
             font=("Arial", 18, "bold"), bg="#f8f9fa", fg="#2c3e50").pack()
    tk.Label(header_frame, text=f"Role: {role.title()}",
             font=("Arial", 12), bg="#f8f9fa", fg="#7f8c8d").pack()

    # Common buttons for ALL roles
    common_frame = tk.LabelFrame(current_dashboard, text="Core Functions", font=("Arial", 12, "bold"), padx=10, pady=10)
    common_frame.pack(pady=10, padx=20, fill="x")
    
    tk.Button(common_frame, text="➕ Add Patient & Appointment", width=30, height=2,
              command=gui_add_patient_and_appointment, bg="#27ae60", fg="white", font=("Arial", 10, "bold")).pack(pady=5)
    tk.Button(common_frame, text="👥 View All Patients", width=30, height=2,
              command=lambda: show_patients_treeview(current_dashboard), bg="#3498db", fg="white", font=("Arial", 10, "bold")).pack(pady=5)
    tk.Button(common_frame, text="📅 View All Appointments", width=30, height=2,
              command=lambda: show_appointments_treeview(current_dashboard), bg="#e67e22", fg="white", font=("Arial", 10, "bold")).pack(pady=5)

    # Role-specific sections
    if role == "doctor":
        doctor_frame = tk.LabelFrame(current_dashboard, text="Doctor Specific", font=("Arial", 12, "bold"), padx=10, pady=10)
        doctor_frame.pack(pady=10, padx=20, fill="x")
        
        tk.Button(doctor_frame, text="👨‍⚕️ My Appointments Only", width=30, height=2,
                  command=lambda: open_doctor_my_appointments(username), bg="#9b59b6", fg="white", font=("Arial", 10, "bold")).pack(pady=5)

    elif role == "admin":
        admin_frame = tk.LabelFrame(current_dashboard, text="Admin Modules", font=("Arial", 12, "bold"), padx=10, pady=10)
        admin_frame.pack(pady=10, padx=20, fill="x")
        
        tk.Button(admin_frame, text="👥 Staff Management", width=30, height=2,
                  command=lambda: messagebox.showinfo("Admin", "Staff Management Module")).pack(pady=3)
        tk.Button(admin_frame, text="💰 Billing and Payment", width=30, height=2,
                  command=lambda: messagebox.showinfo("Admin", "Billing and Payment Module")).pack(pady=3)
        tk.Button(admin_frame, text="📊 Reports and Analytics", width=30, height=2,
                  command=lambda: messagebox.showinfo("Admin", "Reports and Analytics Module")).pack(pady=3)

    # Logout button
    tk.Button(current_dashboard, text="🚪 Logout", width=20, height=2,
              command=lambda: logout(current_dashboard), bg="#e74c3c", fg="white", font=("Arial", 12, "bold")).pack(pady=30)

def open_doctor_my_appointments(username):
    win = tk.Toplevel(current_dashboard)
    win.title(f"Dr. {username.title()} - My Appointments Only")
    win.geometry("900x600")
    win.configure(bg="#f0f8ff")

    tk.Label(win, text=f"My Appointments - Dr. {username.title()}", 
             font=("Arial", 16, "bold"), bg="#f0f8ff").pack(pady=20)

    tree = ttk.Treeview(win, columns=("ID", "Patient", "Date", "Time", "Reason"), show="headings")
    tree.heading("ID", text="ID")
    tree.heading("Patient", text="Patient Name")
    tree.heading("Date", text="Date")
    tree.heading("Time", text="Time")
    tree.heading("Reason", text="Reason")
    
    tree.column("ID", width=50)
    tree.column("Patient", width=200)
    tree.column("Date", width=120)
    tree.column("Time", width=100)
    tree.column("Reason", width=300)

    scrollbar = ttk.Scrollbar(win, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    tree.pack(side="left", expand=True, fill="both", padx=20, pady=20)
    scrollbar.pack(side="right", fill="y")

    # Load doctor's appointments
    appts = db_get_appointments_for_doctor(username)
    for a in appts:
        tree.insert("", "end", values=a)

    # Double-click to view patient details
    def on_double_click(event):
        selected = tree.selection()
        if not selected:
            return
        appt_id = tree.item(selected[0], "values")[0]
        clinic_cur.execute("SELECT patient_id FROM appointments WHERE id=?", (appt_id,))
        row = clinic_cur.fetchone()
        if row:
            view_patient_details(row[0])

    tree.bind("<Double-1>", on_double_click)

def logout(dashboard_win):
    dashboard_win.destroy()
    root.deiconify()

# ----------------- MAIN LOGIN WINDOW -----------------
root = tk.Tk()
root.title("Clinic Management System - Login")
root.geometry("400x300")
root.configure(bg="#ecf0f1")

tk.Label(root, text="🏥 Clinic Management System",
         font=("Arial", 18, "bold"), bg="#ecf0f1").pack(pady=30)

tk.Label(root, text="Username:", bg="#ecf0f1", font=("Arial", 12)).pack(pady=5)
username_entry = tk.Entry(root, font=("Arial", 12))
username_entry.pack(pady=5)

tk.Label(root, text="Password:", bg="#ecf0f1", font=("Arial", 12)).pack(pady=5)
password_entry = tk.Entry(root, show="*", font=("Arial", 12))
password_entry.pack(pady=5)

tk.Button(root, text="🔐 Login", command=login, width=15, height=2, 
          bg="#3498db", fg="white", font=("Arial", 12, "bold")).pack(pady=15)
tk.Button(root, text="📝 Register New User", command=open_registration, 
          width=20, height=2, font=("Arial", 10)).pack(pady=5)

root.mainloop()
