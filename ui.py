"""
ui.py – All Screens, Dialogs, and Reusable Widgets
Imports STATE from state.py; never imports main.py.
"""

import tkinter as tk
from tkinter import ttk, messagebox

from state import STATE
from models import Vehicle, Booking

# ─────────────────────────────────────────────
#  THEME
# ─────────────────────────────────────────────

C = {
    "bg":      "#F0F2FA",
    "card":    "#FFFFFF",
    "primary": "#5B5FEF",
    "accent":  "#F5841F",
    "text":    "#1A1D3B",
    "sub":     "#8589B0",
    "border":  "#E0E3F5",
    "nav_bg":  "#1E2140",
    "green":   "#27AE60",
    "red":     "#E74C3C",
}

FONT_TITLE  = ("Segoe UI", 20, "bold")
FONT_HEADER = ("Segoe UI", 14, "bold")
FONT_BODY   = ("Segoe UI", 11)
FONT_SMALL  = ("Segoe UI", 9)
FONT_BTN    = ("Segoe UI", 12, "bold")

# ─────────────────────────────────────────────
#  REUSABLE WIDGETS
# ─────────────────────────────────────────────

def make_card(parent, **kwargs):
    return tk.Frame(
        parent, bg=C["card"], relief="flat", bd=0,
        highlightbackground=C["border"], highlightthickness=1,
        **kwargs,
    )


def styled_btn(parent, text, command, color=None, fg="white", width=20):
    color = color or C["primary"]
    b = tk.Button(
        parent, text=text, command=command,
        bg=color, fg=fg,
        font=FONT_BTN, relief="flat", bd=0,
        activebackground=color, activeforeground=fg,
        cursor="hand2", width=width, pady=10,
    )
    b.bind("<Enter>", lambda e: b.config(bg=_darken(color)))
    b.bind("<Leave>", lambda e: b.config(bg=color))
    return b


def _darken(hex_color, amt=20):
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return "#{:02x}{:02x}{:02x}".format(max(r - amt, 0), max(g - amt, 0), max(b - amt, 0))


def entry_field(parent, placeholder="", show=""):
    frame = tk.Frame(
        parent, bg=C["card"],
        highlightbackground=C["border"], highlightthickness=1,
    )
    e = tk.Entry(
        frame, font=FONT_BODY, bd=0, relief="flat",
        bg=C["card"], fg=C["text"],
        insertbackground=C["primary"], show=show,
    )
    e.pack(fill="x", padx=10, pady=8)

    if placeholder and not show:
        e.insert(0, placeholder)
        e.config(fg=C["sub"])

        def on_focus_in(_):
            if e.get() == placeholder:
                e.delete(0, tk.END)
                e.config(fg=C["text"])

        def on_focus_out(_):
            if not e.get():
                e.insert(0, placeholder)
                e.config(fg=C["sub"])

        e.bind("<FocusIn>",  on_focus_in)
        e.bind("<FocusOut>", on_focus_out)

    return frame, e


# ─────────────────────────────────────────────
#  BASE SCREEN
# ─────────────────────────────────────────────

class Screen(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master, bg=C["bg"])
        self.app = app

    def show(self): self.place(relwidth=1, relheight=1)
    def hide(self): self.place_forget()


# ─────────────────────────────────────────────
#  SIGNUP SCREEN
# ─────────────────────────────────────────────

