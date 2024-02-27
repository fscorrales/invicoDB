from dataclasses import dataclass

import customtkinter as ctk
import datetime as dt

from .default_widgets_setup import *
from .main_window_ui import MainWindowUI


@dataclass
class MainWindowFct():
    main_window: MainWindowUI

    def __post_init__(self):
        self.pressProcess()

    def pressProcess(self):
        print("Process")

    # def processTypeCallback(self, choice):
    #     if choice == "Completo":
    #         self.frame_siif.var_switch_all.set(1)
    #         self.frame_siif.switch_all()
        # print("optionmenu dropdown clicked:", choice)