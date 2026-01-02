# Clinical-Management-System
A Clinical Management System designed to manage patient records, appointments, billing, and doctor details efficiently.

A desktop-based **Clinical Management System** built with **Python, Tkinter, and SQLite3** to simplify hospital and clinic operations such as patient management, appointment scheduling, and role-based access control

🚀 Project Overview

Healthcare is a critical sector where efficient data management plays a vital role in patient care. Many hospitals still rely on outdated systems, paper-based records, and manual appointment scheduling, which often lead to errors and inefficiencies.

This project provides a **Healthcare / Clinical Management System** with:

- Secure user authentication  
- Organized patient record management  
- Streamlined appointment scheduling  
- Intuitive desktop GUI using Tkinter

The system demonstrates practical application of **database design**, **authentication mechanisms**, and **role-based access control** in a real-world healthcare context.

🧩 Features

User Authentication
  - Login system with username and password
  - Three roles: User, Doctor, Admin

Role-Based Access Control
  - User: Add patients and schedule appointments
  - Doctor: View own appointments and patient details
  - Admin: Staff management, billing, and reports

Patient Management
  - Register new patients
  - Store demographic and medical history details

Appointment Management
  - Schedule appointments linked to patients and doctors
  - Doctor-specific appointment view (each doctor sees only their appointments)

GUI Features
  - Tkinter-based windows and forms
  - TreeView tables to display patients and appointments
  - Actions: refresh, delete, and view details

🏗️ System Architecture

The application follows a simple **3-layer architecture**:

Presentation Layer
  - Tkinter GUI interface (forms, tables, dialogs)

Business Logic Layer
  - Python backend handling validation, role checking, and operations

Data Layer
  - SQLite databases for persistent storage

💾 Database Design

The system uses **two SQLite databases**:

`login.db`

Table: `users`
  - `username` – Primary Key  
  - `password`  
  - `role` – `user` / `admin` / `doctor`

`clinic.db`

Tables: `patients`, `appointments`

- `patients` fields:
  - `id`
  - `name`
  - `age`
  - `gender`
  - `contact`
  - `address`
  - `medical_history`

🛠️ Tech Stack

- Language: Python 3  
- GUI Framework: Tkinter, ttk (for themed widgets and TreeView)
- Database: SQLite3 (file-based, no server required)
- Dialogs: `tkinter.messagebox` for alerts and confirmations

✅ Advantages

Easy to Deploy
  - Can be packaged as a single `.exe` using tools like PyInstaller, along with the database files (`login.db`, `clinic.db`).

No Server Required
  - SQLite is file-based and works fully offline, suitable for small clinics and labs.

Fast Development
  - Tkinter is beginner-friendly and suitable for rapid prototyping of desktop apps.

Secure Access
  - Role-based access control prevents unauthorized access to sensitive operations and data.

📦 Getting Started

Run the application:
python app.py