class SignupScreen(Screen):
    def __init__(self, master, app):
        super().__init__(master, app)
        self._build()

    def _build(self):
        top = tk.Frame(self, bg=C["bg"])
        top.pack(pady=(40, 10))
        tk.Label(top, text="🅿", font=("Segoe UI", 48),
                 fg=C["primary"], bg=C["bg"]).pack()
        tk.Label(top, text="Smart PARKING", font=("Segoe UI", 13, "bold"),
                 fg=C["primary"], bg=C["bg"]).pack()

        form = make_card(self)
        form.pack(padx=30, pady=10, fill="x")

        fields = [
            ("First name",        "", ""),
            ("Username",          "", ""),
            ("Email",             "", ""),
            ("Password",          "", "*"),
            ("Confirm Password",  "", "*"),
        ]
        self._entries = {}
        for lbl, ph, show in fields:
            tk.Label(form, text=lbl, font=FONT_SMALL, fg=C["sub"],
                     bg=C["card"], anchor="w").pack(fill="x", padx=14, pady=(8, 0))
            fr, e = entry_field(form, ph, show=show)
            fr.pack(fill="x", padx=10, pady=(0, 4))
            self._entries[lbl] = e

        self._terms = tk.BooleanVar()
        tk.Checkbutton(
            form, text="I agree with terms and conditions",
            variable=self._terms,
            bg=C["card"], fg=C["text"], font=FONT_BODY,
            activebackground=C["card"], selectcolor=C["primary"],
        ).pack(anchor="w", padx=14, pady=8)

        styled_btn(self, "Sign up", self._signup).pack(pady=8)

        lnk = tk.Label(self, text="Already have an account? Sign in",
                       fg=C["primary"], bg=C["bg"],
                       font=("Segoe UI", 10, "underline"), cursor="hand2")
        lnk.pack()
        lnk.bind("<Button-1>", lambda _: self.app.show("login"))

    def _signup(self):
        name  = self._entries["First name"].get().strip()
        uname = self._entries["Username"].get().strip()
        email = self._entries["Email"].get().strip()
        pw    = self._entries["Password"].get()
        cpw   = self._entries["Confirm Password"].get()

        if not all([name, uname, email, pw]):
            messagebox.showerror("Error", "Please fill all fields"); return
        if pw != cpw:
            messagebox.showerror("Error", "Passwords don't match"); return
        if not self._terms.get():
            messagebox.showerror("Error", "Accept terms first"); return
        if uname in STATE.users:
            messagebox.showerror("Error", "Username already taken"); return

        u = STATE.register_user(name, uname, email, pw)
        STATE.current_user = u
        self.app.show("welcome")


# ─────────────────────────────────────────────
#  LOGIN SCREEN
# ─────────────────────────────────────────────

class LoginScreen(Screen):
    def __init__(self, master, app):
        super().__init__(master, app)
        self._build()

    def _build(self):
        tk.Label(self, text="🅿", font=("Segoe UI", 48),
                 fg=C["primary"], bg=C["bg"]).pack(pady=(50, 5))
        tk.Label(self, text="Smart PARKING", font=("Segoe UI", 13, "bold"),
                 fg=C["primary"], bg=C["bg"]).pack()

        form = make_card(self)
        form.pack(padx=30, pady=20, fill="x")

        tk.Label(form, text="Username", font=FONT_SMALL, fg=C["sub"],
                 bg=C["card"], anchor="w").pack(fill="x", padx=14, pady=(10, 0))
        _, self._uname = entry_field(form)
        self._uname.master.pack(fill="x", padx=10, pady=4)

        tk.Label(form, text="Password", font=FONT_SMALL, fg=C["sub"],
                 bg=C["card"], anchor="w").pack(fill="x", padx=14, pady=(6, 0))
        _, self._pw = entry_field(form, show="*")
        self._pw.master.pack(fill="x", padx=10, pady=(0, 10))

        styled_btn(self, "Sign in", self._login).pack(pady=10)

        lnk = tk.Label(self, text="Don't have an account? Sign up",
                       fg=C["primary"], bg=C["bg"],
                       font=("Segoe UI", 10, "underline"), cursor="hand2")
        lnk.pack()
        lnk.bind("<Button-1>", lambda _: self.app.show("signup"))

        tk.Label(self, text="(demo: admin / admin)",
                 fg=C["sub"], bg=C["bg"], font=FONT_SMALL).pack(pady=4)

    def _login(self):
        uname = self._uname.get().strip()
        pw    = self._pw.get()

        # quick demo shortcut
        if uname == "admin" and pw == "admin":
            if "demo" not in STATE.users:
                STATE.register_user("Demo admin", "demo", "demo@example.com", "admin")
            STATE.current_user = STATE.users["demo"]
            self.app.show("welcome")
            return

        if uname not in STATE.users or not STATE.users[uname].login(pw):
            messagebox.showerror("Error", "Invalid credentials"); return

        STATE.current_user = STATE.users[uname]
        self.app.show("welcome")


# ─────────────────────────────────────────────
#  WELCOME SCREEN
# ─────────────────────────────────────────────

