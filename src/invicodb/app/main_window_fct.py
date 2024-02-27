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
