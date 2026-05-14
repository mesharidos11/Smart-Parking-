"""
Project structure:
    main.py    ← app class
    models.py  ← classes
    state.py   ← AppState singleton (STATE)
    ui.py      ← all screens and widgets
"""

import tkinter as tk
from ui import (
    SignupScreen,
    LoginScreen,
    WelcomeScreen,
    MainScreen,
    C,
)


class App:

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Smart Parking")
        self.root.geometry("390x780")
        self.root.resizable(False, True)
        self.root.config(bg=C["bg"])

        self._screens: dict[str, tk.Frame] = {}
        self._current: tk.Frame | None = None

        self._screens["signup"]  = SignupScreen(self.root, self)
        self._screens["login"]   = LoginScreen(self.root, self)
        self._screens["welcome"] = WelcomeScreen(self.root, self)
        self._screens["main"]    = MainScreen(self.root, self)

        self.show("login")


    def show(self, name: str):
        if self._current:
            self._current.hide()
        screen = self._screens[name]
        screen.show()
        self._current = screen

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    App().run()