class WelcomeScreen(Screen):
    def __init__(self, master, app):
        super().__init__(master, app)
        self._build()

    def _build(self):
        self.config(bg="#2b2b2b")
        card = make_card(self)
        card.place(relx=0.5, rely=0.5, anchor="center", width=300, height=380)

        tk.Label(card, text="🚗", font=("Segoe UI", 60), bg=C["card"]).pack(pady=(20, 5))
        tk.Label(card, text="Welcome", font=FONT_TITLE,
                 fg=C["text"], bg=C["card"]).pack()
        tk.Label(
            card,
            text=(
                "Welcome to Smart Parking.\n"
                "Now in order to use all the\n"
                "functionality of the app add\n"
                "your cars and addresses on\n"
                "the home page."
            ),
            font=FONT_BODY, fg=C["sub"], bg=C["card"],
            justify="center", wraplength=240,
        ).pack(pady=15)
        styled_btn(card, "OK", lambda: self.app.show("main"),
                   color=C["accent"], width=18).pack(pady=10)


# ─────────────────────────────────────────────
#  MAIN SHELL  (nav + page container)
# ─────────────────────────────────────────────

class MainScreen(Screen):
    def __init__(self, master, app):
        super().__init__(master, app)
        self._build()

    def _build(self):
        # ── Top header ───────────────────────────────────────────
        self.header = tk.Frame(self, bg=C["primary"], height=60)
        self.header.pack(fill="x")
        self.header.pack_propagate(False)

        tk.Button(
            self.header, text="☰", font=("Segoe UI", 16),
            bg=C["primary"], fg="white", relief="flat",
            activebackground=C["primary"],
            command=self._toggle_menu,
        ).pack(side="left", padx=12, pady=10)

        self._title_lbl = tk.Label(
            self.header, text="Home",
            font=FONT_HEADER, fg="white", bg=C["primary"],
        )
        self._title_lbl.pack(side="left", padx=10)

        tk.Label(self.header, text="👤", font=("Segoe UI", 18),
                 fg="white", bg=C["primary"]).pack(side="right", padx=12)

        # ── Page container ───────────────────────────────────────
        self.page_area = tk.Frame(self, bg=C["bg"])
        self.page_area.pack(fill="both", expand=True)

        # ── Bottom nav ───────────────────────────────────────────
        self._build_bottom_nav()

        # ── Side menu (hidden initially) ─────────────────────────
        self._menu_open  = False
        self._side_menu  = self._build_side_menu()

        # ── Pages ────────────────────────────────────────────────
        self.pages = {
            "home":    HomePage(self.page_area, self.app),
            "cars":    CarsPage(self.page_area, self.app),
            "booking": BookingPage(self.page_area, self.app),
            "notifs":  NotificationsPage(self.page_area, self.app),
        }
        self.show_page("home")

    def _build_bottom_nav(self):
        nav = tk.Frame(self, bg=C["nav_bg"], height=60)
        nav.pack(fill="x", side="bottom")
        nav.pack_propagate(False)
        for icon, page in [("🏠", "home"), ("📋", "booking"),
                            ("💳", "cars"), ("🔔", "notifs")]:
            tk.Button(
                nav, text=icon, font=("Segoe UI", 20),
                bg=C["nav_bg"], fg="white", relief="flat",
                activebackground=C["nav_bg"], cursor="hand2",
                command=lambda p=page: self.show_page(p),
            ).pack(side="left", expand=True, fill="both")

    def _build_side_menu(self):
        menu = tk.Frame(self, bg=C["nav_bg"], width=220)
        tk.Label(menu, text="Smart PARKING", font=("Segoe UI", 12, "bold"),
                 fg=C["primary"], bg=C["nav_bg"]).pack(pady=20)

        for lbl, page in [
            ("🏠  Home",           "home"),
            ("🚗  My Cars",        "cars"),
            ("📋  Bookings",       "booking"),
            ("🔔  Notifications",  "notifs"),
        ]:
            tk.Button(
                menu, text=lbl, font=FONT_BODY,
                fg="white", bg=C["nav_bg"],
                relief="flat", activebackground="#2a2f5a",
                anchor="w", padx=20, pady=10,
                command=lambda p=page: [self._toggle_menu(), self.show_page(p)],
            ).pack(fill="x")

        tk.Button(
            menu, text="🚪  Logout", font=FONT_BODY,
            fg=C["red"], bg=C["nav_bg"],
            relief="flat", activebackground="#2a2f5a",
            anchor="w", padx=20, pady=10,
            command=lambda: [self._toggle_menu(), self.app.show("login")],
        ).pack(fill="x", side="bottom", pady=20)

        return menu

    def _toggle_menu(self):
        if self._menu_open:
            self._side_menu.place_forget()
        else:
            self._side_menu.place(x=0, y=60, relheight=1, width=220)
            self._side_menu.lift()
        self._menu_open = not self._menu_open

    def show_page(self, name: str):
        titles = {
            "home":    "Home",
            "cars":    "Cars",
            "booking": "Bookings",
            "notifs":  "Notifications",
        }
        self._title_lbl.config(text=titles.get(name, ""))
        if self._menu_open:
            self._toggle_menu()
        for p in self.pages.values():
            p.place_forget()
        page = self.pages[name]
        page.place(relwidth=1, relheight=1)
        if hasattr(page, "refresh"):
            page.refresh()


