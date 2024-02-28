import datetime as dt
import os
from dataclasses import dataclass

import customtkinter as ctk

from ..download.download_db import *
from ..hangling_path import HanglingPath
from .default_widgets_setup import *
from .main_window_ui import MainWindowUI


@dataclass
class MainWindowFct():
    mw: MainWindowUI

    def __post_init__(self):
        # self.output_path = HanglingPath().get_update_path_input()
        # self.credentials_path = HanglingPath().get_invicodb_path()
        # self.credentials_path = os.path.join(
        #     self.credentials_path, 'download'
        # )
        self.configureOptionalProcessType()
        self.configureButtonBeginProcess()

    def configureOptionalProcessType(self):
        self.mw.optional_process_type.configure(
            command = self.processTypeCallback
        )

    def processTypeCallback(self, choice):
        if choice == "Personalizado":
            self.mw.unselectAllCheakBoxes()
        elif choice == "Control Icaro":
            self.unselectAllCheakBoxes()
            self.mw.frame_sist_propios.var_icaro.set(1)
            self.mw.frame_siif.var_rf602.set(1)
            self.mw.frame_siif.var_gto_rpa03g.set(1)
            self.mw.frame_siif.var_rcg01_uejp.set(1)
            self.mw.frame_siif.var_rfondo07tp.set(1)
            self.mw.frame_sscc.var_ctas_ctes.set(1)
            self.mw.frame_gastos.var_ctrl_icaro.set(1)
        elif choice == "Completo":
            self.unselectAllCheakBoxes()
            self.mw.frame_siif.var_switch_all.set(1)
            self.mw.frame_siif.switch_all()
            self.mw.frame_sgf.var_switch_all.set(1)
            self.mw.frame_sgf.switch_all()
            self.mw.frame_sscc.var_switch_all.set(1)
            self.mw.frame_sscc.switch_all()
            self.mw.frame_recuperos.var_switch_all.set(1)
            self.mw.frame_recuperos.switch_all()
            self.mw.frame_sist_propios.var_switch_all.set(1)
            self.mw.frame_sist_propios.switch_all()
            self.mw.frame_recursos.var_switch_all.set(1)
            self.mw.frame_recursos.switch_all()
            self.mw.frame_gastos.var_switch_all.set(1)
            self.mw.frame_gastos.switch_all()
        elif choice == "Completo Sin Recuperos":
            self.processTypeCallback("Completo")
            self.mw.frame_recuperos.var_switch_all.set(0)
            self.mw.frame_recuperos.switch_all()

    def unselectAllCheakBoxes(self):
        self.mw.frame_siif.var_switch_all.set(0)
        self.mw.frame_siif.switch_all()
        self.mw.frame_sgf.var_switch_all.set(0)
        self.mw.frame_sgf.switch_all()
        self.mw.frame_sscc.var_switch_all.set(0)
        self.mw.frame_sscc.switch_all()
        self.mw.frame_recuperos.var_switch_all.set(0)
        self.mw.frame_recuperos.switch_all()
        self.mw.frame_sist_propios.var_switch_all.set(0)
        self.mw.frame_sist_propios.switch_all()
        self.mw.frame_recursos.var_switch_all.set(0)
        self.mw.frame_recursos.switch_all()
        self.mw.frame_gastos.var_switch_all.set(0)
        self.mw.frame_gastos.switch_all()

    def configureButtonBeginProcess(self):
        self.mw.button_start.configure(
            command = self.beginProcess
        )

    def beginProcess(self):
        if self.mw.var_download.get() == 1:
            self.processDownload()

        if self.mw.var_update.get() == 1:
            print("Update")

        if self.mw.var_upload.get() == 1:
            print("Upload")
    
    def processDownload(self):
        # print("Download")
        siif_list = self.mw.frame_siif.get_variable()
        print(siif_list)
        if len(siif_list) > 0:
            pass

        #     siif_credentials_path = os.path.join(
        #         self.credentials_path, 'siif_credentials.json'
        #     )
        #     siif = DownloadSIIF(
        #         path_credentials_file=siif_credentials_path,
        #         output_path=os.path.join(self.output_path, 'Reportes SIIF')
        #     )
        #     print("Download")