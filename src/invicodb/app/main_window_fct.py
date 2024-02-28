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
        self.configureProcessOptionMenu()
        self.configureButtonBeginProcess()

    def configureProcessOptionMenu(self):
        self.mw.optional_process_type.configure(
            command = self.processTypeCallback
        )
        self.mw.option_desde.configure(
            command = self.processDesdeCallback
        )
        self.mw.option_hasta.configure(
            command = self.processHastaCallback
        )

    def processDesdeCallback(self, choice):
        int_desde = int(choice)
        int_hasta = int(self.mw.option_hasta.get())
        if int_desde > int_hasta:
            self.mw.option_hasta.set(choice)

    def processHastaCallback(self, choice):
        int_desde = int(self.mw.option_desde.get())
        int_hasta = int(choice)
        if int_desde > int_hasta:
            self.mw.option_desde.set(choice)

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
            self.mw.frame_siif.switchAll()
            self.mw.frame_sgf.var_switch_all.set(1)
            self.mw.frame_sgf.switchAll()
            self.mw.frame_sscc.var_switch_all.set(1)
            self.mw.frame_sscc.switchAll()
            self.mw.frame_recuperos.var_switch_all.set(1)
            self.mw.frame_recuperos.switchAll()
            self.mw.frame_sist_propios.var_switch_all.set(1)
            self.mw.frame_sist_propios.switchAll()
            self.mw.frame_recursos.var_switch_all.set(1)
            self.mw.frame_recursos.switchAll()
            self.mw.frame_gastos.var_switch_all.set(1)
            self.mw.frame_gastos.switchAll()
        elif choice == "Completo Sin Recuperos":
            self.processTypeCallback("Completo")
            self.mw.frame_recuperos.var_switch_all.set(0)
            self.mw.frame_recuperos.switchAll()

    def unselectAllCheakBoxes(self):
        self.mw.frame_siif.var_switch_all.set(0)
        self.mw.frame_siif.switchAll()
        self.mw.frame_sgf.var_switch_all.set(0)
        self.mw.frame_sgf.switchAll()
        self.mw.frame_sscc.var_switch_all.set(0)
        self.mw.frame_sscc.switchAll()
        self.mw.frame_recuperos.var_switch_all.set(0)
        self.mw.frame_recuperos.switchAll()
        self.mw.frame_sist_propios.var_switch_all.set(0)
        self.mw.frame_sist_propios.switchAll()
        self.mw.frame_recursos.var_switch_all.set(0)
        self.mw.frame_recursos.switchAll()
        self.mw.frame_gastos.var_switch_all.set(0)
        self.mw.frame_gastos.switchAll()

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
        ejercicio_desde = int(self.mw.option_desde.get())
        ejercicio_hasta = int(self.mw.option_hasta.get())
        ejercicios = list(map(str, range(ejercicio_desde, ejercicio_hasta + 1)))
        # Generamos output path y credentials path
        output_path = HanglingPath().get_update_path_input()
        credentials_path = HanglingPath().get_invicodb_path()
        credentials_path = os.path.join(
            credentials_path, 'download'
        )
        # Verificamos si existen reportes SIIF para descargar
        siif_list = self.mw.frame_siif.getText()
        if len(siif_list) > 0:
            # Cargamos credenciales e instanciamos SIIF
            # siif_credentials_path = os.path.join(
            #     credentials_path, 'siif_credentials.json'
            # )
            # siif = DownloadSIIF(
            #     path_credentials_file = siif_credentials_path,
            #     output_path = os.path.join(output_path, 'Reportes SIIF'),
            # )
            # Mantenemos abierta la conexión hasta descargar todos los reportes que necesitamos
            # siif.download_all = True

            if self.mw.frame_siif.var_rf610.get() == 1:
                # siif.download_ppto_gtos_desc_rf610(ejercicios)
                pass
            # if self.mw.frame_siif.var_rf602.get() == 1:
            #     siif.download_rf602()
            # if self.mw.frame_siif.var_gto_rpa03g.get() == 1:
            #     siif.download_gto_rpa03g()
            # if self.mw.frame_siif.var_rcg01_uejp.get() == 1:
            #     siif.download_rcg01_uejp()
            # if self.mw.frame_siif.var_rfondo07tp.get() == 1:
            #     siif.download_rfondo07tp()


            # self.download_mayor_contable_rcocc31(
            #     ejercicios, 
            #     ctas_contables = [
            #         '1112-2-6', '1141-1-4', '2111-1-1', '2111-1-2',
            #         '2113-2-9', '2121-1-1', '2122-1-2',
            #     ]
            # )
            # mes_actual = dt.datetime.strftime(dt.datetime.now(), '%Y-%m')
            # mes_anterior = int(mes_actual[-2:]) - 1
            # if mes_anterior == 0:
            #     mes_anterior = 12
            #     mes_anterior = str(int(mes_actual[:4]) - 1) + '-' + str(mes_anterior).zfill(2)
            # else:    
            #     mes_anterior = mes_actual[:-2] + str(mes_anterior).zfill(2) 
            # meses = [mes_anterior, mes_actual]
            # self.download_deuda_flotante_rdeu012(meses)

            
            # siif.quit() #Revisar el remove HTML
        
        # Verificamos si existen reportes SGF para descargar
        sgf_list = self.mw.frame_sgf.getText()
        if len(sgf_list) > 0:
            # Cargamos credenciales e instanciamos SGF
            # invico_credentials_path = os.path.join(
            #     credentials_path, 'invico_credentials.json'
            # )
            # sgf = DownloadSGF(
            #     path_credentials_file=invico_credentials_path,
            #     output_path=os.path.join(output_path, 'Sistema Gestion Financiera')
            # )
            # Mantenemos abierta la conexión hasta descargar todos los reportes que necesitamos
            # sgf.download_all = True
            # sgf.quit()
            pass
        
        # Verificamos si existen reportes SSCC para descargar
        sscc_list = self.mw.frame_sscc.getText()
        if len(sscc_list) > 0:
            # Cargamos credenciales e instanciamos SSCC
            # invico_credentials_path = os.path.join(
            #     credentials_path, 'invico_credentials.json'
            # )
            # sscc = DownloadSSCC(
            #     path_credentials_file=invico_credentials_path,
            #     output_path=os.path.join(output_path, 'Sistema de Seguimiento de Cuentas Corrientes')
            # )
            # Mantenemos abierta la conexión hasta descargar todos los reportes que necesitamos
            # sscc.download_all = True
            # sscc.quit()
            pass

        # Verificamos si existen reportes del Sist Recuperos para descargar
        recuperos_list = self.mw.frame_recuperos.getText()
        if len(recuperos_list) > 0:
            # Cargamos credenciales e instanciamos Sist Recuperos
            # recuperos_credentials_path = os.path.join(
            #     credentials_path, 'sgv_credentials.json'
            # )
            # recuperos = DownloadSGV(
            #     path_credentials_file = recuperos_credentials_path,
            #     output_path = os.path.join(output_path, 'Gestión Vivienda GV')
            # )
            # Mantenemos abierta la conexión hasta descargar todos los reportes que necesitamos
            # recuperos.download_all = True
            # recuperos.quit()
            pass

        # Verificamos si existen reportes del Sist Propios para descargar
        sist_propios_list = self.mw.frame_sist_propios.getText()
        if len(sist_propios_list) > 0:
            if self.mw.frame_sist_propios.var_icaro.get() == 1:
                # my_path = HanglingPath().get_outside_path()
                # exequiel_path = HanglingPath().get_r_icaro_path()
                # CopyIcaro(
                #     exequiel_path = os.path.join(exequiel_path, 'ICARO.sqlite'),
                #     my_path = os.path.join(my_path, 'R Output/SQLite Files/ICARO.sqlite')
                # )
                pass
            if self.mw.frame_sist_propios.var_slave.get() == 1:
                # exequiel_path = HanglingPath().get_slave_path()
                # CopySlave(
                #     exequiel_path = os.path.join(exequiel_path, 'Slave.mdb'),
                #     my_path = os.path.join(output_path, 'Slave/Slave.mdb')
                # )
                pass
            pass