# ─────────────────────────────────────────────
#  HOME PAGE
# ─────────────────────────────────────────────

class HomePage(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master, bg=C["bg"])
        self.app = app
        self._build()

    def _build(self):
        top = tk.Frame(self, bg=C["primary"], height=100)
        top.pack(fill="x")
        top.pack_propagate(False)
        user_name = STATE.current_user.name if STATE.current_user else "User"
        tk.Label(top, text=f"Hello, {user_name} 👋",
                 font=FONT_HEADER, fg="white", bg=C["primary"]).pack(anchor="w", padx=20, pady=(20, 0))
        tk.Label(top, text="Find your perfect parking spot",
                 font=FONT_SMALL, fg="#BDC3E8", bg=C["primary"]).pack(anchor="w", padx=20)

        tk.Label(self, text="Available Parking Lots",
                 font=FONT_HEADER, fg=C["text"], bg=C["bg"]).pack(anchor="w", padx=20, pady=(15, 5))

        scroll = tk.Frame(self, bg=C["bg"])
        scroll.pack(fill="both", expand=True, padx=15)

        for lot in STATE.parking_lots:
            avail = len(lot.getAvailableSpots())
            card  = make_card(scroll)
            card.pack(fill="x", pady=6)
            row = tk.Frame(card, bg=C["card"])
            row.pack(fill="x", padx=15, pady=12)

            tk.Label(row, text="🅿", font=("Segoe UI", 28),
                     fg=C["primary"], bg=C["card"]).pack(side="left")

            info = tk.Frame(row, bg=C["card"])
            info.pack(side="left", padx=12, fill="x", expand=True)
            tk.Label(info, text=lot.name, font=FONT_HEADER,
                     fg=C["text"], bg=C["card"], anchor="w").pack(fill="x")
            tk.Label(info, text=lot.address, font=FONT_SMALL,
                     fg=C["sub"], bg=C["card"], anchor="w").pack(fill="x")

            right = tk.Frame(row, bg=C["card"])
            right.pack(side="right")
            clr = C["green"] if avail > 5 else C["accent"] if avail > 0 else C["red"]
            tk.Label(right, text=f"{avail} free",
                     font=("Segoe UI", 10, "bold"), fg=clr, bg=C["card"]).pack()
            tk.Button(
                right, text="Book →",
                font=("Segoe UI", 9, "bold"), fg="white", bg=C["primary"],
                relief="flat", padx=8, pady=4, cursor="hand2",
                command=lambda l=lot: self._open_booking(l),
            ).pack(pady=4)

    def refresh(self):
        pass  # simple; could rebuild cards on demand

    def _open_booking(self, lot):
        dlg = BookingDialog(self.winfo_toplevel(), lot)
        self.wait_window(dlg)


# ─────────────────────────────────────────────
#  BOOKING DIALOG
# ─────────────────────────────────────────────

