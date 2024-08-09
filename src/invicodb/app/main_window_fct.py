import datetime as dt
import os
from dataclasses import dataclass

import customtkinter as ctk

from ..download.download_db import *
from ..hangling_path import HanglingPath
from ..update.update_db import *
from ..upload.upload_db import UploadGoogleSheet
from .default_widgets_setup import *
from .main_window_ui import MainWindowUI


@dataclass
class MainWindowFct():
    mw: MainWindowUI

    def __post_init__(self):
        self.disableDownloadCheckBoxes()
        self.configureProcessOptionMenu()
        self.configureButtonBeginProcess()

    def disableDownloadCheckBoxes(self):
        self.mw.frame_recuperos.var_resumen_facturado.set(0)
        self.mw.frame_recuperos.var_resumen_recaudado.set(0)

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
        elif choice == "Ejecución y Control Recursos":
            self.unselectAllCheakBoxes()
            self.mw.frame_siif.var_rci02.set(1)
            self.mw.frame_siif.var_ri102.set(1)
            self.mw.frame_sscc.var_ctas_ctes.set(1)
            self.mw.frame_sscc.var_banco_invico.set(1)
            self.mw.frame_recursos.var_ejec_recursos.set(1)
            self.mw.frame_recursos.var_comprobantes_recursos.set(1)
            self.mw.frame_recursos.var_ctrl_recursos.set(1)
        elif choice == "Flujo de Caja":
            self.unselectAllCheakBoxes()
            self.mw.frame_sscc.var_ctas_ctes.set(1)
            self.mw.frame_sscc.var_banco_invico.set(1)
            self.mw.frame_recursos.var_flujo_caja.set(1)
        elif choice == "Control 3% INVICO":
            self.unselectAllCheakBoxes()
            self.mw.frame_siif.var_rci02.set(1)
            self.mw.frame_siif.var_rcocc31.set(1)
            self.mw.frame_sscc.var_ctas_ctes.set(1)
            self.mw.frame_recursos.var_ctrl_3_porc_invico.set(1)
        elif choice == "Ejecución Gastos":
            self.unselectAllCheakBoxes()
            self.mw.frame_siif.var_rf610.set(1)
            self.mw.frame_siif.var_rf602.set(1)
            self.mw.frame_siif.var_gto_rpa03g.set(1)
            self.mw.frame_siif.var_rcg01_uejp.set(1)
            self.mw.frame_siif.var_rfp_p605b.set(1)
            self.mw.frame_sscc.var_ctas_ctes.set(1)
            self.mw.frame_gastos.var_ejec_gastos.set(1)
            self.mw.frame_gastos.var_comprobantes_gastos.set(1)
        elif choice == "Planillómetro y Ejecución Obras":
            self.unselectAllCheakBoxes()
            self.mw.frame_siif.var_rf610.set(1)
            self.mw.frame_siif.var_rf602.set(1)
            self.mw.frame_sist_propios.var_icaro.set(1)
            self.mw.frame_recuperos.var_saldo_recuperos_cobrar_variacion.set(1)
            self.mw.frame_gastos.var_planillometro_obras.set(1)
            self.mw.frame_gastos.var_ejec_obras.set(1)
            self.mw.frame_gastos.var_ejec_fdos_provinciales.set(1)
            self.mw.frame_gastos.var_ejec_mod_basicos.set(1)
        elif choice == "Fondos Permanentes y Cajas Chicas":
            self.unselectAllCheakBoxes()
            self.mw.frame_siif.var_gto_rpa03g.set(1)
            self.mw.frame_siif.var_rcg01_uejp.set(1)
            # Falta un reporte SIIF rog01 (solo una vez)
            self.mw.frame_sscc.var_ctas_ctes.set(1)
            self.mw.frame_gastos.var_ejec_fdos_permanentes.set(1)
        elif choice == "Control Icaro":
            self.unselectAllCheakBoxes()
            self.mw.frame_sist_propios.var_icaro.set(1)
            self.mw.frame_siif.var_rf602.set(1)
            self.mw.frame_siif.var_gto_rpa03g.set(1)
            self.mw.frame_siif.var_rcg01_uejp.set(1)
            self.mw.frame_siif.var_rfondo07tp.set(1)
            self.mw.frame_sscc.var_ctas_ctes.set(1)
            self.mw.frame_gastos.var_ctrl_icaro.set(1)
        elif choice == "Control Obras":
            self.unselectAllCheakBoxes()
            self.mw.frame_siif.var_rdeu012.set(1)
            self.mw.frame_sgf.var_resumen_rend_prov.set(1)
            self.mw.frame_sgf.var_listado_prov.set(1)
            self.mw.frame_sscc.var_banco_invico.set(1)
            self.mw.frame_sscc.var_ctas_ctes.set(1)
            self.mw.frame_sist_propios.var_icaro.set(1)
            self.mw.frame_gastos.var_ctrl_obras.set(1)
        elif choice == "Listado Obras":
            self.unselectAllCheakBoxes()
            self.mw.frame_sist_propios.var_icaro.set(1)
            self.mw.frame_sgo.var_listado_obras.set(1)
            self.mw.frame_gastos.var_listado_obras.set(1)
        elif choice == "Control Haberes":
            self.unselectAllCheakBoxes()
            self.mw.frame_siif.var_rcg01_uejp.set(1)
            self.mw.frame_siif.var_gto_rpa03g.set(1)
            self.mw.frame_siif.var_rcocc31.set(1)
            self.mw.frame_siif.var_rdeu012.set(1)
            self.mw.frame_sscc.var_banco_invico.set(1)
            self.mw.frame_sscc.var_ctas_ctes.set(1)
            self.mw.frame_gastos.var_ctrl_haberes.set(1)
        elif choice == "Control Honorarios":
            self.unselectAllCheakBoxes()
            self.mw.frame_siif.var_rcg01_uejp.set(1)
            self.mw.frame_siif.var_gto_rpa03g.set(1)
            self.mw.frame_siif.var_rcocc31.set(1)
            self.mw.frame_sgf.var_resumen_rend_prov.set(1)
            self.mw.frame_sscc.var_banco_invico.set(1)
            self.mw.frame_sscc.var_ctas_ctes.set(1)
            self.mw.frame_sist_propios.var_slave.set(1)
            self.mw.frame_gastos.var_ctrl_honorarios.set(1)
        elif choice == "Control Escribanos":
            self.unselectAllCheakBoxes()
            self.mw.frame_siif.var_rcocc31.set(1)
            self.mw.frame_sgf.var_resumen_rend_prov.set(1)
            self.mw.frame_sscc.var_banco_invico.set(1)
            self.mw.frame_sscc.var_ctas_ctes.set(1)
            self.mw.frame_gastos.var_ctrl_escribanos.set(1)
        elif choice == "Control Retenciones":
            self.unselectAllCheakBoxes()
            self.mw.frame_siif.var_rdeu012.set(1)
            self.mw.frame_siif.var_rcocc31.set(1)
            self.mw.frame_sgf.var_resumen_rend_prov.set(1)
            self.mw.frame_sscc.var_banco_invico.set(1)
            self.mw.frame_sscc.var_ctas_ctes.set(1)
            self.mw.frame_sist_propios.var_icaro.set(1)
            self.mw.frame_gastos.var_ctrl_retenciones.set(1)
        elif choice == "Control Débitos Bancarios":
            self.unselectAllCheakBoxes()
            self.mw.frame_siif.var_rcg01_uejp.set(1)
            self.mw.frame_siif.var_gto_rpa03g.set(1)
            self.mw.frame_sscc.var_banco_invico.set(1)
            self.mw.frame_sscc.var_ctas_ctes.set(1)
            self.mw.frame_gastos.var_ctrl_debitos_bancarios.set(1)

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
            self.disableDownloadCheckBoxes()
            self.processDownload()

        if self.mw.var_update.get() == 1:
            self.processUpdate()

        if self.mw.var_upload.get() == 1:
            self.processUpload()
    
    @staticmethod
    def getMonthsList(years):
        years = list(map(int, years))
        fecha_actual = dt.datetime.now()
        lista_meses = []
        for year in years:
            for month in range(1, 13):  # Iterar sobre los meses del año
                fecha = dt.date(year, month, 1)  # Crear una fecha para el primer día de cada mes
                if fecha.year < fecha_actual.year:
                    mes_anio = fecha.strftime("%Y-%m")  # Formatear la fecha como "mm-yyyy"
                    lista_meses.append(mes_anio)  # Agregar el mes al lista
                elif fecha.year == fecha_actual.year:
                    if fecha.month <= fecha_actual.month:
                        mes_anio = fecha.strftime("%Y-%m")  # Formatear la fecha como "mm-yyyy"
                        lista_meses.append(mes_anio)  # Agregar el mes al lista
        return lista_meses


    def processDownload(self):
        print('***Iniciando descarga de datos***')
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
            siif_credentials_path = os.path.join(
                credentials_path, 'siif_credentials.json'
            )
            siif = DownloadSIIF(
                path_credentials_file = siif_credentials_path,
                output_path = os.path.join(output_path, 'Reportes SIIF'),
            )
            # Mantenemos abierta la conexión hasta descargar todos los reportes que necesitamos
            siif.download_all = True
            siif.go_to_reports()

            if self.mw.frame_siif.var_rf610.get() == 1:
                siif.download_ppto_gtos_desc_rf610(ejercicios)
            if self.mw.frame_siif.var_rf602.get() == 1:
                siif.download_ppto_gtos_fte_rf602(ejercicios)
            if self.mw.frame_siif.var_rcg01_uejp.get() == 1:
                siif.download_comprobantes_gtos_rcg01_uejp(ejercicios)
            if self.mw.frame_siif.var_gto_rpa03g.get() == 1:
                siif.download_comprobantes_gtos_gpo_part_gto_rpa03g(ejercicios)
            if self.mw.frame_siif.var_rdeu012.get() == 1:
                meses = self.getMonthsList(ejercicios)
                siif.download_deuda_flotante_rdeu012(meses)   
            if self.mw.frame_siif.var_rfondo07tp.get() == 1:
                siif.download_resumen_fdos_rfondo07tp(ejercicios)  
            if self.mw.frame_siif.var_ri102.get() == 1:
                siif.download_ppto_rec_ri102(ejercicios)  
            if self.mw.frame_siif.var_rci02.get() == 1:
                siif.download_comprobantes_rec_rci02(ejercicios)  
            if self.mw.frame_siif.var_rcocc31.get() == 1:
                # Determinamos las cuentas Contables a descargar (¿esto es correcto?)
                ctas_contables = [
                    '1112-2-6', '1141-1-4', '2111-1-1', '2111-1-2',
                    '2113-2-9', '2121-1-1', '2122-1-2',
                ]
                siif.download_mayor_contable_rcocc31(
                    ejercicios, ctas_contables=ctas_contables
                )
            if self.mw.frame_siif.var_rfp_p605b.get() == 1:
                last_ejercicio = int(ejercicios[-1])
                if last_ejercicio < dt.datetime.now().year:
                    siif.download_form_gto_rfp_p605b(ejercicios)
                elif last_ejercicio == dt.datetime.now().year:
                    if dt.datetime.now().month >= 9:
                        siif.download_form_gto_rfp_p605b(ejercicios)
                else:
                    ejercicios_aux = ejercicios.copy()
                    ejercicios_aux = ejercicios_aux[:-1]
                    siif.download_form_gto_rfp_p605b(ejercicios)
            
            siif.quit() #Revisar el remove HTML
        
        # Verificamos si se desea bajar el Resumen de Rend. Prov. SGF
        if self.mw.frame_sgf.var_resumen_rend_prov.get() == 1:
            # Cargamos credenciales e instanciamos SGF
            invico_credentials_path = os.path.join(
                credentials_path, 'invico_credentials.json'
            )
            sgf = DownloadSGF(
                path_credentials_file=invico_credentials_path,
                output_path=os.path.join(output_path, 'Sistema Gestion Financiera')
            )
            sgf.download_resumen_rend_prov(ejercicios)
            # Faltan los otros reportes
            # if self.mw.frame_sgf.var_resumen_rend_obras.get() == 1:
            #     sgf.download_ppto_gtos_desc_rf610(ejercicios)
            # if self.mw.frame_sgf.var_certificados_obras.get() == 1:
            #     sgf.download_ppto_gtos_desc_rf610(ejercicios)
            # if self.mw.frame_sgf.var_listado_prov.get() == 1:
            #     sgf.download_ppto_gtos_desc_rf610(ejercicios)
        
        # Verificamos si se desea bajar los Mov Grales SSCC
        if self.mw.frame_sscc.var_banco_invico.get() == 1:
            # Cargamos credenciales e instanciamos SSCC
            invico_credentials_path = os.path.join(
                credentials_path, 'invico_credentials.json'
            )
            sscc = DownloadSSCC(
                path_credentials_file=invico_credentials_path,
                output_path=os.path.join(output_path, 'Sistema de Seguimiento de Cuentas Corrientes')
            )
            sscc.download_banco_invico(ejercicios)
            # Falta agregar el proceso de autodescarga de saldos finales SSCC

        # Verificamos si existen reportes del Sist Recuperos para descargar
        recuperos_list = self.mw.frame_recuperos.getText()
        if len(recuperos_list) > 0:
            # Cargamos credenciales e instanciamos Sist Recuperos
            recuperos_credentials_path = os.path.join(
                credentials_path, 'sgv_credentials.json'
            )
            recuperos = DownloadSGV(
                path_credentials_file = recuperos_credentials_path,
                output_path = os.path.join(output_path, 'Gestión Vivienda GV')
            )
            # Mantenemos abierta la conexión hasta descargar todos los reportes que necesitamos
            recuperos.download_all = True

            if self.mw.frame_recuperos.var_saldo_barrio.get() == 1:
                recuperos.download_saldo_barrio(ejercicios)
            if self.mw.frame_recuperos.var_saldo_barrio_variacion.get() == 1:
                recuperos.download_saldo_barrio_variacion(ejercicios)
            if self.mw.frame_recuperos.var_saldo_recuperos_cobrar_variacion.get() == 1:
                recuperos.download_saldo_recuperos_cobrar_variacion(ejercicios)
            if self.mw.frame_recuperos.var_saldo_motivo.get() == 1:
                recuperos.download_saldo_motivo(ejercicios)
            if self.mw.frame_recuperos.var_saldo_motivo_por_barrio.get() == 1:
                recuperos.download_saldo_motivo_por_barrio(ejercicios)
            if self.mw.frame_recuperos.var_barrios_nuevos.get() == 1:
                recuperos.download_barrios_nuevos(ejercicios)
            if self.mw.frame_recuperos.var_resumen_facturado.get() == 1:
                recuperos.download_resumen_facturado(ejercicios)
            if self.mw.frame_recuperos.var_resumen_recaudado.get() == 1:
                recuperos.download_resumen_recaudado(ejercicios)
            recuperos.quit()

        # Verificamos si existen reportes del Sist Propios para descargar
        sist_propios_list = self.mw.frame_sist_propios.getText()
        if len(sist_propios_list) > 0:
            if self.mw.frame_sist_propios.var_icaro.get() == 1:
                my_path = HanglingPath().get_outside_path()
                exequiel_path = HanglingPath().get_r_icaro_path()
                CopyIcaro(
                    exequiel_path = os.path.join(exequiel_path, 'ICARO.sqlite'),
                    my_path = os.path.join(my_path, 'R Output/SQLite Files/ICARO.sqlite')
                )
            if self.mw.frame_sist_propios.var_slave.get() == 1:
                exequiel_path = HanglingPath().get_slave_path()
                CopySlave(
                    exequiel_path = os.path.join(exequiel_path, 'Slave.mdb'),
                    my_path = os.path.join(output_path, 'Slave/Slave.mdb')
                )

        sgo_list = self.mw.frame_sgo.getText()
        if len(sgo_list) > 0:
            # Cargamos credenciales e instanciamos SIIF
            sgo_credentials_path = os.path.join(
                credentials_path, 'sgv_credentials.json'
            )
            sgo = DownloadSGO(
                path_credentials_file = sgo_credentials_path,
                output_path = os.path.join(output_path, 'Sistema Gestion Obras'),
            )
            # Mantenemos abierta la conexión hasta descargar todos los reportes que necesitamos
            sgo.download_all = True

            if self.mw.frame_sgo.var_listado_obras.get() == 1:
                sgo.download_listado_obras()
            sgo.quit()

        print('***Finalizando descarga de datos***')
    def processUpdate(self):
        print('***Iniciando actualización de Base de Datos***')
        # Generamos output path y credentials path
        input_path = HanglingPath().get_update_path_input()
        output_path = HanglingPath().get_db_path()

        # Verificamos si existen reportes SIIF para descargar
        siif_list = self.mw.frame_siif.getText()
        if len(siif_list) > 0:
            # Cargamos credenciales e instanciamos SIIF

            siif = UpdateSIIF(
                os.path.join(input_path, 'Reportes SIIF'), 
                os.path.join(output_path, 'siif.sqlite')
            )

            if self.mw.frame_siif.var_rf610.get() == 1:
                siif.update_ppto_gtos_desc_rf610()
            if self.mw.frame_siif.var_rf602.get() == 1:
                siif.update_ppto_gtos_fte_rf602()
            if self.mw.frame_siif.var_rcg01_uejp.get() == 1:
                siif.update_comprobantes_gtos_rcg01_uejp()
            if self.mw.frame_siif.var_gto_rpa03g.get() == 1:
                siif.update_comprobantes_gtos_gpo_part_gto_rpa03g()
            if self.mw.frame_siif.var_rdeu012.get() == 1:
                siif.update_deuda_flotante_rdeu012()   
            if self.mw.frame_siif.var_rfondo07tp.get() == 1:
                siif.update_resumen_fdos_rfondo07tp()  
            if self.mw.frame_siif.var_ri102.get() == 1:
                siif.update_ppto_rec_ri102()  
            if self.mw.frame_siif.var_rci02.get() == 1:
                siif.update_comprobantes_rec_rci02()  
            if self.mw.frame_siif.var_rcocc31.get() == 1:
                siif.update_mayor_contable_rcocc31()
            if self.mw.frame_siif.var_rfp_p605b.get() == 1:
                siif.update_form_gto_rfp_p605b()
            # Actualizamos estos reportes siempre
            siif.update_deuda_flotante_rdeu012b2_c()
            siif.update_detalle_partidas_rog01()
        
        sgf_list = self.mw.frame_sgf.getText()
        if len(sgf_list) > 0:

            # Cargamos credenciales e instanciamos SGF
            sgf = UpdateSGF(
                os.path.join(input_path, 'Sistema Gestion Financiera'), 
                os.path.join(output_path, 'sgf.sqlite')
            )

            if self.mw.frame_sgf.var_resumen_rend_prov.get() == 1:
                sgf.update_resumen_rend_prov()
            if self.mw.frame_sgf.var_resumen_rend_obras.get() == 1:
                sgf.update_resumen_rend_obras()
            if self.mw.frame_sgf.var_certificados_obras.get() == 1:
                sgf.update_certificados_obras()
            if self.mw.frame_sgf.var_listado_prov.get() == 1:
                sgf.update_listado_prov()
        
        sscc_list = self.mw.frame_sscc.getText()
        if len(sscc_list) > 0:
            # Cargamos credenciales e instanciamos SSCC

            sscc = UpdateSSCC(
                os.path.join(input_path, 'Sistema de Seguimiento de Cuentas Corrientes'), 
                os.path.join(output_path,'sscc.sqlite')
            )

            if self.mw.frame_sscc.var_banco_invico.get() == 1:
                sscc.update_banco_invico()
            if self.mw.frame_sscc.var_ctas_ctes.get() == 1:
                sscc.update_ctas_ctes()
            if self.mw.frame_sscc.var_sdo_final_banco_invico.get() == 1:
                sscc.update_sdo_final_banco_invico()

        # Verificamos si existen reportes del Sist Recuperos para descargar
        recuperos_list = self.mw.frame_recuperos.getText()
        if len(recuperos_list) > 0:

            recuperos = UpdateSGV(
                os.path.join(input_path, 'Gestión Vivienda GV'), 
                os.path.join(output_path, 'sgv.sqlite')
            )

            if self.mw.frame_recuperos.var_saldo_barrio.get() == 1:
                recuperos.update_saldo_barrio()
            if self.mw.frame_recuperos.var_saldo_barrio_variacion.get() == 1:
                recuperos.update_saldo_barrio_variacion()
            if self.mw.frame_recuperos.var_saldo_recuperos_cobrar_variacion.get() == 1:
                recuperos.update_saldo_recuperos_cobrar_variacion()
            if self.mw.frame_recuperos.var_saldo_motivo.get() == 1:
                recuperos.update_saldo_motivo()
            if self.mw.frame_recuperos.var_saldo_motivo_por_barrio.get() == 1:
                recuperos.update_saldo_motivo_por_barrio()
            if self.mw.frame_recuperos.var_barrios_nuevos.get() == 1:
                recuperos.update_barrios_nuevos()
            if self.mw.frame_recuperos.var_resumen_facturado.get() == 1:
                recuperos.update_resumen_facturado()
            if self.mw.frame_recuperos.var_resumen_recaudado.get() == 1:
                recuperos.update_resumen_recaudado()

        # Verificamos si existen reportes del Sist Propios para descargar
        sist_propios_list = self.mw.frame_sist_propios.getText()
        if len(sist_propios_list) > 0:
            if self.mw.frame_sist_propios.var_icaro.get() == 1:
                UpdateIcaro(
                    os.path.join(HanglingPath().get_outside_path(),
                    'R Output/SQLite Files/ICARO.sqlite'), 
                    os.path.join(output_path, 'icaro.sqlite')
                    ).migrate_icaro()

            if self.mw.frame_sist_propios.var_slave.get() == 1:
                UpdateSlave(
                    os.path.join(input_path, 'Slave/Slave.mdb'), 
                    os.path.join(output_path, 'slave.sqlite')
                    ).migrate_slave()
                
        sgo_list = self.mw.frame_sgo.getText()
        if len(sgo_list) > 0:
            sgo = UpdateSGO(
                os.path.join(input_path, 'Sistema Gestion Obras'), 
                os.path.join(output_path,'sgo.sqlite')
            )

            if self.mw.frame_sgo.var_listado_obras.get() == 1:
                sgo.update_listado_obras()

        print('***Finalizando actualización de Base de Datos***')
    def processUpload(self):
        print('***Iniciando subida de datos a Google Sheet***')

        ejercicio_actual = str(dt.datetime.now().year)
        ejercicio_anterior = str(dt.datetime.now().year - 1)
        ejercicio_siguiente = str(dt.datetime.now().year + 1)
        ejercicios_varios = range(int(ejercicio_actual)-5, int(ejercicio_actual)+1)
        ejercicios_varios = [str(x) for x in ejercicios_varios]

        google_credentials_path = HanglingPath().get_invicodb_path()
        google_credentials_path = os.path.join(
            google_credentials_path, 'upload'
        )
        google_credentials_path = os.path.join(
            google_credentials_path, 'google_credentials.json'
        )
        input_path = HanglingPath().get_update_path_input()
        output_path = HanglingPath().get_db_path()

        upload = UploadGoogleSheet(
            path_credentials_file=google_credentials_path,
            ejercicio='2023',
            update_db=False,
            input_path=input_path,
            output_path=output_path
        )

        recursos_list = self.mw.frame_recursos.getText()
        if len(recursos_list) > 0:

            if (self.mw.frame_recursos.var_ejec_recursos.get() == 1 or 
                self.mw.frame_recursos.var_comprobantes_recursos.get() == 1 or
                self.mw.frame_recursos.var_ctrl_recursos.get() == 1):
                upload.upload_control_recursos(ejercicios_varios)
            if self.mw.frame_recursos.var_flujo_caja.get() == 1:
                upload.upload_flujo_caja(ejercicios_varios)
            if self.mw.frame_recursos.var_ctrl_3_porc_invico.get() == 1:
                upload.upload_control_3_porciento_invico([ejercicio_actual, ejercicio_anterior])

        gastos_list = self.mw.frame_gastos.getText()
        if len(gastos_list) > 0:
            #self.upload_planillometro()
            #self.upload_formulacion_gtos()
            if (self.mw.frame_gastos.var_ejec_gastos.get() == 1 or 
                self.mw.frame_gastos.var_comprobantes_gastos.get() == 1):
                upload.upload_ejecucion_gtos(ejercicios_varios)
            if self.mw.frame_gastos.var_planillometro_obras.get() == 1:
                upload.upload_planillometro()  #Sin determinar ejercicios?
            if (self.mw.frame_gastos.var_ejec_obras.get() == 1 or 
                self.mw.frame_gastos.var_ejec_mod_basicos.get() == 1):
                upload.upload_ejecucion_pres() #Sin determinar ejercicios?
            if self.mw.frame_gastos.var_ejec_fdos_provinciales.get() == 1:
                upload.upload_ejecucion_obras_fondos_prov(ejercicios_varios)
            if self.mw.frame_gastos.var_ejec_fdos_permanentes.get() == 1:
                upload.upload_fondos_perm_cajas_chicas(ejercicios_varios)
            if self.mw.frame_gastos.var_ctrl_icaro.get() == 1:
                upload.upload_control_icaro(ejercicios_varios)
            if self.mw.frame_gastos.var_ctrl_obras.get() == 1:
                upload.upload_control_obras(ejercicios_varios)
            if self.mw.frame_gastos.var_listado_obras.get() == 1:
                upload.upload_listado_obras()
            if self.mw.frame_gastos.var_ctrl_haberes.get() == 1:
                upload.upload_control_haberes([ejercicio_actual, ejercicio_anterior])
            if self.mw.frame_gastos.var_ctrl_honorarios.get() == 1:
                upload.upload_control_honorarios([ejercicio_actual, ejercicio_anterior])
            if self.mw.frame_gastos.var_ctrl_escribanos.get() == 1:
                upload.upload_control_escribanos([ejercicio_actual, ejercicio_anterior])
            if self.mw.frame_gastos.var_ctrl_retenciones.get() == 1:
                upload.upload_control_retenciones([ejercicio_actual, ejercicio_anterior])
            if self.mw.frame_gastos.var_ctrl_debitos_bancarios.get() == 1:
                upload.upload_control_debitos_bancarios([ejercicio_actual, ejercicio_anterior])

        print('***Finalizando subida de datos a Google Sheet***')
