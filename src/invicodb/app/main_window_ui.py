import datetime as dt
from dataclasses import dataclass

import customtkinter as ctk

from .default_widgets_setup import *


@dataclass
class MainWindowUI():
    master:ctk.CTk
    row_frame:int = 0
    column_frame:int = 0
    padding_frame:int = 20
    padx_frame:int = 20
    pady_frame:int = 5
    padx_checkbox:int = 5
    pady_checkbox:int = 5

    def __post_init__(self):
        self.setupInitialParametersFrame(row=0, column=0, columnspan=3)
        self.setupTabViewDUU(row=1, column=0, columnspan=3)
        self.setupSIIFFrame(row=0, column=0, rowspan=2)
        self.setupSGFFrame(row=0, column=1)
        self.setupSSCCFrame(row=1, column=1)
        self.setupSistemaRecuperosFrame(row=0, column=2)
        self.setupSistemasPropiosFrame(row=1, column=2)
        self.setupProcessFrame(row=2, column=0, columnspan=3)
        self.setupRecursosFrame(row=0, column=0)
        self.setupGastosFrame(row=0, column=1)

    def setupInitialParametersFrame(
        self, row:int = 1, column:int = 0, rowspan:int = 1, columnspan:int = 1
    ):
        self.frame_process = DefaultFrame(self.master)
        self.frame_process.configure(height=50)
        self.frame_process.grid(
            row=row, column=column, rowspan=rowspan, columnspan=columnspan,
            padx=self.padx_frame, pady=0, sticky="nsew",             
        )
        for index in [1, 2, 3, 4]:
            self.frame_process.columnconfigure(index=index, weight=1)

        optional_menu_list = [
            'Personalizado',
            'Completo',
            'Completo Sin Recuperos',
            'Control Icaro'
        ]
        var_option_process_type = ctk.StringVar(value="Personalizado")
        self.optional_process_type = DefaultOptionMenu(
            self.frame_process, values = optional_menu_list,
            variable = var_option_process_type,
        )
        self.optional_process_type.configure(width=300)
        # self.optional_menu.set("Readonly combobox")
        self.optional_process_type.grid(
            row=0, column=0, sticky="nsew",
            padx=self.padx_checkbox, pady=self.pady_checkbox
        )

        current_year = dt.datetime.now().year
        year_list = list(map(str, range(current_year, 2009, -1)))

        self.label_desde = ctk.CTkLabel(self.frame_process, text="Desde:")
        self.label_desde.grid(
            row=0, column=1, sticky="nsew",
        )
        var_option_desde = ctk.StringVar(value= str(current_year))
        self.option_desde = DefaultOptionMenu(
            self.frame_process, values=year_list, variable=var_option_desde)
        self.option_desde.grid(
            row=0, column=2, sticky="nsew", 
            padx=self.padx_checkbox, pady=self.pady_checkbox
        )

        self.label_hasta = ctk.CTkLabel(self.frame_process, text="Hasta:")
        self.label_hasta.grid(row=0, column=3, sticky="nsew")
        var_option_hasta = ctk.StringVar(value= str(current_year))
        self.option_hasta = DefaultOptionMenu(
            self.frame_process, values=year_list, variable=var_option_hasta
        )
        self.option_hasta.grid(
            row=0, column=4, sticky="nsew", 
            padx=self.padx_checkbox, pady=self.pady_checkbox
        )

    def setupTabViewDUU(
        self, row:int = 1, column:int = 0, rowspan:int = 1, columnspan:int = 1
    ):
        self.tabview_duu = DefaultTabView(self.master)
        self.tabview_duu.configure(width=1050, height=595)
        self.tab_download_update = self.tabview_duu.add('Download & Update')
        self.tab_upload = self.tabview_duu.add('Upload (Google Sheet)')
        self.tabview_duu.grid(
            row=row, column=column, rowspan=rowspan, columnspan=columnspan,
            padx=self.padx_frame, pady=0, sticky="nsew", 
        )

    def setupSIIFFrame(
        self, row:int = 1, column:int = 0, rowspan:int = 1, columnspan:int = 1
    ):
        
        values_and_vars = {
            'Presupuesto Gastos con Descripción (rf610)':'var_rf610',
            'Presupuesto Gastos con Fuentes (rf602)':'var_rf602',
            'Comprobantes Gastos (rcg01_uejp)':'var_rcg01_uejp',
            'Comprobantes Gastos x Partida (rpa03g)':'var_gto_rpa03g',
            'Deuda Flotante (rdeu012)':'var_rdeu012',
            'Resumen de Fondos (rfondo07tp)':'var_rfondo07tp',
            'Presupuesto Recursos (ri102)':'var_ri102',
            'Comprobantes Recursos (rci02)':'var_rci02',
            'Mayor Contable (rcocc31)':'var_rcocc31',
            'Formulación Gastos (rfp_p605b)':'var_rfp_p605b',
        }
        self.frame_siif = MyScrollableCheckboxFrame(
            self.tab_download_update, title="SIIF", 
            values_and_vars=values_and_vars,
            padx_checkbox=self.padx_checkbox, pady_checkbox=self.pady_checkbox
        )
        # self.frame_siif.configure(height = 450)
        self.frame_siif.grid(
            row=row, column=column, rowspan=rowspan, columnspan=columnspan,
            padx=self.padx_frame, pady=self.pady_frame, sticky="nsew", 
        )

    def setupSGFFrame(
        self, row:int = 1, column:int = 0, rowspan:int = 1, columnspan:int = 1
    ):

        values_and_vars = {
            'Resumen de Rendiciones por Proveedor':'var_resumen_rend_prov',
            'Resumen de Rendiciones por Obra':'var_resumen_rend_obras',
            'Certificados de Obras':'var_certificados_obras',
            'Listado de Proveedores':'var_listado_prov',
        }
        self.frame_sgf = MyScrollableCheckboxFrame(
            self.tab_download_update, title="Sistema de Gestión Financiera (SGF)", 
            values_and_vars=values_and_vars,
            padx_checkbox=self.padx_checkbox, pady_checkbox=self.pady_checkbox
        )
        self.frame_sgf.grid(
            row=row, column=column, rowspan=rowspan, columnspan=columnspan,
            padx=self.padx_frame, pady=self.pady_frame, sticky="nsew", 
        )

    def setupSSCCFrame(
        self, row:int = 1, column:int = 0, rowspan:int = 1, columnspan:int = 1
    ):

        values_and_vars = {
            'Listado de Cuentas Corrientes (Manual)':'var_ctas_ctes',
            'Consulta General de Movimientos':'var_banco_invico',
            'Saldo Final Banco INVICO (Manual)':'var_sdo_final_banco_invico',
        }
        self.frame_sscc = MyScrollableCheckboxFrame(
            self.tab_download_update, title="Sistema de Seguimiento de Ctas Ctes (SSCC)", 
            values_and_vars=values_and_vars,
            padx_checkbox=self.padx_checkbox, pady_checkbox=self.pady_checkbox
        )
        self.frame_sscc.grid(
            row=row, column=column, rowspan=rowspan, columnspan=columnspan,
            padx=self.padx_frame, pady=self.pady_frame, sticky="nsew", 
        )

    def setupSistemaRecuperosFrame(
        self, row:int = 1, column:int = 0, rowspan:int = 1, columnspan:int = 1
    ):

        values_and_vars = {
            'Saldos por Barrio':'var_saldo_barrio',
            'Evolución de Saldos por Barrio':'var_saldo_barrio_variacion',
            'Variación de Saldos Recuperos a Cobrar':'var_saldo_recuperos_cobrar_variacion',
            'Evolución de Saldos por Motivos':'var_saldo_motivo',
            'Evolución de Saldos por Motivos por Barrio':'var_saldo_motivo_por_barrio',
            'Barrios Nuevos Incorporados':'var_barrios_nuevos',
            'Resumen Facturado':'var_resumen_facturado',
            'Resumen Recaudado':'var_resumen_recaudado',
        }
        self.frame_recuperos = MyScrollableCheckboxFrame(
            self.tab_download_update, title="Sistema Recuperos", values_and_vars=values_and_vars,
            padx_checkbox=self.padx_checkbox, pady_checkbox=self.pady_checkbox
        )
        self.frame_recuperos.grid(
            row=row, column=column, rowspan=rowspan, columnspan=columnspan,
            padx=self.padx_frame, pady=self.pady_frame, sticky="nsew", 
        )

    def setupSistemasPropiosFrame(
        self, row:int = 1, column:int = 0, 
        rowspan:int = 1, columnspan:int = 1
    ):
        values_and_vars = {
            'Icaro': 'var_icaro',
            'Slave': 'var_slave',
        }
        self.frame_sist_propios = MyScrollableCheckboxFrame(
            self.tab_download_update, title="Sistemas Propios", values_and_vars=values_and_vars,
            padx_checkbox=self.padx_checkbox, pady_checkbox=self.pady_checkbox
        )
        self.frame_sist_propios.grid(
            row=row, column=column, rowspan=rowspan, columnspan=columnspan,
            padx=self.padx_frame, pady=self.pady_frame, sticky="nsew", 
        )

    def setupRecursosFrame(
        self, row:int = 0, column:int = 0, rowspan:int = 1, columnspan:int = 1
    ):

        values_and_vars = {
            'Ejecución Anual Recursos':'var_ejec_recursos',
            'Comprobantes Recursos':'var_comprobantes_recursos',
            'Flujo de Caja':'var_flujo_caja',
            'Control Recursos':'var_ctrl_recursos',
            'Control 3% INVICO':'var_ctrl_3_porc_invico',
        }
        self.frame_recursos = MyScrollableCheckboxFrame(
            self.tab_upload, title="Recursos", values_and_vars=values_and_vars,
            padx_checkbox=self.padx_checkbox, pady_checkbox=self.pady_checkbox
        )
        self.frame_recursos.grid(
            row=row, column=column, rowspan=rowspan, columnspan=columnspan,
            padx=self.padx_frame, pady=self.pady_frame, sticky="nsew", 
        )

    def setupGastosFrame(
        self, row:int = 0, column:int = 0, rowspan:int = 1, columnspan:int = 1
    ):

        values_and_vars = {
            'Control Icaro':'var_ctrl_icaro',
            # 'Evolución de Saldos por Barrio':'var_saldo_barrio_variacion',
            # 'Variación de Saldos Recuperos a Cobrar':'var_saldo_recuperos_cobrar_variacion',
            # 'Evolución de Saldos por Motivos':'var_saldo_motivo',
            # 'Evolución de Saldos por Motivos por Barrio':'var_saldo_motivo_por_barrio',
            # 'Barrios Nuevos Incorporados':'var_barrios_nuevos',
            # 'Resumen Facturado':'var_resumen_facturado',
            # 'Resumen Recaudado':'var_resumen_recaudado',
        }
        self.frame_gastos = MyScrollableCheckboxFrame(
            self.tab_upload, title="Gastos", values_and_vars=values_and_vars,
            padx_checkbox=self.padx_checkbox, pady_checkbox=self.pady_checkbox
        )
        self.frame_gastos.grid(
            row=row, column=column, rowspan=rowspan, columnspan=columnspan,
            padx=self.padx_frame, pady=self.pady_frame, sticky="nsew", 
        )

    def setupProcessFrame(
        self, row:int = 1, column:int = 0, rowspan:int = 1, columnspan:int = 1
    ):
        self.frame_process = DefaultFrame(self.master)
        self.frame_process.configure(height=50)
        self.frame_process.grid(
            row=row, column=column, rowspan=rowspan, columnspan=columnspan,
            padx=self.padx_frame, pady=self.pady_frame, sticky="nsew",             
        )
        for index in [0, 1, 2, 4]:
            self.frame_process.columnconfigure(index=index, weight=1)
        
        self.var_download = ctk.BooleanVar(value=True)
        self.switch_download = DefaultSwitch(
            self.frame_process, text="Download", variable=self.var_download,
        )
        self.switch_download.grid(
            row = 0, column = 0, padx = 10, pady = 10
        )

        self.var_update = ctk.BooleanVar(value=True)
        self.switch_update = DefaultSwitch(
            self.frame_process, text="Update", variable=self.var_update,
        )
        self.switch_update.grid(
            row = 0, column = 1, padx = 10, pady = 10
        )

        self.var_upload = ctk.BooleanVar(value=True)
        self.switch_upload = DefaultSwitch(
            self.frame_process, text="Upload", variable=self.var_upload,
        )
        self.switch_upload.grid(
            row = 0, column = 2, padx = 10, pady = 10
        )
        
        self.button_start = DefaultButton(
            self.frame_process, text="Process", 
        )
        self.button_start.grid(row = 0, column = 4, padx = 10, pady = 10)
