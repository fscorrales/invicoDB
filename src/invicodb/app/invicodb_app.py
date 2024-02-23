"""
Example script for testing the Azure ttk theme
Author: rdbende
License: MIT license
Source: https://github.com/rdbende/ttk-widget-factory
"""


import os
import tkinter as tk
from tkinter import ttk

from ..hangling_path import HanglingPath
from .widget_setup import WidgetSetup


class App(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self)

        # Make the app responsive
        for index in [0, 1, 2, 4, 5]:
            self.columnconfigure(index=index, weight=1)
            self.rowconfigure(index=index, weight=1)

        # Create value lists
        # self.option_menu_list = ["", "OptionMenu", "Option 1", "Option 2"]
        # self.combo_list = ["Combobox", "Editable item 1", "Editable item 2"]
        self.readonly_combo_list = ["Readonly combobox", "Item 1", "Item 2"]

        # Create control variables
        self.var_0 = tk.BooleanVar()
        self.var_1 = tk.BooleanVar(value=True)
        self.var_2 = tk.BooleanVar()
        self.var_3 = tk.IntVar(value=2)
        # self.var_4 = tk.StringVar(value=self.option_menu_list[1])
        self.var_5 = tk.DoubleVar(value=75.0)

        # Create widgets :
        #padx_frame=(20, 10), pady_frame=(20, 10), padding_frame=(20, 10)
        ws = WidgetSetup(
            self, padx_frame=10, pady_frame=10, padding_frame=5, 
            padx_checkbox=5, pady_checkbox=5
        )
        ws.setupSIIFWidgets(row_frame=0, column_frame=0, rowspan_frame=5)
        ws.setupSGFWidgets(row_frame=0, column_frame=1)
        self.separator = ttk.Separator(self)
        self.separator.grid(row=1, column=1, padx=(20, 10), pady=10, sticky="ew")
        ws.setupSSCCWidgets(row_frame=2, column_frame=1)
        ws.setupSistemaRecuperosWidgets(row_frame=0, column_frame=2, rowspan_frame=3)
        self.separator = ttk.Separator(self)
        self.separator.grid(row=3, column=1, padx=(20, 10), pady=10, sticky="ew", columnspan=2)
        ws.setupSistemasPropiosWidgets(row_frame=4, column_frame=1, columnspan_frame=2)
        self.setup_widgets()
    #     self.myButton = ttk.Button(self, text="Show", command=self.show).grid(row=4, column=2)

    # def show(self):
    #     self.myLabel = ttk.Label(self, text=self.var_rf610.get()).grid(row=5, column=2)


    def setup_widgets(self):
        pass
        # # Create a Frame for input widgets
        # self.widgets_frame = ttk.Frame(self, padding=(0, 0, 0, 10))
        # self.widgets_frame.grid(
        #     row=1, column=1, padx=10, pady=(30, 10), sticky="nsew", rowspan=3
        # )
        # self.widgets_frame.columnconfigure(index=0, weight=1)

        # # Read-only combobox
        # self.readonly_combo = ttk.Combobox(
        #     self.widgets_frame, state="readonly", values=self.readonly_combo_list
        # )
        # self.readonly_combo.current(0)
        # self.readonly_combo.grid(row=3, column=0, padx=5, pady=10, sticky="ew")

        # # Togglebutton
        # self.togglebutton = ttk.Checkbutton(
        #     self.widgets_frame, text="Toggle button", style="Toggle.TButton"
        # )
        # self.togglebutton.grid(row=8, column=0, padx=5, pady=10, sticky="nsew")

        # # Switch
        # self.switch = ttk.Checkbutton(
        #     self.widgets_frame, text="Switch", style="Switch.TCheckbutton"
        # )
        # self.switch.grid(row=9, column=0, padx=5, pady=10, sticky="nsew")

        # # Sizegrip
        # self.sizegrip = ttk.Sizegrip(self)
        # self.sizegrip.grid(row=100, column=100, padx=(0, 5), pady=(0, 5))


if __name__ == "__main__":
    root = tk.Tk()
    root.title("")

    app_path = HanglingPath().get_invicodb_path()
    app_path = os.path.join(
        app_path, 'app'
    )

    # Simply set the theme
    # root.tk.call("source", os.path.join(app_path, 'azure.tcl'))
    # root.tk.call("set_theme", "light")

    # Create a style
    style = ttk.Style(root)
    # Import the tcl file
    root.tk.call('source', os.path.join(app_path, 'forest-light.tcl'))
    # Set the theme with the theme_use method
    print(app_path)
    style.theme_use('forest-light')

    app = App(root)
    app.pack(fill="both", expand=True)

    # Set a minsize for the window, and place it in the middle
    root.update()
    root.minsize(root.winfo_width(), root.winfo_height())
    x_cordinate = int((root.winfo_screenwidth() / 2) - (root.winfo_width() / 2))
    y_cordinate = int((root.winfo_screenheight() / 2) - (root.winfo_height() / 2))
    root.geometry("+{}+{}".format(x_cordinate, y_cordinate-20))

    root.mainloop()

    # From invicoDB.src
    # python -m invicodb.app.invicodb_app