class BookingDialog(tk.Toplevel):
    def __init__(self, master, lot):
        super().__init__(master)
        self.lot = lot
        self.title("Book Parking")
        self.geometry("400x560")
        self.resizable(False, False)
        self.config(bg=C["bg"])
        self.grab_set()
        self._selected_hours    = tk.IntVar(value=3)
        self._selected_services = {
            "electric_charge": tk.BooleanVar(),
            "car_wash":        tk.BooleanVar(),
        }
        self._build()

    def _build(self):
        # Header
        hdr = tk.Frame(self, bg=C["primary"])
        hdr.pack(fill="x")
        tk.Label(hdr, text=f"Parking area – {self.lot.name}",
                 font=FONT_HEADER, fg="white", bg=C["primary"]).pack(side="left", padx=15, pady=12)
        tk.Button(hdr, text="✕", fg="white", bg=C["primary"],
                  font=("Segoe UI", 14), relief="flat",
                  command=self.destroy).pack(side="right", padx=12)

        avail = len(self.lot.getAvailableSpots())
        tk.Label(self, text=f"📍 {self.lot.address}   |   {avail} Spots Available",
                 font=FONT_SMALL, fg=C["sub"], bg=C["bg"]).pack(pady=6)

        # Date (static demo)
        df = make_card(self)
        df.pack(padx=20, fill="x", pady=4)
        tk.Label(df, text="📅  22 April, Monday       🕐  1:30 am",
                 font=FONT_BODY, fg=C["primary"], bg=C["card"]).pack(padx=15, pady=10)

        # Plan
        tk.Label(self, text="Plan", font=FONT_HEADER,
                 fg=C["text"], bg=C["bg"]).pack(anchor="w", padx=20, pady=(10, 4))
        plans_f = tk.Frame(self, bg=C["bg"])
        plans_f.pack(padx=20, fill="x")
        for h, price in [(1, 20), (2, 35), (3, 60), (4, 80)]:
            f = tk.Frame(plans_f, bg=C["bg"])
            f.pack(side="left", expand=True, padx=3)
            tk.Radiobutton(
                f, text=f"{h}hr\n{price} SAR",
                variable=self._selected_hours, value=h,
                indicatoron=False, selectcolor=C["primary"],
                bg=C["card"], fg=C["text"],
                activebackground=C["primary"], activeforeground="white",
                font=("Segoe UI", 9, "bold"),
                relief="solid", bd=1, padx=8, pady=6,
                command=self._update_total,
            ).pack(fill="x")

        # Services
        tk.Label(self, text="Services", font=FONT_HEADER,
                 fg=C["text"], bg=C["bg"]).pack(anchor="w", padx=20, pady=(12, 4))
        svc_f = tk.Frame(self, bg=C["bg"])
        svc_f.pack(padx=20, fill="x")
        for key, icon, lbl, price in [
            ("electric_charge", "⚡", "Electric charge", "40 SAR"),
            ("car_wash",        "🚿", "Car wash",        "30 SAR"),
        ]:
            tk.Checkbutton(
                svc_f, text=f"{icon} {lbl}: {price}",
                variable=self._selected_services[key],
                bg=C["bg"], fg=C["text"], font=FONT_BODY,
                activebackground=C["bg"], selectcolor=C["primary"],
                command=self._update_total,
            ).pack(anchor="w", pady=3)

        # Total
        self._total_lbl = tk.Label(self, text="Total: 60 SAR",
                                   font=FONT_TITLE, fg=C["accent"], bg=C["bg"])
        self._total_lbl.pack(pady=10)
        styled_btn(self, "Reserve Now", self._reserve, color=C["accent"]).pack(pady=6)
        self._update_total()

    def _update_total(self):
        from models import Payment
        hours = self._selected_hours.get()
        svcs  = [k for k, v in self._selected_services.items() if v.get()]
        total = Payment(0, hours, extra_services=svcs).calculateFee(hours, svcs)
        self._total_lbl.config(text=f"Total: {total} SAR  |  {hours}hr")

    def _reserve(self):
        if not STATE.current_user:
            messagebox.showerror("Error", "Please login first"); return

        hours  = self._selected_hours.get()
        svcs   = [k for k, v in self._selected_services.items() if v.get()]
        result = STATE.make_booking(self.lot, hours, svcs)

        if result is None:
            messagebox.showerror("Full", "No spots available"); return

        booking, payment = result
        messagebox.showinfo(
            "Success ✅",
            f"Booking confirmed!\n{booking}\n{payment.getReceipt()}",
        )
        self.destroy()


