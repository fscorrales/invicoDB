"""
Example script for testing the Custom Tkinter
Author: Tom Schimansky
License: 
Source: https://github.com/TomSchimansky/CustomTkinter
Custom Theme: https://github.com/avalon60/ctk_theme_builder
"""


import os
import customtkinter as ctk

from ..hangling_path import HanglingPath
from .main_window_ui import MainWindowUI
from .main_window_fct import MainWindowFct

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        main_window = MainWindowUI(
            self, padx_frame=10, pady_frame=10
        )
        MainWindowFct(main_window)

        # self.readonly_combo_list = ["Readonly combobox", "Item 1", "Item 2"]
        # self.readonly_combo = ctk.CTkOptionMenu(
        #     self, values=self.readonly_combo_list
        # )
        # self.readonly_combo.set("Readonly combobox")
        # self.readonly_combo.grid()

        #Last
        self.centerApp()

    def centerApp(self):
        self.update()
        self.minsize(self.winfo_width(), self.winfo_height())
        x_cordinate = int((self.winfo_screenwidth() / 2) - (self.winfo_width() / 2))
        y_cordinate = int((self.winfo_screenheight() / 2) - (self.winfo_height() / 2))
        self.geometry("+{}+{}".format(x_cordinate, y_cordinate-20))



if __name__ == "__main__":

    # app_path = HanglingPath().get_invicodb_path()
    # app_path = os.path.join(
    #     app_path, 'app'
    # )

    # Create a style
    ctk.set_appearance_mode("dark")  # Modes: system (default), light, dark
    ctk.set_default_color_theme("dark-blue")  # Themes: blue (default), dark-blue, green

    app = App()

    app.mainloop()

    # From invicoDB.src
    # python -m invicodb.app.app
