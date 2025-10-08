import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from uuid import uuid4
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Optional


# -------------------------
# Data models
# -------------------------
@dataclass
class Patient:
    name: str
    email: str


@dataclass
class Appointment:
    id: str
    patient: Patient
    date: str
    time: str
    dentist: str
    status: str = "Pending"  # Added status field
    booked_at: datetime = field(default_factory=datetime.now)


# -------------------------
# Manager class
# -------------------------
class AppointmentManager:
    def __init__(self):
        self.appointments: Dict[str, Appointment] = {}
        self.dentists = ["Dr. Jhunsoy Love Jun", "Dr. Jograd Ballesteros ", "Dr. Beyoncé Calubaquib",
                         "Dr. Estanislao Manansala", "Dr.  Federico Liwanag VII", "Dr. Vergamino Antiporda",
                         "Dr. Princess Payapa Pamplona"]
        # Admin credentials (in real app, use proper authentication)
        self.admin_username = "admin"
        self.admin_password = "admin123"
        # Available time slots
        self.time_slots = [
            "08:00 AM", "08:30 AM", "09:00 AM", "09:30 AM",
            "10:00 AM", "10:30 AM", "11:00 AM", "11:30 AM",
            "01:00 PM", "01:30 PM", "02:00 PM", "02:30 PM",
            "03:00 PM", "03:30 PM", "04:00 PM", "04:30 PM",
            "05:00 PM", "05:30 PM"
        ]

    def verify_admin(self, username: str, password: str) -> bool:
        """Verify admin credentials"""
        return username == self.admin_username and password == self.admin_password

    def reserve(self, patient: Patient, date: str, time: str, dentist: str) -> Optional[Appointment]:
        # Check if the time slot is already taken for this dentist and date
        for appt in self.appointments.values():
            if appt.dentist == dentist and appt.date == date and appt.time == time:
                return None  # Time slot already taken
        appt_id = str(uuid4())[:8]
        appointment = Appointment(appt_id, patient, date, time, dentist, "Pending")
        self.appointments[appt_id] = appointment
        return appointment

    def is_time_slot_available(self, dentist: str, date: str, time: str) -> bool:
        """Check if a time slot is available for a specific dentist and date"""
        for appt in self.appointments.values():
            if appt.dentist == dentist and appt.date == date and appt.time == time:
                return False
        return True

    def get_available_slots(self, dentist: str, date: str) -> List[str]:
        """Get all available time slots for a dentist on a specific date"""
        available = []
        for time_slot in self.time_slots:
            if self.is_time_slot_available(dentist, date, time_slot):
                available.append(time_slot)
        return available

    def cancel(self, appt_id: str) -> bool:
        return self.appointments.pop(appt_id, None) is not None

    def cancel_by_email(self, email: str) -> bool:
        """Cancel appointment by patient email"""
        for appt_id, appt in list(self.appointments.items()):
            if appt.patient.email == email:
                del self.appointments[appt_id]
                return True
        return False

    def confirm_appointment(self, appt_id: str) -> bool:
        """Confirm an appointment"""
        if appt_id in self.appointments:
            self.appointments[appt_id].status = "Confirmed"
            return True
        return False

    def decline_appointment(self, appt_id: str) -> bool:
        """Decline an appointment"""
        if appt_id in self.appointments:
            self.appointments[appt_id].status = "Declined"
            return True
        return False

    def all_appointments(self) -> List[Appointment]:
        return list(self.appointments.values())