# ─────────────────────────────────────────────
#  CARS PAGE
# ─────────────────────────────────────────────

class CarsPage(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master, bg=C["bg"])
        self.app = app
        self._build()

    def _build(self):
        hdr = tk.Frame(self, bg=C["bg"])
        hdr.pack(fill="x", padx=20, pady=(15, 5))
        tk.Label(hdr, text="My Cars", font=FONT_TITLE,
                 fg=C["text"], bg=C["bg"]).pack(side="left")
        tk.Button(
            hdr, text="+ Add new car",
            font=("Segoe UI", 10, "bold"),
            fg=C["primary"], bg=C["bg"],
            relief="flat", cursor="hand2",
            command=self._add_car,
        ).pack(side="right")

        self.list_frame = tk.Frame(self, bg=C["bg"])
        self.list_frame.pack(fill="both", expand=True, padx=15)
        self.refresh()

    def refresh(self):
        for w in self.list_frame.winfo_children():
            w.destroy()
        my_cars = STATE.my_vehicles()
        if not my_cars:
            tk.Label(self.list_frame, text="No cars yet. Add one!",
                     font=FONT_BODY, fg=C["sub"], bg=C["bg"]).pack(pady=40)
            return
        icons = {"sedan": "🚗", "suv": "🚙", "truck": "🚛", "ev": "⚡"}
        for v in my_cars:
            card = make_card(self.list_frame)
            card.pack(fill="x", pady=5)
            row = tk.Frame(card, bg=C["card"])
            row.pack(fill="x", padx=12, pady=10)
            tk.Label(row, text=icons.get(v.vehicle_type, "🚗"),
                     font=("Segoe UI", 28), bg=C["primary"],
                     fg="white", padx=6, pady=4).pack(side="left")
            info = tk.Frame(row, bg=C["card"])
            info.pack(side="left", padx=12)
            tk.Label(info, text=v.model, font=FONT_HEADER,
                     fg=C["text"], bg=C["card"], anchor="w").pack(fill="x")
            tk.Label(info, text=v.licensePlate, font=FONT_SMALL,
                     fg=C["sub"], bg=C["card"], anchor="w").pack(fill="x")
            tk.Button(
                row, text="🗑", font=("Segoe UI", 14),
                fg=C["red"], bg=C["card"],
                relief="flat", cursor="hand2",
                command=lambda vid=v.vehicleID: self._delete_car(vid),
            ).pack(side="right", padx=8)

    def _add_car(self):
        dlg = AddCarDialog(self.winfo_toplevel())
        self.wait_window(dlg)
        self.refresh()

    def _delete_car(self, vid: int):
        if messagebox.askyesno("Delete", "Remove this car?"):
            STATE.remove_vehicle(vid)
            self.refresh()


