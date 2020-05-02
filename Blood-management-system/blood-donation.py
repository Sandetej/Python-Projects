from tkinter import *
from tkinter.font import BOLD
import mysql.connector
from tkinter import messagebox

# This variable is used to keep track of current open popup window
current_popup = None

# Create main window
root = Tk()
root.title("SandeepTeja Blood Donation Management System")
root.configure(bg='#f4f4f4')
root.geometry("900x600")

# Connect to MySQL database
try:
    db = mysql.connector.connect(host="localhost", user="root", password='', database='db')
    cursor = db.cursor()
except Exception as e:
    messagebox.showerror("Error", f"Database connection failed: {e}")

# This dictionary will store the unit label widgets for each blood group
unit_labels = {}

# When popup window is closed, reset variable
def clear_popup():
    global current_popup
    current_popup = None

# This function updates the unit values shown on screen from database
def refresh_table():
    try:
        cursor.execute("SELECT * FROM BloodBank")
        for bg, units in cursor.fetchall():
            if bg in unit_labels:
                unit_labels[bg].config(text=units)
    except Exception as e:
        messagebox.showerror("Error", f"Unable to refresh: {e}")

# This function updates units in DB when someone donates blood
def Donate_dbase():
    global bgrp, bunits, current_popup
    units = bunits.get()
    try:
        cursor.execute(f"SELECT units FROM BloodBank WHERE Blood_Grp='{bgrp}'")
        current_units = cursor.fetchone()
        if current_units:
            updated_units = str(int(current_units[0]) + int(units))
            cursor.execute(f"UPDATE BloodBank SET units='{updated_units}' WHERE Blood_Grp='{bgrp}'")
            db.commit()
            messagebox.showinfo('Success', "Blood Donated Successfully")
            current_popup.destroy()
            clear_popup()
            refresh_table()  # Refresh the units shown
        else:
            messagebox.showerror("Error", "Blood group not found")
    except Exception as e:
        messagebox.showerror("Database Error", str(e))

# This opens donate blood popup window
def donate(bg):
    global bgrp, bunits, current_popup
    if current_popup:
        messagebox.showwarning("Action Blocked", "Close the existing popup first.")
        return

    bgrp = bg
    top = Toplevel(root)
    current_popup = top
    top.protocol("WM_DELETE_WINDOW", lambda: top.destroy() or clear_popup())
    top.title("Donate Blood")
    top.geometry("400x200")
    top.configure(bg='#dbeafe')

    Label(top, text="Donate Blood", font=('Arial', 16, BOLD), bg='#dbeafe', fg='darkblue').pack(pady=10)
    Label(top, text="Enter number of units:", font=('Arial', 12), bg='#dbeafe', fg='black').pack()

    bunits = Entry(top, font=('Arial', 12))
    bunits.pack(pady=10)

    Button(top, text="Submit", command=Donate_dbase, bg="#dc2626", fg="black", font=('Arial', 12)).pack(pady=10)

# This function is for requesting blood from DB
def Request_dbase():
    global bgrp, bunits, current_popup
    units = bunits.get()
    try:
        cursor.execute(f"SELECT units FROM BloodBank WHERE Blood_Grp='{bgrp}'")
        current_units = cursor.fetchone()
        if current_units and int(current_units[0]) >= int(units):
            updated_units = str(int(current_units[0]) - int(units))
            cursor.execute(f"UPDATE BloodBank SET units='{updated_units}' WHERE Blood_Grp='{bgrp}'")
            db.commit()
            messagebox.showinfo('Success', "Blood Request Successful")
            current_popup.destroy()
            clear_popup()
            refresh_table()  # Refresh values on GUI
        else:
            messagebox.showwarning("Unavailable", "Not enough units available")
    except Exception as e:
        messagebox.showerror("Database Error", str(e))

# This opens the request blood popup window
def request(bg):
    global bgrp, bunits, current_popup
    if current_popup:
        messagebox.showwarning("Action Blocked", "Close the existing popup first.")
        return

    bgrp = bg
    top = Toplevel(root)
    current_popup = top
    top.protocol("WM_DELETE_WINDOW", lambda: top.destroy() or clear_popup())
    top.title("Request Blood")
    top.geometry("400x200")
    top.configure(bg='#fde68a')

    Label(top, text="Request Blood", font=('Arial', 16, BOLD), bg='#dbeafe', fg='darkblue').pack(pady=10)
    Label(top, text="Enter number of units:", font=('Arial', 12), bg='#dbeafe', fg='black').pack()

    bunits = Entry(top, font=('Arial', 12))
    bunits.pack(pady=10)

    Button(top, text="Submit", command=Request_dbase, bg="#dc2626", fg="black", font=('Arial', 12)).pack(pady=10)

# Title of app
Label(root, text="Blood Donation Management System", font=('Arial', 24, BOLD), bg='#f4f4f4', fg='darkred').pack(pady=20)

# Table frame for showing blood groups and units
frame = Frame(root, bg='#ffffff', bd=2, relief=RIDGE)
frame.pack(fill=BOTH, expand=True, padx=20, pady=10)

# Header row
header_bg = '#1f2937'
header_fg = 'white'

Label(frame, text="Blood Group", font=('Arial', 14, BOLD), width=15, bg=header_bg, fg=header_fg).grid(row=0, column=0, padx=5, pady=5)
Label(frame, text="Available Units", font=('Arial', 14, BOLD), width=15, bg=header_bg, fg=header_fg).grid(row=0, column=1, padx=5, pady=5)
Label(frame, text="Actions", font=('Arial', 14, BOLD), width=30, bg=header_bg, fg=header_fg).grid(row=0, column=2, columnspan=2, padx=5, pady=5)

# Now show all blood groups from database
try:
    cursor.execute("SELECT * FROM BloodBank")
    for i, (bg, units) in enumerate(cursor.fetchall(), start=1):
        Label(frame, text=bg, font=('Arial', 12), width=15).grid(row=i, column=0, padx=5, pady=5)

        # Label where units will be updated dynamically
        unit_label = Label(frame, text=units, font=('Arial', 12), width=15)
        unit_label.grid(row=i, column=1, padx=5, pady=5)
        unit_labels[bg] = unit_label  # Save for refresh

        # Buttons to donate or request blood
        Button(frame, text="Donate", command=lambda b=bg: donate(b), bg="#2563eb", fg="black", font=('Arial', 10)).grid(row=i, column=2, padx=5, pady=5)
        Button(frame, text="Request", command=lambda b=bg: request(b), bg="#dc2626", fg="black", font=('Arial', 10)).grid(row=i, column=3, padx=5, pady=5)
except Exception as e:
    messagebox.showerror("Error", f"Unable to fetch data: {e}")

# Start the application
root.mainloop()