# -------------------------
# GUI Application
# -------------------------
class DentalApp:
    def __init__(self, root):
        self.manager = AppointmentManager()
        self.root = root
        self.root.title("ToothPearl Dental Clinic")
        self.root.geometry("1200x700")
        self.root.resizable(False, False)

        # ---------- Load background image once ----------
        try:
            original_image = Image.open("clinic.bg.png")
            resized = original_image.resize((1200, 700), Image.LANCZOS)
            self.bg_photo = ImageTk.PhotoImage(resized)
            self.bg_label = tk.Label(self.root, image=self.bg_photo)
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            # fallback if image not found / cannot load
            print("Warning: Could not load background image:", e)
            self.bg_label = tk.Label(self.root, bg="white")
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # show the first page
        self.show_main_menu()

    def clear_container(self):
        """Destroy only widgets that were created inside the background label."""
        for widget in self.bg_label.winfo_children():
            widget.destroy()

    # ---------------- Main Menu ----------------
    def show_main_menu(self):
        self.clear_container()

        # HEADER
        header = tk.Label(
            self.bg_label,
            text="TOOTHPEARL DENTAL CLINIC",
            font=("Impact", 32, "bold"),
            bg="#000000",
            fg="white"
        )
        header.place(x=40, y=80)

        # NAV BAR
        nav_buttons = [
            ("SERVICES", self.show_services),
            ("PRICING", self.show_pricing),
            ("ABOUT US", self.show_about_us),
            ("NEED HELP?", self.show_need_help),
        ]

        for idx, (text, cmd) in enumerate(nav_buttons):
            btn = tk.Button(
                self.bg_label,
                text=text,
                font=("Arial", 12, "bold"),
                bg="#FFCC00",
                fg="black",
                padx=15,
                pady=8,
                relief="flat",
                bd=0,
                highlightthickness=0,
                activebackground="#FFCC00",
                activeforeground="black",
                cursor="hand2",
                command=cmd if cmd else None
            )
            btn.place(x=300 + (idx * 180), y=20)
            btn.bind("<FocusIn>", lambda e: e.widget.config(relief="flat"))
            btn.bind("<FocusOut>", lambda e: e.widget.config(relief="flat"))

        # ACTION BUTTONS (3 buttons now, removed VIEW APPOINTMENTS)
        button_actions = [
            ("BOOK NOW", self.book_appointment_form),
            ("CANCEL BOOKING", self.cancel_appointment_form),
            ("REBOOK", self.rebook_form),
        ]

        for idx, (text, cmd) in enumerate(button_actions):
            btn = tk.Button(
                self.bg_label,
                text=text,
                font=("Arial Black", 14),
                bg="#FFEB3B",
                fg="black",
                width=20,
                height=2,
                relief="flat",
                bd=0,
                highlightthickness=0,
                activebackground="#FFEB3B",
                activeforeground="black",
                cursor="hand2",
                command=cmd
            )
            btn.place(x=50, y=200 + (idx * 100))
            btn.bind("<FocusIn>", lambda e: e.widget.config(relief="flat"))
            btn.bind("<FocusOut>", lambda e: e.widget.config(relief="flat"))

        # EXIT BUTTON (4th position, same color as other buttons)
        exit_btn = tk.Button(
            self.bg_label,
            text="EXIT",
            font=("Arial Black", 14),
            bg="#FFEB3B",
            fg="black",
            width=20,
            height=2,
            relief="flat",
            bd=0,
            highlightthickness=0,
            activebackground="#FFEB3B",
            activeforeground="black",
            cursor="hand2",
            command=self.root.quit
        )
        exit_btn.place(x=50, y=500)
        exit_btn.bind("<FocusIn>", lambda e: e.widget.config(relief="flat"))
        exit_btn.bind("<FocusOut>", lambda e: e.widget.config(relief="flat"))

        # ADMIN LOGIN BUTTON (small yellow button, moved to far right)
        admin_btn = tk.Button(
            self.bg_label,
            text="Log In",
            font=("Arial", 10, "bold"),
            bg="#FFCC00",
            fg="black",
            width=10,
            height=1,
            relief="flat",
            bd=0,
            highlightthickness=0,
            activebackground="#FFCC00",
            activeforeground="black",
            cursor="hand2",
            command=self.show_login_page
        )
        admin_btn.place(x=1080, y=610)
        admin_btn.bind("<FocusIn>", lambda e: e.widget.config(relief="flat"))
        admin_btn.bind("<FocusOut>", lambda e: e.widget.config(relief="flat"))

    # ---------------- Admin Login Page ----------------
    def show_login_page(self):
        self.clear_container()

        # Title frame
        title_frame = tk.Frame(self.bg_label, bg="#FFEB3B", height=100)
        title_frame.pack(fill="x")
        title_frame.pack_propagate(False)
        tk.Label(
            title_frame,
            text="ADMIN LOGIN",
            font=("Arial Black", 32, "bold"),
            bg="#FFEB3B",
            fg="black"
        ).pack(expand=True)

        # Content frame
        content_frame = tk.Frame(self.bg_label, bg="#F5F5F5")
        content_frame.pack(fill="both", expand=True)

        # Login form container
        login_container = tk.Frame(content_frame, bg="#F5F5F5")
        login_container.place(relx=0.5, rely=0.45, anchor="center")

        # Username field
        username_frame = tk.Frame(login_container, bg="#F5F5F5")
        username_frame.pack(pady=20)

        tk.Label(
            username_frame,
            text="Username",
            font=("Arial", 16, "bold"),
            bg="#EAB308",
            fg="black",
            anchor="w",
            padx=10,
            width=20
        ).pack(fill="x", pady=(0, 8))

        username_entry = tk.Entry(
            username_frame,
            width=30,
            font=("Arial", 15),
            bg="#D9D9D9",
            relief="flat"
        )
        username_entry.pack(ipady=8)

        # Password field
        password_frame = tk.Frame(login_container, bg="#F5F5F5")
        password_frame.pack(pady=20)

        tk.Label(
            password_frame,
            text="Password",
            font=("Arial", 16, "bold"),
            bg="#EAB308",
            fg="black",
            anchor="w",
            padx=10,
            width=20
        ).pack(fill="x", pady=(0, 8))

        password_entry = tk.Entry(
            password_frame,
            width=30,
            font=("Arial", 15),
            bg="#D9D9D9",
            relief="flat",
            show="●"
        )
        password_entry.pack(ipady=8)

        # Button frame
        button_frame = tk.Frame(login_container, bg="#F5F5F5")
        button_frame.pack(pady=30)

        def attempt_login():
            username = username_entry.get().strip()
            password = password_entry.get().strip()

            if self.manager.verify_admin(username, password):
                messagebox.showinfo("Success", "Login successful!")
                self.show_admin_page()
            else:
                messagebox.showerror("Error", "Invalid username or password!")
                password_entry.delete(0, "end")

        tk.Button(
            button_frame,
            text="BACK",
            bg="#EAB308",
            fg="black",
            font=("Arial", 14, "bold"),
            width=12,
            height=1,
            relief="flat",
            bd=0,
            highlightthickness=0,
            activebackground="#EAB308",
            command=self.show_main_menu,
            cursor="hand2"
        ).pack(side="left", padx=10)

        tk.Button(
            button_frame,
            text="LOGIN",
            bg="#4CAF50",
            fg="white",
            font=("Arial", 14, "bold"),
            width=12,
            height=1,
            relief="flat",
            bd=0,
            highlightthickness=0,
            activebackground="#45a049",
            command=attempt_login,
            cursor="hand2"
        ).pack(side="left", padx=10)

        # Bind Enter key to login
        password_entry.bind("<Return>", lambda e: attempt_login())
        username_entry.bind("<Return>", lambda e: password_entry.focus())

    def show_admin_page(self):
        self.clear_container()

        # Title bar
        title_frame = tk.Frame(self.bg_label, bg="#FFEB3B", height=100)
        title_frame.pack(fill="x")
        title_frame.pack_propagate(False)
        tk.Label(
            title_frame,
            text="ADMIN DASHBOARD - MANAGE APPOINTMENTS",
            font=("Arial Black", 28, "bold"),
            bg="#FFEB3B",
            fg="black"
        ).pack(expand=True)

        # Content frame
        content_frame = tk.Frame(self.bg_label, bg="#F5F5F5")
        content_frame.pack(fill="both", expand=True)

        # Table container
        table_container = tk.Frame(content_frame, bg="#F5F5F5")
        table_container.pack(fill="both", expand=True, padx=40, pady=20)

        # Style for treeview - Updated with borders
        # Style for treeview - Updated with borders
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Admin.Treeview",
                        background="#D9D9D9",
                        foreground="black",
                        rowheight=40,
                        fieldbackground="#D9D9D9",
                        borderwidth=2,
                        relief="solid")
        style.configure("Admin.Treeview.Heading",
                        background="#4A90E2",
                        foreground="white",
                        font=("Arial", 12, "bold"),
                        borderwidth=2,
                        relief="solid")
        style.map("Admin.Treeview",
                  background=[("selected", "#CFCFCF")],  # light gray
                  foreground=[("selected", "black")])  # keep text visible
        style.map("Admin.Treeview.Heading",
                  background=[("active", "#4A90E2")])

        # Create treeview with border
        tree_frame = tk.Frame(table_container, bg="#4A90E2", bd=2, relief="solid")
        tree_frame.pack(fill="both", expand=True)

        tree = ttk.Treeview(
            tree_frame,
            columns=("id", "name", "email", "date", "time", "dentist", "status"),
            show="headings",
            style="Admin.Treeview",
            height=10
        )

        # Define headings
        tree.heading("id", text="ID")
        tree.heading("name", text="Patient Name")
        tree.heading("email", text="Email Address")
        tree.heading("date", text="Date")
        tree.heading("time", text="Time")
        tree.heading("dentist", text="Dentist")
        tree.heading("status", text="Status")

        # Define column widths and alignments
        tree.column("id", width=80, anchor="center")
        tree.column("name", width=150, anchor="w")
        tree.column("email", width=220, anchor="w")
        tree.column("date", width=100, anchor="center")
        tree.column("time", width=100, anchor="center")
        tree.column("dentist", width=150, anchor="w")
        tree.column("status", width=100, anchor="center")

        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        # Pack tree and scrollbar
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Function to refresh the table
        def refresh_table():
            # Clear existing items
            for item in tree.get_children():
                tree.delete(item)

            # Insert data
            appointments = self.manager.all_appointments()
            if appointments:
                for appt in appointments:
                    # Color code by status
                    tag = ""
                    if appt.status == "Confirmed":
                        tag = "confirmed"
                    elif appt.status == "Declined":
                        tag = "declined"
                    elif appt.status == "Pending":
                        tag = "pending"

                    tree.insert("", "end", values=(
                        appt.id,
                        appt.patient.name,
                        appt.patient.email,
                        appt.date,
                        appt.time,
                        appt.dentist,
                        appt.status
                    ), tags=(tag,))

            # Configure tags for colors (keeping your original color coding)
            tree.tag_configure("confirmed", background="#C8E6C9")
            tree.tag_configure("declined", background="#FFCDD2")
            tree.tag_configure("pending", background="#FFF9C4")

        # Initial load
        refresh_table()

        # Action buttons frame
        action_frame = tk.Frame(content_frame, bg="#F5F5F5")
        action_frame.pack(pady=15)

        def confirm_selected():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Warning", "Please select an appointment to confirm!")
                return

            item = tree.item(selected[0])
            appt_id = item['values'][0]

            if self.manager.confirm_appointment(appt_id):
                messagebox.showinfo("Success", f"Appointment {appt_id} confirmed!")
                refresh_table()
            else:
                messagebox.showerror("Error", "Failed to confirm appointment!")

        def decline_selected():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Warning", "Please select an appointment to decline!")
                return

            item = tree.item(selected[0])
            appt_id = item['values'][0]

            result = messagebox.askyesno("Confirm Decline",
                                         f"Are you sure you want to decline appointment {appt_id}?")
            if result:
                if self.manager.decline_appointment(appt_id):
                    messagebox.showinfo("Success", f"Appointment {appt_id} declined!")
                    refresh_table()
                else:
                    messagebox.showerror("Error", "Failed to decline appointment!")

        def delete_selected():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Warning", "Please select an appointment to delete!")
                return

            item = tree.item(selected[0])
            appt_id = item['values'][0]

            result = messagebox.askyesno("Confirm Delete",
                                         f"Are you sure you want to permanently delete appointment {appt_id}?")
            if result:
                if self.manager.cancel(appt_id):
                    messagebox.showinfo("Success", f"Appointment {appt_id} deleted!")
                    refresh_table()
                else:
                    messagebox.showerror("Error", "Failed to delete appointment!")

        # Action buttons
        tk.Button(
            action_frame,
            text="✓ CONFIRM",
            bg="#4CAF50",
            fg="white",
            font=("Arial", 12, "bold"),
            width=15,
            height=1,
            relief="flat",
            bd=0,
            highlightthickness=0,
            activebackground="#45a049",
            command=confirm_selected,
            cursor="hand2"
        ).pack(side="left", padx=10)

        tk.Button(
            action_frame,
            text="✗ DECLINE",
            bg="#FF9800",
            fg="white",
            font=("Arial", 12, "bold"),
            width=15,
            height=1,
            relief="flat",
            bd=0,
            highlightthickness=0,
            activebackground="#F57C00",
            command=decline_selected,
            cursor="hand2"
        ).pack(side="left", padx=10)

        tk.Button(
            action_frame,
            text="🗑 DELETE",
            bg="#F44336",
            fg="white",
            font=("Arial", 12, "bold"),
            width=15,
            height=1,
            relief="flat",
            bd=0,
            highlightthickness=0,
            activebackground="#D32F2F",
            command=delete_selected,
            cursor="hand2"
        ).pack(side="left", padx=10)

        tk.Button(
            action_frame,
            text="↻ REFRESH",
            bg="#2196F3",
            fg="white",
            font=("Arial", 12, "bold"),
            width=15,
            height=1,
            relief="flat",
            bd=0,
            highlightthickness=0,
            activebackground="#1976D2",
            command=refresh_table,
            cursor="hand2"
        ).pack(side="left", padx=10)

        # Statistics label
        stats_text = f"Total Appointments: {len(self.manager.all_appointments())}"
        stats_label = tk.Label(
            action_frame,
            text=stats_text,
            font=("Arial", 11, "bold"),
            bg="#F5F5F5",
            fg="#666666"
        )
        stats_label.pack(side="left", padx=20)

        # Bottom buttons
        bottom_frame = tk.Frame(content_frame, bg="#F5F5F5")
        bottom_frame.pack(side="bottom", pady=15)

        tk.Button(
            bottom_frame,
            text="LOGOUT",
            bg="#EAB308",
            fg="black",
            font=("Arial", 14, "bold"),
            width=15,
            height=1,
            relief="flat",
            bd=0,
            highlightthickness=0,
            activebackground="#D4A307",
            command=self.show_main_menu,
            cursor="hand2"
        ).pack()

    # ---------------- Booking Form ----------------
    def book_appointment_form(self):
        self.clear_container()

        # Title frame
        title_frame = tk.Frame(self.bg_label, bg="#FFEB3B", height=100)
        title_frame.pack(fill="x")
        title_frame.pack_propagate(False)
        tk.Label(
            title_frame,
            text="TOOTHPEARL DENTAL CLINIC",
            font=("Arial Black", 32, "bold"),
            bg="#FFEB3B",
            fg="black"
        ).pack(expand=True)

        content_frame = tk.Frame(self.bg_label, bg="#F5F5F5")
        content_frame.pack(fill="both", expand=True)

        form_container = tk.Frame(content_frame, bg="#F5F5F5")
        form_container.place(relx=0.5, rely=0.5, anchor="center")

        # --- helper to create entry with placeholder behavior ---
        def make_entry_with_placeholder(parent, placeholder, **entry_opts):
            entry = tk.Entry(parent, **entry_opts)
            ph = placeholder
            entry.insert(0, ph)
            entry.config(fg="grey")

            def on_focus_in(event, e=entry, ph=ph):
                if e.get() == ph:
                    e.delete(0, "end")
                    e.config(fg="black")

            def on_focus_out(event, e=entry, ph=ph):
                if not e.get().strip():
                    e.insert(0, ph)
                    e.config(fg="grey")

            entry.bind("<FocusIn>", on_focus_in)
            entry.bind("<FocusOut>", on_focus_out)
            return entry

        # ROW 1
        row1_frame = tk.Frame(form_container, bg="#F5F5F5")
        row1_frame.pack(pady=(40, 20))

        name_frame = tk.Frame(row1_frame, bg="#F5F5F5")
        name_frame.pack(side="left", padx=(0, 60))
        tk.Label(
            name_frame,
            text="Name",
            font=("Arial", 16),
            bg="#EAB308",
            fg="black",
            anchor="w",
            padx=5
        ).pack(fill="x", pady=(0, 8))

        name_placeholder = "Ex. Justine Nabunturan"
        name_entry = make_entry_with_placeholder(
            name_frame,
            name_placeholder,
            width=40, font=("Arial", 15), bg="#D9D9D9", relief="flat"
        )
        name_entry.pack(ipady=6)

        dentist_frame = tk.Frame(row1_frame, bg="#F5F5F5")
        dentist_frame.pack(side="left")
        tk.Label(
            dentist_frame,
            text="Preferred Dentist",
            font=("Arial", 16),
            bg="#EAB308",
            fg="black",
            anchor="w",
            padx=5
        ).pack(fill="x", pady=(0, 8))

        dentist_combo = ttk.Combobox(dentist_frame, values=self.manager.dentists, state="readonly",
                                     width=38, font=("Arial", 14))
        dentist_combo.set("Ex. Dr. Jhunsuy Love Jun")
        dentist_combo.pack()

        # ROW 2
        row2_frame = tk.Frame(form_container, bg="#F5F5F5")
        row2_frame.pack(pady=20)
        gender_frame = tk.Frame(row2_frame, bg="#F5F5F5")
        gender_frame.pack(side="left", padx=(5, 60))
        tk.Label(
            gender_frame,
            text="Gender",
            font=("Arial", 16),
            bg="#EAB308",
            fg="black",
            anchor="w",
            padx=5
        ).pack(fill="x", pady=(0, 8))

        radio_container = tk.Frame(gender_frame, bg="#D9D9D9", width=440, height=45)
        radio_container.pack()
        radio_container.pack_propagate(False)

        gender_var = tk.StringVar(value="N/A")
        radio_inner = tk.Frame(radio_container, bg="#D9D9D9")
        radio_inner.pack(anchor="w", padx=10, pady=8)
        tk.Radiobutton(radio_inner, text="Male", variable=gender_var, value="Male",
                       bg="#D9D9D9", font=("Arial", 12), activebackground="#D9D9D9").pack(side="left", padx=(0, 15))
        tk.Radiobutton(radio_inner, text="Female", variable=gender_var, value="Female",
                       bg="#D9D9D9", font=("Arial", 12), activebackground="#D9D9D9").pack(side="left", padx=(0, 15))
        tk.Radiobutton(radio_inner, text="Prefer not to say", variable=gender_var, value="N/A",
                       bg="#D9D9D9", font=("Arial", 12), activebackground="#D9D9D9").pack(side="left")

        email_frame = tk.Frame(row2_frame, bg="#F5F5F5")
        email_frame.pack(side="left")
        tk.Label(
            email_frame,
            text="Email address",
            font=("Arial", 16),
            bg="#EAB308",
            fg="black",
            anchor="w",
            padx=5
        ).pack(fill="x", pady=(0, 8))

        email_placeholder = "Ex. j.nabunturan1111@umindanao.edu.ph"
        email_entry = make_entry_with_placeholder(
            email_frame,
            email_placeholder,
            width=40, font=("Arial", 15), bg="#D9D9D9", relief="flat"
        )
        email_entry.pack(ipady=6)

        # ROW 3
        row3_frame = tk.Frame(form_container, bg="#F5F5F5")
        row3_frame.pack(pady=20)
        reason_frame = tk.Frame(row3_frame, bg="#F5F5F5")
        reason_frame.pack(side="left", padx=(0, 60))
        tk.Label(
            reason_frame,
            text="Reason for Visit",
            font=("Arial", 16),
            bg="#EAB308",
            fg="black",
            anchor="w",
            padx=5
        ).pack(fill="x", pady=(0, 8))

        reason_placeholder = "Ex. Wisdom tooth Root canal"

        reason_text = tk.Text(
            reason_frame,
            width=40,
            height=5,
            font=("Arial", 14),
            bg="#D9D9D9",
            relief="flat",
            wrap="word"
        )
        reason_text.pack()

        reason_text.insert("1.0", reason_placeholder)
        reason_text.config(fg="gray")

        def on_focus_in(event):
            if reason_text.get("1.0", "end-1c") == reason_placeholder:
                reason_text.delete("1.0", "end")
                reason_text.config(fg="black")

        def on_focus_out(event):
            if reason_text.get("1.0", "end-1c").strip() == "":
                reason_text.insert("1.0", reason_placeholder)
                reason_text.config(fg="gray")

        reason_text.bind("<FocusIn>", on_focus_in)
        reason_text.bind("<FocusOut>", on_focus_out)

        # DATE AND TIME SELECTION
        datetime_frame = tk.Frame(row3_frame, bg="#F5F5F5")
        datetime_frame.pack(side="left")

        tk.Label(
            datetime_frame,
            text="SELECT DATE & TIME",
            font=("Arial", 16),
            bg="#EAB308",
            fg="black",
            anchor="w",
            padx=5
        ).pack(fill="x", pady=(0, 8))

        datetime_container = tk.Frame(datetime_frame, bg="#D9D9D9", width=440, height=200)
        datetime_container.pack()
        datetime_container.pack_propagate(False)

        # --- New Scrollable Date Selectors ---
        date_inner = tk.Frame(datetime_container, bg="#D9D9D9")
        date_inner.pack(fill="x", padx=10, pady=(10, 5))

        tk.Label(
            date_inner,
            text="Date:",
            font=("Arial", 12, "bold"),
            bg="#D9D9D9",
            fg="black"
        ).pack(side="left", padx=(0, 10))

        month_var = tk.StringVar(value="1")
        day_var = tk.StringVar(value="1")
        year_var = tk.StringVar(value="2025")

        month_spin = tk.Spinbox(date_inner, from_=1, to=12, wrap=True, width=5,
                                font=("Arial", 12), justify="center", textvariable=month_var,
                                state="readonly", relief="flat")
        month_spin.pack(side="left", padx=(0, 5))

        day_spin = tk.Spinbox(date_inner, from_=1, to=31, wrap=True, width=5,
                              font=("Arial", 12), justify="center", textvariable=day_var,
                              state="readonly", relief="flat")
        day_spin.pack(side="left", padx=(0, 5))

        year_spin = tk.Spinbox(date_inner, from_=2025, to=2030, wrap=True, width=7,
                               font=("Arial", 12), justify="center", textvariable=year_var,
                               state="readonly", relief="flat")
        year_spin.pack(side="left", padx=(0, 5))

        def get_selected_date():
            return f"{month_var.get().zfill(2)}/{day_var.get().zfill(2)}/{year_var.get()}"

        # Time slots
        time_label = tk.Label(
            datetime_container,
            text="Available Times (select dentist & date first):",
            font=("Arial", 10),
            bg="#D9D9D9",
            fg="#666666"
        )
        time_label.pack(pady=(5, 5))

        time_canvas = tk.Canvas(datetime_container, bg="#D9D9D9", height=100, highlightthickness=0)
        time_scrollbar = tk.Scrollbar(datetime_container, orient="vertical", command=time_canvas.yview)
        time_slots_frame = tk.Frame(time_canvas, bg="#D9D9D9")

        time_canvas.configure(yscrollcommand=time_scrollbar.set)
        time_canvas.pack(side="left", fill="both", expand=True, padx=(10, 0))
        time_scrollbar.pack(side="right", fill="y", padx=(0, 10))

        canvas_frame = time_canvas.create_window((0, 0), window=time_slots_frame, anchor="nw")

        selected_time = tk.StringVar(value="")

        def update_time_slots():
            for widget in time_slots_frame.winfo_children():
                widget.destroy()

            date = get_selected_date()

            # Show all available slots immediately (ignore dentist)
            if hasattr(self.manager, "time_slots"):
                available_slots = self.manager.time_slots
            else:
                available_slots = [
                    "08:00 AM", "08:30 AM", "09:00 AM", "09:30 AM", "10:00 AM",
                    "10:30 AM", "11:00 AM", "11:30 AM", "01:00 PM", "01:30 PM",
                    "02:00 PM", "02:30 PM"
                ]

            # Update label right away with the date
            time_label.config(
                text=f"✓ {len(available_slots)} available time slots for {date}",
                fg="#4CAF50"
            )

            row, col = 0, 0
            current_selected = selected_time.get()

            for time_slot in available_slots:
                is_selected = time_slot == current_selected
                bg_color = "#FFF59D" if is_selected else "#C8E6C9"

                btn = tk.Button(
                    time_slots_frame,
                    text=time_slot,
                    font=("Arial", 9, "bold" if is_selected else "normal"),
                    width=10, height=1,
                    bg=bg_color,
                    fg="black",
                    relief="flat",
                    cursor="hand2",
                    command=lambda t=time_slot: select_time(t)
                )
                btn.grid(row=row, column=col, padx=3, pady=3)
                col += 1
                if col > 2:
                    col = 0
                    row += 1

            time_slots_frame.update_idletasks()
            time_canvas.config(scrollregion=time_canvas.bbox("all"))

        def select_time(time):
            selected_time.set(time)
            update_time_slots()

        def on_date_change(*args):
            update_time_slots()

        # ✅ Automatically show times on date change
        month_var.trace_add("write", on_date_change)
        day_var.trace_add("write", on_date_change)
        year_var.trace_add("write", on_date_change)

        # ✅ Keep dentist combo refresh optional (not required)
        dentist_combo.bind("<<ComboboxSelected>>", lambda e: update_time_slots())

        # ✅ Trigger once immediately so times show on load
        update_time_slots()

        # ✅ Bind scroll updates
        month_var.trace_add("write", on_date_change)
        day_var.trace_add("write", on_date_change)
        year_var.trace_add("write", on_date_change)
        dentist_combo.bind("<<ComboboxSelected>>", lambda e: update_time_slots())

        # BUTTON ROW
        button_frame = tk.Frame(form_container, bg="#F5F5F5")
        button_frame.pack(pady=(20, 20), anchor="e")

        def confirm_booking():
            name = name_entry.get().strip()
            if name == name_placeholder:
                name = ""

            email = email_entry.get().strip()
            if email == email_placeholder:
                email = ""

            date = get_selected_date()
            time = selected_time.get().strip()

            dentist = dentist_combo.get().strip()
            if dentist.startswith("Ex. "):
                dentist = dentist[4:].strip()
            if dentist == "" or dentist.lower().startswith("dr.") and dentist == "":
                dentist = ""

            gender = gender_var.get()

            reason = reason_text.get("1.0", "end-1c").strip()
            if reason == reason_placeholder:
                reason = ""

            if not all([name, email, date, dentist, gender, reason, time]):
                messagebox.showerror("Error", "All fields are required, including time slot!")
                return

            patient = Patient(name, email)
            appt = self.manager.reserve(patient, date, time, dentist)

            if appt:
                messagebox.showinfo(
                    "Success",
                    f"Appointment booked successfully!\n\nAppointment ID: {appt.id}\nPatient: {name}\nDentist: {dentist}\nDate: {date}\nTime: {time}\n\nStatus: Pending (awaiting admin approval)"
                )
                self.show_main_menu()
            else:
                messagebox.showwarning("Unavailable", "This time slot is already booked. Please select another time.")

        tk.Button(
            button_frame, text="BACK", bg="#EAB308", fg="black",
            font=("Arial", 14, "bold"), width=12, height=1, relief="flat",
            bd=0, highlightthickness=0, activebackground="#EAB308",
            command=self.show_main_menu, cursor="hand2"
        ).pack(side="left", padx=10)

        tk.Button(
            button_frame, text="CONFIRM", bg="#EAB308", fg="black",
            font=("Arial", 14, "bold"), width=12, height=1, relief="flat",
            bd=0, highlightthickness=0, activebackground="#EAB308",
            command=confirm_booking, cursor="hand2"
        ).pack(side="left")

    # ---------------- Cancel ----------------
    def cancel_appointment_form(self):
        self.clear_container()

        # Title frame
        title_frame = tk.Frame(self.bg_label, bg="#FFEB3B", height=100)
        title_frame.pack(fill="x")
        title_frame.pack_propagate(False)
        tk.Label(
            title_frame,
            text="TOOTHPEARL DENTAL CLINIC",
            font=("Arial Black", 32, "bold"),
            bg="#FFEB3B",
            fg="black"
        ).pack(expand=True)

        # Main background
        content_frame = tk.Frame(self.bg_label, bg="white")
        content_frame.pack(fill="both", expand=True)

        # Centered container
        form_container = tk.Frame(content_frame, bg="white")
        form_container.place(relx=0.5, rely=0.5, anchor="center")

        # --- helper for entry with placeholder ---
        def make_entry_with_placeholder(parent, placeholder, **entry_opts):
            entry = tk.Entry(parent, **entry_opts)
            entry.insert(0, placeholder)
            entry.config(fg="grey")

            def on_focus_in(event):
                if entry.get() == placeholder:
                    entry.delete(0, "end")
                    entry.config(fg="black")

            def on_focus_out(event):
                if not entry.get().strip():
                    entry.insert(0, placeholder)
                    entry.config(fg="grey")

            entry.bind("<FocusIn>", on_focus_in)
            entry.bind("<FocusOut>", on_focus_out)
            return entry

        # ---------------- INPUT FIELDS ----------------

        # Name
        tk.Label(
            form_container,
            text="Name",
            font=("Arial", 16),
            bg="#EAB308",
            fg="black",
            anchor="center"
        ).pack(fill="x", pady=(10, 5))
        name_placeholder = "Ex. Justine Nabunturan"
        name_entry = make_entry_with_placeholder(
            form_container,
            name_placeholder,
            width=45, font=("Arial", 15),
            bg="#D9D9D9", relief="flat", justify="center"
        )
        name_entry.pack(ipady=8, pady=(0, 15))

        # Email
        tk.Label(
            form_container,
            text="Email Address",
            font=("Arial", 16),
            bg="#EAB308",
            fg="black",
            anchor="center"
        ).pack(fill="x", pady=(5, 5))
        email_placeholder = "Ex. j.nabunturan1111@umindanao.edu.ph"
        email_entry = make_entry_with_placeholder(
            form_container,
            email_placeholder,
            width=45, font=("Arial", 15),
            bg="#D9D9D9", relief="flat", justify="center"
        )
        email_entry.pack(ipady=8, pady=(0, 15))

        # Reason
        tk.Label(
            form_container,
            text="Reason",
            font=("Arial", 16),
            bg="#EAB308",
            fg="black",
            anchor="center"
        ).pack(fill="x", pady=(5, 5))
        reason_placeholder = "Ex. Change Date"
        reason_entry = make_entry_with_placeholder(
            form_container,
            reason_placeholder,
            width=45, font=("Arial", 15),
            bg="#D9D9D9", relief="flat", justify="center"
        )
        reason_entry.pack(ipady=8, pady=(0, 15))

        # ---------------- BUTTONS ----------------
        button_frame = tk.Frame(form_container, bg="white")
        button_frame.pack(pady=(20, 10), anchor="e")

        def cancel_now():
            name = name_entry.get().strip()
            email = email_entry.get().strip()
            reason = reason_entry.get().strip()

            if name == name_placeholder:
                name = ""
            if email == email_placeholder:
                email = ""
            if reason == reason_placeholder:
                reason = ""

            if not all([name, email, reason]):
                messagebox.showerror("Error", "All fields are required!")
                return

            if self.manager.cancel_by_email(email):
                messagebox.showinfo("Success", f"Appointment for {email} cancelled.")
                self.show_main_menu()
            else:
                messagebox.showerror("Error", "Appointment not found.")

        # BACK button
        tk.Button(
            button_frame,
            text="BACK",
            bg="#EAB308",
            fg="black",
            font=("Arial", 14, "bold"),
            width=10, height=1,
            relief="flat", bd=0,
            activebackground="#EAB308",
            cursor="hand2",
            command=self.show_main_menu
        ).pack(side="left", padx=10)

        # CONFIRM button
        tk.Button(
            button_frame,
            text="NEXT",
            bg="#EAB308",
            fg="black",
            font=("Arial", 14, "bold"),
            width=10, height=1,
            relief="flat", bd=0,
            activebackground="#EAB308",
            cursor="hand2",
            command=cancel_now
        ).pack(side="left", padx=10)

    # ---------------- Rebook Form ----------------
    def rebook_form(self):
        self.clear_container()

        # Title frame
        title_frame = tk.Frame(self.bg_label, bg="#FFEB3B", height=100)
        title_frame.pack(fill="x")
        title_frame.pack_propagate(False)
        tk.Label(
            title_frame,
            text="TOOTHPEARL DENTAL CLINIC",
            font=("Arial Black", 32, "bold"),
            bg="#FFEB3B",
            fg="black"
        ).pack(expand=True)

        # Main background (white, consistent with Cancel)
        content_frame = tk.Frame(self.bg_label, bg="white")
        content_frame.pack(fill="both", expand=True)

        form_container = tk.Frame(content_frame, bg="white")
        form_container.place(relx=0.5, rely=0.5, anchor="center")

        # --- helper for entry with placeholder ---
        def make_entry_with_placeholder(parent, placeholder, **entry_opts):
            entry = tk.Entry(parent, **entry_opts)
            ph = placeholder
            entry.insert(0, ph)
            entry.config(fg="grey")

            def on_focus_in(event, e=entry, ph=ph):
                if e.get() == ph:
                    e.delete(0, "end")
                    e.config(fg="black")

            def on_focus_out(event, e=entry, ph=ph):
                if not e.get().strip():
                    e.insert(0, ph)
                    e.config(fg="grey")

            entry.bind("<FocusIn>", on_focus_in)
            entry.bind("<FocusOut>", on_focus_out)
            return entry

        # ---------------- INPUT FIELDS ----------------

        # Name
        tk.Label(
            form_container,
            text="Name",
            font=("Arial", 16),
            bg="#EAB308",
            fg="black",
            anchor="center"
        ).pack(fill="x", pady=(10, 5))
        name_placeholder = "Ex. Justine Nabunturan"
        name_entry = make_entry_with_placeholder(
            form_container,
            name_placeholder,
            width=45, font=("Arial", 15),
            bg="#D9D9D9", relief="flat", justify="center"
        )
        name_entry.pack(ipady=8, pady=(0, 15))

        # Reason
        tk.Label(
            form_container,
            text="Reason",
            font=("Arial", 16),
            bg="#EAB308",
            fg="black",
            anchor="center"
        ).pack(fill="x", pady=(5, 5))
        reason_placeholder = "Ex. Change Date"
        reason_entry = make_entry_with_placeholder(
            form_container,
            reason_placeholder,
            width=45, font=("Arial", 15),
            bg="#D9D9D9", relief="flat", justify="center"
        )
        reason_entry.pack(ipady=8, pady=(0, 15))

        # Email
        tk.Label(
            form_container,
            text="Email Address",
            font=("Arial", 16),
            bg="#EAB308",
            fg="black",
            anchor="center"
        ).pack(fill="x", pady=(5, 5))
        email_placeholder = "Ex. j.nabunturan1111@umindanao.edu.ph"
        email_entry = make_entry_with_placeholder(
            form_container,
            email_placeholder,
            width=45, font=("Arial", 15),
            bg="#D9D9D9", relief="flat", justify="center"
        )
        email_entry.pack(ipady=8, pady=(0, 15))

        # ---------------- BUTTONS ----------------
        button_frame = tk.Frame(form_container, bg="white")
        # lower position + right alignment
        button_frame.pack(pady=(60, 10), anchor="e", padx=40)

        def next_to_booking():
            name = name_entry.get().strip()
            email = email_entry.get().strip()
            reason = reason_entry.get().strip()

            if name == name_placeholder:
                name = ""
            if email == email_placeholder:
                email = ""
            if reason == reason_placeholder:
                reason = ""

            if not all([name, email, reason]):
                messagebox.showerror("Error", "All fields are required!")
                return

            # Cancel old appointment and redirect to booking form
            self.manager.cancel_by_email(email)
            self.book_appointment_form()

        # BACK button
        tk.Button(
            button_frame,
            text="BACK",
            bg="#EAB308",
            fg="black",
            font=("Arial", 14, "bold"),
            width=10, height=1,
            relief="flat", bd=0,
            activebackground="#EAB308",
            cursor="hand2",
            command=self.show_main_menu
        ).pack(side="left", padx=10)

        # NEXT button
        tk.Button(
            button_frame,
            text="NEXT",
            bg="#EAB308",
            fg="black",
            font=("Arial", 14, "bold"),
            width=10, height=1,
            relief="flat", bd=0,
            activebackground="#EAB308",
            cursor="hand2",
            command=next_to_booking
        ).pack(side="left", padx=10)

    # ---------------- Services Page ----------------
    def show_services(self):
        self.clear_container()

        # Title bar
        title_frame = tk.Frame(self.bg_label, bg="#FFEB3B", height=100)
        title_frame.pack(fill="x")
        title_frame.pack_propagate(False)
        tk.Label(
            title_frame,
            text="SERVICES",
            font=("Arial Black", 32, "bold"),
            bg="#FFEB3B",
            fg="black"
        ).pack(expand=True)

        # Content frame
        content_frame = tk.Frame(self.bg_label, bg="#F5F5F5")
        content_frame.pack(fill="both", expand=True)

        # 4 service columns
        services = {
            "General &\nPreventive": [
                "Dental check-ups / consultations",
                "Teeth cleaning (prophylaxis)",
                "Oral examinations & X-rays",
                "Fluoride treatments",
                "Sealants (to protect teeth from decay)"
            ],
            "Restorative\nDentistry": [
                "Fillings (for cavities)",
                "Crowns and bridges",
                "Dentures (partial or full)",
                "Dental implants",
                "Root canal treatment"
            ],
            "Cosmetic\nDentistry": [
                "Teeth whitening",
                "Veneers",
                "Bonding (fixing chipped or discolored teeth)",
                "Smile makeover consultations",
                "Braces (metal, ceramic, lingual)",
                "Invisalign or clear aligners",
                "Retainers"
            ],
            "Oral Surgery": [
                "Tooth extractions (regular or wisdom teeth)",
                "Surgical removal of impacted teeth",
                "Bone grafting"
            ]
        }

        # Grid layout for 4 columns
        services_frame = tk.Frame(content_frame, bg="#F5F5F5")
        services_frame.place(relx=0.5, rely=0.12, anchor="n")

        for i, (title, items) in enumerate(services.items()):
            col = tk.Frame(services_frame, bg="#D9D9D9", width=260, height=450)
            col.grid(row=0, column=i, padx=20, pady=10)
            col.pack_propagate(False)

            # Yellow header
            tk.Label(
                col, text=title, font=("Arial", 16, "bold"),
                bg="#EAB308", fg="black", height=2
            ).pack(fill="x")

            # Items
            items_frame = tk.Frame(col, bg="#D9D9D9")
            items_frame.pack(fill="both", expand=True, padx=10, pady=10)

            for item in items:
                tk.Label(
                    items_frame, text="• " + item,
                    font=("Arial", 12), bg="#D9D9D9", fg="black",
                    anchor="w", justify="left", wraplength=240
                ).pack(anchor="w", pady=2)

        # Back button
        tk.Button(
            content_frame, text="BACK", bg="#EAB308", fg="black",
            font=("Arial", 14, "bold"), width=12, height=1, relief="flat",
            bd=0, highlightthickness=0, activebackground="#EAB308",
            command=self.show_main_menu, cursor="hand2"
        ).pack(side="bottom", pady=20)

    def show_pricing(self):
        self.clear_container()

        # Title bar
        title_frame = tk.Frame(self.bg_label, bg="#FFEB3B", height=100)
        title_frame.pack(fill="x")
        title_frame.pack_propagate(False)
        tk.Label(
            title_frame,
            text="PRICING",
            font=("Arial Black", 32, "bold"),
            bg="#FFEB3B",
            fg="black"
        ).pack(expand=True)

        # Content frame with light gray background
        content_frame = tk.Frame(self.bg_label, bg="#F5F5F5")
        content_frame.pack(fill="both", expand=True)

        # Pricing data structure
        pricing_data = {
            "General & Preventive": [
                ("Dental check-up/consultation", "₱500 - ₱1,000"),
                ("Teeth cleaning (prophylaxis)", "₱1,000 - ₱2,500"),
                ("Oral examination & X-rays", "₱800 - ₱3,000"),
                ("Fluoride treatment", "₱500 - ₱1,500"),
                ("Sealants", "₱800 - ₱2,000 per tooth")
            ],
            "Restorative Dentistry": [
                ("Fillings", "₱1,500 - ₱5,000 per tooth"),
                ("Crowns", "₱8,000 - ₱25,000 per tooth"),
                ("Bridges", "₱15,000 - ₱50,000"),
                ("Dentures", "₱10,000 - ₱60,000"),
                ("Dental implants", "₱40,000 - ₱100,000 per tooth"),
                ("Root canal treatment", "₱5,000 - ₱15,000")
            ],
            "Cosmetic Dentistry": [
                ("Teeth whitening", "₱5,000 - ₱15,000"),
                ("Veneers", "₱15,000 - ₱40,000 per tooth"),
                ("Bonding", "₱2,000 - ₱8,000 per tooth"),
                ("Braces", "₱40,000 - ₱150,000"),
                ("Invisalign/clear aligners", "₱100,000 - ₱250,000"),
                ("Retainers", "₱3,000 - ₱10,000")
            ],
            "Oral Surgery": [
                ("Tooth extraction", "₱1,500 - ₱5,000"),
                ("Wisdom tooth removal", "₱5,000 - ₱15,000"),
                ("Surgical removal of impacted teeth", "₱8,000 - ₱20,000"),
                ("Bone grafting", "₱15,000 - ₱40,000")
            ]
        }

        # Main container - centered
        main_container = tk.Frame(content_frame, bg="#F5F5F5")
        main_container.place(relx=0.5, rely=0.45, anchor="center")

        # Create horizontal frame for all 4 categories side by side
        categories_frame = tk.Frame(main_container, bg="#F5F5F5")
        categories_frame.pack()

        # Create all 4 categories in a single row
        for category, items in pricing_data.items():
            # Category container
            cat_container = tk.Frame(categories_frame, bg="#F5F5F5")
            cat_container.pack(side="left", padx=12)

            # Category header
            header = tk.Frame(cat_container, bg="#EAB308", width=250, height=55)
            header.pack(fill="x")
            header.pack_propagate(False)

            tk.Label(
                header,
                text=category,
                font=("Arial", 13, "bold"),
                bg="#EAB308",
                fg="black"
            ).pack(expand=True)

            # Items container with tall vertical box
            items_container = tk.Frame(cat_container, bg="#D9D9D9", width=250, height=380)
            items_container.pack(fill="both")
            items_container.pack_propagate(False)

            # Items frame with padding
            items_frame = tk.Frame(items_container, bg="#D9D9D9")
            items_frame.pack(fill="both", expand=True, padx=12, pady=12)

            for service, price in items:
                # Service row
                service_row = tk.Frame(items_frame, bg="#D9D9D9")
                service_row.pack(fill="x", pady=5)

                tk.Label(
                    service_row,
                    text=f"• {service}",
                    font=("Arial", 10),
                    bg="#D9D9D9",
                    fg="black",
                    anchor="w",
                    justify="left",
                    wraplength=220
                ).pack(anchor="w", fill="x")

                # Price on separate line, indented
                tk.Label(
                    service_row,
                    text=price,
                    font=("Arial", 9, "bold"),
                    bg="#D9D9D9",
                    fg="black",
                    anchor="w"
                ).pack(anchor="w", padx=(10, 0))

        # Bottom section
        bottom_frame = tk.Frame(content_frame, bg="#F5F5F5")
        bottom_frame.pack(side="bottom", fill="x", pady=15)

        # Disclaimer
        tk.Label(
            bottom_frame,
            text="*Prices are estimates and may vary. Please contact us for accurate quotes.",
            font=("Arial", 9, "italic"),
            bg="#F5F5F5",
            fg="#666666"
        ).pack(pady=(0, 10))

        # Back button - centered
        back_btn_frame = tk.Frame(bottom_frame, bg="#F5F5F5")
        back_btn_frame.pack()

        tk.Button(
            back_btn_frame,
            text="BACK",
            bg="#EAB308",
            fg="black",
            font=("Arial", 14, "bold"),
            width=12,
            height=1,
            relief="flat",
            bd=0,
            highlightthickness=0,
            activebackground="#D4A307",
            command=self.show_main_menu,
            cursor="hand2"
        ).pack()

    # ---------------- About Us Page ----------------
    def show_about_us(self):
        self.clear_container()

        # Title bar
        title_frame = tk.Frame(self.bg_label, bg="#FFEB3B", height=100)
        title_frame.pack(fill="x")
        title_frame.pack_propagate(False)
        tk.Label(
            title_frame,
            text="ABOUT US",
            font=("Arial Black", 32, "bold"),
            bg="#FFEB3B",
            fg="black"
        ).pack(expand=True)

        # Content frame
        content_frame = tk.Frame(self.bg_label, bg="#F5F5F5")
        content_frame.pack(fill="both", expand=True)

        # Main container
        about_container = tk.Frame(content_frame, bg="#F5F5F5")
        about_container.place(relx=0.5, rely=0.4, anchor="center")

        # About content
        about_text = """Welcome to ToothPearl Dental Clinic!

At ToothPearl, we believe that everyone deserves a healthy, beautiful smile. Our clinic is dedicated to providing exceptional dental care in a comfortable and welcoming environment.

Our Mission
To deliver comprehensive, patient-centered dental care using the latest technology and techniques, while ensuring every visit is comfortable and stress-free.

Our Team
Our experienced team of dentists and hygienists are committed to continuing education and staying current with the latest advancements in dentistry. We treat each patient like family.

Why Choose Us?
• State-of-the-art equipment and facilities
• Experienced and caring dental professionals
• Comprehensive range of dental services
• Flexible scheduling and emergency care
• Comfortable and modern clinic environment
• Patient education and preventive care focus

We look forward to welcoming you to our dental family!"""

        tk.Label(
            about_container,
            text=about_text,
            font=("Arial", 13),
            bg="#F5F5F5",
            fg="black",
            justify="left",
            wraplength=900
        ).pack(pady=20, padx=50)

        # Back button
        tk.Button(
            content_frame, text="BACK", bg="#EAB308", fg="black",
            font=("Arial", 14, "bold"), width=12, height=1, relief="flat",
            bd=0, highlightthickness=0, activebackground="#EAB308",
            command=self.show_main_menu, cursor="hand2"
        ).pack(side="bottom", pady=20)

    # ---------------- Need Help Page ----------------
    def show_need_help(self):
        self.clear_container()

        # Title bar
        title_frame = tk.Frame(self.bg_label, bg="#FFEB3B", height=100)
        title_frame.pack(fill="x")
        title_frame.pack_propagate(False)
        tk.Label(
            title_frame,
            text="NEED HELP?",
            font=("Arial Black", 32, "bold"),
            bg="#FFEB3B",
            fg="black"
        ).pack(expand=True)

        # Content frame
        content_frame = tk.Frame(self.bg_label, bg="#F5F5F5")
        content_frame.pack(fill="both", expand=True)

        # Main container with grid layout
        help_container = tk.Frame(content_frame, bg="#F5F5F5")
        help_container.place(relx=0.5, rely=0.4, anchor="center")

        # Contact info sections in 2x2 grid
        contact_sections = [
            ("📞 Phone", [
                "Main Line: (082) 123-4567",
                "Emergency: (0917) 123-4567",
                "Available: Mon-Sat, 8AM-8PM"
            ]),
            ("📧 Email", [
                "General Inquiries: info@toothpearl.com",
                "Appointments: appointments@toothpearl.com",
                "We respond within 24 hours"
            ]),
            ("📍 Location", [
                "ToothPearl Dental Clinic",
                "123 Dental Street, Davao City",
                "Near City Hall, 2nd Floor"
            ]),
            ("🕐 Clinic Hours", [
                "Monday - Friday: 8:00 AM - 8:00 PM",
                "Saturday: 9:00 AM - 6:00 PM",
                "Sunday: Closed (Emergency calls only)"
            ])
        ]

        # Create 2x2 grid
        for idx, (title, items) in enumerate(contact_sections):
            row = idx // 2
            col = idx % 2

            # Section frame
            section = tk.Frame(help_container, bg="#D9D9D9", width=480, height=180)
            section.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")
            section.pack_propagate(False)

            # Title
            tk.Label(
                section,
                text=title,
                font=("Arial", 15, "bold"),
                bg="#EAB308",
                fg="black",
                anchor="w",
                padx=20,
                pady=10
            ).pack(fill="x")

            # Items
            for item in items:
                tk.Label(
                    section,
                    text=item,
                    font=("Arial", 12),
                    bg="#D9D9D9",
                    fg="black",
                    anchor="w",
                    padx=25,
                    pady=5
                ).pack(fill="x")

        # Emergency note
        tk.Label(
            content_frame,
            text="⚠️ For dental emergencies outside clinic hours, call our emergency hotline.",
            font=("Arial", 12, "bold"),
            bg="#FFEB3B",
            fg="black",
            pady=15,
            padx=20
        ).pack(side="bottom", pady=(0, 50))

        # Back button
        tk.Button(
            content_frame, text="BACK", bg="#EAB308", fg="black",
            font=("Arial", 14, "bold"), width=12, height=1, relief="flat",
            bd=0, highlightthickness=0, activebackground="#EAB308",
            command=self.show_main_menu, cursor="hand2"
        ).pack(side="bottom", pady=20)


# -------------------------
# Run the App
# -------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = DentalApp(root)
    root.mainloop()