class AddCarDialog(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Add Car")
        self.geometry("340x380")
        self.resizable(False, False)
        self.config(bg=C["bg"])
        self.grab_set()
        self._build()

    def _build(self):
        tk.Label(self, text="Add New Car", font=FONT_TITLE,
                 fg=C["text"], bg=C["bg"]).pack(pady=15)
        form = make_card(self)
        form.pack(padx=20, fill="x")

        self._entries = {}
        for lbl, ph in [("Model / Name", "e.g. Mercedes G 63"),
                         ("License Plate", "e.g. A 61026")]:
            tk.Label(form, text=lbl, font=FONT_SMALL, fg=C["sub"],
                     bg=C["card"], anchor="w").pack(fill="x", padx=14, pady=(8, 0))
            fr, e = entry_field(form, ph)
            fr.pack(fill="x", padx=10, pady=(0, 4))
            self._entries[lbl] = e

        tk.Label(form, text="Type", font=FONT_SMALL, fg=C["sub"],
                 bg=C["card"], anchor="w").pack(fill="x", padx=14, pady=(6, 0))
        self._type = ttk.Combobox(form, values=["sedan", "suv", "truck", "ev"],
                                  state="readonly", font=FONT_BODY)
        self._type.set("sedan")
        self._type.pack(fill="x", padx=10, pady=(0, 10))

        styled_btn(self, "Add Car", self._save).pack(pady=12)

    def _save(self):
        model = self._entries["Model / Name"].get().strip()
        plate = self._entries["License Plate"].get().strip()
        if not model or not plate:
            messagebox.showerror("Error", "Fill all fields"); return
        STATE.add_vehicle(plate, self._type.get(), model)
        self.destroy()


# ─────────────────────────────────────────────
#  BOOKINGS PAGE
# ─────────────────────────────────────────────

class BookingPage(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master, bg=C["bg"])
        self.app = app
        self._build()

    def _build(self):
        tk.Label(self, text="My Bookings", font=FONT_TITLE,
                 fg=C["text"], bg=C["bg"]).pack(pady=15, anchor="w", padx=20)
        self.list_frame = tk.Frame(self, bg=C["bg"])
        self.list_frame.pack(fill="both", expand=True, padx=15)
        self.refresh()

    def refresh(self):
        for w in self.list_frame.winfo_children():
            w.destroy()
        my_b = STATE.my_bookings()
        if not my_b:
            tk.Label(self.list_frame, text="No bookings yet.",
                     font=FONT_BODY, fg=C["sub"], bg=C["bg"]).pack(pady=40)
            return
        for b in reversed(my_b):
            p    = STATE.payment_for(b.bookingID)
            card = make_card(self.list_frame)
            card.pack(fill="x", pady=5)
            inner = tk.Frame(card, bg=C["card"])
            inner.pack(fill="x", padx=15, pady=12)

            clr = C["green"] if b.status == "active" else \
                  C["red"]   if b.status == "cancelled" else C["sub"]
            tk.Label(inner, text=f"Booking #{b.bookingID}",
                     font=FONT_HEADER, fg=C["text"], bg=C["card"]).pack(anchor="w")
            tk.Label(inner, text=f"Spot {b.spotID}  |  {b.getDuration()} hrs",
                     font=FONT_SMALL, fg=C["sub"], bg=C["card"]).pack(anchor="w")
            tk.Label(inner, text=f"Status: {b.status.upper()}",
                     font=("Segoe UI", 10, "bold"), fg=clr, bg=C["card"]).pack(anchor="w")
            if p:
                tk.Label(inner, text=f"Paid: {p.amount} SAR  ({p.method})",
                         font=FONT_SMALL, fg=C["sub"], bg=C["card"]).pack(anchor="w")
            if b.status == "active":
                tk.Button(
                    inner, text="Cancel Booking",
                    font=("Segoe UI", 9), fg="white", bg=C["red"],
                    relief="flat", padx=8, pady=4, cursor="hand2",
                    command=lambda bk=b: self._cancel(bk),
                ).pack(anchor="w", pady=4)

    def _cancel(self, booking: Booking):
        if messagebox.askyesno("Cancel", "Cancel this booking?"):
            STATE.cancel_booking(booking)
            self.refresh()


# ─────────────────────────────────────────────
#  NOTIFICATIONS PAGE
# ─────────────────────────────────────────────

class NotificationsPage(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master, bg=C["bg"])
        self.app = app
        self._build()

    def _build(self):
        tk.Label(self, text="Notifications", font=FONT_TITLE,
                 fg=C["text"], bg=C["bg"]).pack(pady=15, anchor="w", padx=20)
        self.list_frame = tk.Frame(self, bg=C["bg"])
        self.list_frame.pack(fill="both", expand=True, padx=15)
        self.refresh()

    def refresh(self):
        for w in self.list_frame.winfo_children():
            w.destroy()
        my_n = STATE.my_notifications()
        if not my_n:
            tk.Label(self.list_frame, text="No notifications.",
                     font=FONT_BODY, fg=C["sub"], bg=C["bg"]).pack(pady=40)
            return
        icons = {"booking": "📌", "cancel": "❌", "info": "ℹ️", "alert": "⚠️"}
        for n in reversed(my_n):
            card = make_card(self.list_frame)
            card.pack(fill="x", pady=4)
            row = tk.Frame(card, bg=C["card"])
            row.pack(fill="x", padx=14, pady=10)
            tk.Label(row, text=icons.get(n.type, "🔔"),
                     font=("Segoe UI", 20), bg=C["card"]).pack(side="left")
            tk.Label(row, text=n.message,
                     font=FONT_BODY, fg=C["text"], bg=C["card"],
                     wraplength=280, justify="left").pack(side="left", padx=10)
