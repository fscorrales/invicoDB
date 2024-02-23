import tkinter as tk
from tkinter import ttk
from dataclasses import dataclass

@dataclass
class WidgetSetup:
    parent:ttk.Frame
    row_frame:int = 0
    column_frame:int = 0
    rowspan_frame:int = 1
    columnspan_frame:int = 1
    padding_frame:int = 20
    padx_frame:int = 20
    pady_frame:int = 10
    padx_checkbox:int = 5
    pady_checkbox:int = 10
    
    def setupSIIFWidgets(
        self, row_frame = None, column_frame:int = None, 
        rowspan_frame:int = None, columnspan_frame:int = None,
        padding_frame:int = None, padx_frame:int = None, pady_frame:int = None,
        padx_checkbox:int = None, pady_checkbox:int = None
    ):
        if row_frame is None:
            row_frame = self.row_frame
        if column_frame is None:
            column_frame = self.column_frame
        if rowspan_frame is None:
            rowspan_frame = self.rowspan_frame
        if columnspan_frame is None:
            columnspan_frame = self.columnspan_frame
        if padding_frame is None:
            padding_frame = self.padding_frame            
        if padx_frame is None:
            padx_frame = self.padx_frame
        if pady_frame is None:
            pady_frame = self.pady_frame
        if padx_checkbox is None:
            padx_checkbox = self.padx_checkbox
        if pady_checkbox is None:
            pady_checkbox = self.pady_checkbox

        
        # Create a Frame for SIIF
        self.parent.check_frame_siif = ttk.LabelFrame(self.parent, text="SIIF", padding=padding_frame)
        self.parent.check_frame_siif.grid(
            row=row_frame, column=column_frame, padx=padx_frame, pady=pady_frame, sticky="nsew",
            rowspan=rowspan_frame, columnspan=columnspan_frame
        )

        # Checkbuttons
        row = 0
        self.parent.var_rf610 = tk.BooleanVar()
        self.parent.check_rf610 = ttk.Checkbutton(
            self.parent.check_frame_siif, text="Presupuesto Gastos con Descripción (rf610)", variable=self.parent.var_rf610
        )
        self.parent.check_rf610.grid(row=row, column=0, padx=padx_checkbox, pady=pady_checkbox, sticky="nsew")

        row += 1
        self.parent.var_rf602 = tk.BooleanVar()
        self.parent.check_rf602 = ttk.Checkbutton(
            self.parent.check_frame_siif, text="Presupuesto Gastos con Fuentes (rf602)", variable=self.parent.var_rf602
        )
        self.parent.check_rf602.grid(row=row, column=0, padx=padx_checkbox, pady=pady_checkbox, sticky="nsew")

        row += 1
        self.parent.var_rcg01_uejp = tk.BooleanVar()
        self.parent.check_rcg01_uejp = ttk.Checkbutton(
            self.parent.check_frame_siif, text="Comprobantes Gastos (rcg01_uejp)", variable=self.parent.var_rcg01_uejp
        )
        self.parent.check_rcg01_uejp.grid(row=row, column=0, padx=padx_checkbox, pady=pady_checkbox, sticky="nsew")

        row += 1
        self.parent.var_rpa03g  = tk.BooleanVar()
        self.parent.check_rpa03g = ttk.Checkbutton(
            self.parent.check_frame_siif, text="Comprobantes Gastos x Partida (rpa03g)", variable=self.parent.var_rpa03g
        )
        self.parent.check_rpa03g.grid(row=row, column=0, padx=padx_checkbox, pady=pady_checkbox, sticky="nsew")

        row += 1
        self.parent.var_rdeu012  = tk.BooleanVar()
        self.parent.check_rdeu012 = ttk.Checkbutton(
            self.parent.check_frame_siif, text="Deuda Flotante (rdeu012)", variable=self.parent.var_rdeu012
        )
        self.parent.check_rdeu012.grid(row=row, column=0, padx=padx_checkbox, pady=pady_checkbox, sticky="nsew")

        row += 1
        self.parent.var_rfondo07tp = tk.BooleanVar()
        self.parent.check_rfondo07tp = ttk.Checkbutton(
            self.parent.check_frame_siif, text="Resumen de Fondos (rfondo07tp)", variable=self.parent.var_rfondo07tp
        )
        self.parent.check_rfondo07tp.grid(row=row, column=0, padx=padx_checkbox, pady=pady_checkbox, sticky="nsew")

        row += 1
        self.parent.var_ri102 = tk.BooleanVar()
        self.parent.check_ri102 = ttk.Checkbutton(
            self.parent.check_frame_siif, text="Presupuesto Recursos (ri102)", variable=self.parent.var_ri102
        )
        self.parent.check_ri102.grid(row=row, column=0, padx=padx_checkbox, pady=pady_checkbox, sticky="nsew")

        row += 1
        self.parent.var_rci02  = tk.BooleanVar()
        self.parent.check_rci02 = ttk.Checkbutton(
            self.parent.check_frame_siif, text="Comprobantes Recursos (rci02)", variable=self.parent.var_rci02
        )
        self.parent.check_rci02.grid(row=row, column=0, padx=padx_checkbox, pady=pady_checkbox, sticky="nsew")

        row += 1
        self.parent.var_rcocc31  = tk.BooleanVar()
        self.parent.check_rcocc31 = ttk.Checkbutton(
            self.parent.check_frame_siif, text="Mayor Contable (rcocc31)", variable=self.parent.var_rcocc31
        )
        self.parent.check_rcocc31.grid(row=row, column=0, padx=padx_checkbox, pady=pady_checkbox, sticky="nsew")

        row += 1
        self.parent.var_rfp_p605b  = tk.BooleanVar()
        self.parent.check_rfp_p605b = ttk.Checkbutton(
            self.parent.check_frame_siif, text="Formulación Gastos (rfp_p605b)", variable=self.parent.var_rfp_p605b
        )
        self.parent.check_rfp_p605b.grid(row=row, column=0, padx=padx_checkbox, pady=pady_checkbox, sticky="nsew")

    def setupSGFWidgets(
        self, row_frame = None, column_frame:int = None, 
        rowspan_frame:int = None, columnspan_frame:int = None,
        padding_frame:int = None, padx_frame:int = None, pady_frame:int = None,
        padx_checkbox:int = None, pady_checkbox:int = None
    ):
        if row_frame is None:
            row_frame = self.row_frame
        if column_frame is None:
            column_frame = self.column_frame
        if rowspan_frame is None:
            rowspan_frame = self.rowspan_frame
        if columnspan_frame is None:
            columnspan_frame = self.columnspan_frame
        if padding_frame is None:
            padding_frame = self.padding_frame    
        if padx_frame is None:
            padx_frame = self.padx_frame
        if pady_frame is None:
            pady_frame = self.pady_frame
        if padx_checkbox is None:
            padx_checkbox = self.padx_checkbox
        if pady_checkbox is None:
            pady_checkbox = self.pady_checkbox

        # Create a Frame for SGV
        self.parent.check_frame_sgf = ttk.LabelFrame(self.parent, text="Sistema de Gestión Financiera (SGF)", padding=padding_frame)
        self.parent.check_frame_sgf.grid(
            row=row_frame, column=column_frame, padx=padx_frame, pady=pady_frame, sticky="nsew"
        )

        # Checkbuttons
        row = 0
        self.parent.var_resumen_rend_prov = tk.BooleanVar()
        self.parent.check_resumen_rend_prov = ttk.Checkbutton(
            self.parent.check_frame_sgf, text="Resumen de Rendiciones por Proveedor", 
            variable=self.parent.var_resumen_rend_prov
        )
        self.parent.check_resumen_rend_prov.grid(row=row, column=0, padx=padx_checkbox, pady=pady_checkbox, sticky="nsew")

        row += 1
        self.parent.var_resumen_rend_obras = tk.BooleanVar()
        self.parent.check_resumen_rend_obras = ttk.Checkbutton(
            self.parent.check_frame_sgf, text="Resumen de Rendiciones por Obra", 
            variable=self.parent.var_resumen_rend_obras
        )
        self.parent.check_resumen_rend_obras.grid(row=row, column=0, padx=padx_checkbox, pady=pady_checkbox, sticky="nsew")

        row += 1
        self.parent.var_certificados_obras = tk.BooleanVar()
        self.parent.check_certificados_obras = ttk.Checkbutton(
            self.parent.check_frame_sgf, text="Certificados de Obras", 
            variable=self.parent.var_certificados_obras
        )
        self.parent.check_certificados_obras.grid(row=row, column=0, padx=padx_checkbox, pady=pady_checkbox, sticky="nsew")

        row += 1
        self.parent.var_listado_prov = tk.BooleanVar()
        self.parent.check_listado_prov = ttk.Checkbutton(
            self.parent.check_frame_sgf, text="Listado de Proveedores", 
            variable=self.parent.var_listado_prov
        )
        self.parent.check_listado_prov.grid(row=row, column=0, padx=padx_checkbox, pady=pady_checkbox, sticky="nsew")

    def setupSSCCWidgets(
        self, row_frame = None, column_frame:int = None, 
        rowspan_frame:int = None, columnspan_frame:int = None,
        padding_frame:int = None, padx_frame:int = None, pady_frame:int = None,
        padx_checkbox:int = None, pady_checkbox:int = None
    ):
        if row_frame is None:
            row_frame = self.row_frame
        if column_frame is None:
            column_frame = self.column_frame
        if rowspan_frame is None:
            rowspan_frame = self.rowspan_frame
        if columnspan_frame is None:
            columnspan_frame = self.columnspan_frame
        if padding_frame is None:
            padding_frame = self.padding_frame    
        if padx_frame is None:
            padx_frame = self.padx_frame
        if pady_frame is None:
            pady_frame = self.pady_frame
        if padx_checkbox is None:
            padx_checkbox = self.padx_checkbox
        if pady_checkbox is None:
            pady_checkbox = self.pady_checkbox

        # Create a Frame for SGV
        self.parent.check_frame_sscc = ttk.LabelFrame(self.parent, text="Sistema de Seguimiento de Ctas Ctes (SSCC)", padding=padding_frame)
        self.parent.check_frame_sscc.grid(
            row=row_frame, column=column_frame, padx=padx_frame, pady=pady_frame, sticky="nsew",
            rowspan=rowspan_frame, columnspan=columnspan_frame
        )

        # Checkbuttons
        row = 0
        self.parent.var_ctas_ctes = tk.BooleanVar()
        self.parent.check_ctas_ctes = ttk.Checkbutton(
            self.parent.check_frame_sscc, text="Listado de Cuentas Corrientes (Manual)", 
            variable=self.parent.var_ctas_ctes
        )
        self.parent.check_ctas_ctes.grid(row=row, column=0, padx=padx_checkbox, pady=pady_checkbox, sticky="nsew")

        row += 1
        self.parent.var_banco_invico = tk.BooleanVar()
        self.parent.check_banco_invico = ttk.Checkbutton(
            self.parent.check_frame_sscc, text="Consulta General de Movimientos", 
            variable=self.parent.var_banco_invico
        )
        self.parent.check_banco_invico.grid(row=row, column=0, padx=padx_checkbox, pady=pady_checkbox, sticky="nsew")

        row += 1
        self.parent.var_sdo_final_banco_invico = tk.BooleanVar()
        self.parent.check_sdo_final_banco_invico = ttk.Checkbutton(
            self.parent.check_frame_sscc, text="Saldo Final Banco INVICO (Manual)", 
            variable=self.parent.var_sdo_final_banco_invico
        )
        self.parent.check_sdo_final_banco_invico.grid(row=row, column=0, padx=padx_checkbox, pady=pady_checkbox, sticky="nsew")

    def setupSistemaRecuperosWidgets(
        self, row_frame = None, column_frame:int = None, 
        rowspan_frame:int = None, columnspan_frame:int = None,
        padding_frame:int = None, padx_frame:int = None, pady_frame:int = None,
        padx_checkbox:int = None, pady_checkbox:int = None
    ):
        if row_frame is None:
            row_frame = self.row_frame
        if column_frame is None:
            column_frame = self.column_frame
        if rowspan_frame is None:
            rowspan_frame = self.rowspan_frame
        if columnspan_frame is None:
            columnspan_frame = self.columnspan_frame
        if padding_frame is None:
            padding_frame = self.padding_frame    
        if padx_frame is None:
            padx_frame = self.padx_frame
        if pady_frame is None:
            pady_frame = self.pady_frame
        if padx_checkbox is None:
            padx_checkbox = self.padx_checkbox
        if pady_checkbox is None:
            pady_checkbox = self.pady_checkbox

        # Create a Frame for SGV
        self.parent.check_frame_recuperos = ttk.LabelFrame(self.parent, text="Sistema Recuperos", padding=padding_frame)
        self.parent.check_frame_recuperos.grid(
            row=row_frame, column=column_frame, padx=padx_frame, pady=pady_frame, sticky="nsew",
            rowspan=rowspan_frame, columnspan=columnspan_frame
        )

        # Checkbuttons
        row = 0
        self.parent.var_saldo_barrio = tk.BooleanVar()
        self.parent.check_saldo_barrio = ttk.Checkbutton(
            self.parent.check_frame_recuperos, text="Saldos por Barrio", 
            variable=self.parent.var_saldo_barrio
        )
        self.parent.check_saldo_barrio.grid(row=row, column=0, padx=padx_checkbox, pady=pady_checkbox, sticky="nsew")

        row += 1
        self.parent.var_saldo_barrio_variacion = tk.BooleanVar()
        self.parent.check_saldo_barrio_variacion = ttk.Checkbutton(
            self.parent.check_frame_recuperos, text="Evolución de Saldos por Barrio", 
            variable=self.parent.var_saldo_barrio_variacion
        )
        self.parent.check_saldo_barrio_variacion.grid(row=row, column=0, padx=padx_checkbox, pady=pady_checkbox, sticky="nsew")

        row += 1
        self.parent.var_saldo_recuperos_cobrar_variacion = tk.BooleanVar()
        self.parent.check_saldo_recuperos_cobrar_variacion = ttk.Checkbutton(
            self.parent.check_frame_recuperos, text="Variación de Saldos Recuperos a Cobrar", 
            variable=self.parent.var_saldo_recuperos_cobrar_variacion
        )
        self.parent.check_saldo_recuperos_cobrar_variacion.grid(row=row, column=0, padx=padx_checkbox, pady=pady_checkbox, sticky="nsew")

        row += 1
        self.parent.var_saldo_motivo = tk.BooleanVar()
        self.parent.check_saldo_motivo = ttk.Checkbutton(
            self.parent.check_frame_recuperos, text="Evolución de Saldos por Motivos", 
            variable=self.parent.var_saldo_motivo
        )
        self.parent.check_saldo_motivo.grid(row=row, column=0, padx=padx_checkbox, pady=pady_checkbox, sticky="nsew")

        row += 1
        self.parent.var_saldo_motivo_por_barrio = tk.BooleanVar()
        self.parent.check_saldo_motivo_por_barrio = ttk.Checkbutton(
            self.parent.check_frame_recuperos, text="Evolución de Saldos por Motivos por Barrio", 
            variable=self.parent.var_saldo_motivo_por_barrio
        )
        self.parent.check_saldo_motivo_por_barrio.grid(row=row, column=0, padx=padx_checkbox, pady=pady_checkbox, sticky="nsew")

        row += 1
        self.parent.var_barrios_nuevos= tk.BooleanVar()
        self.parent.check_barrios_nuevos = ttk.Checkbutton(
            self.parent.check_frame_recuperos, text="Barrios Nuevos Incorporados", 
            variable=self.parent.var_barrios_nuevos
        )
        self.parent.check_barrios_nuevos.grid(row=row, column=0, padx=padx_checkbox, pady=pady_checkbox, sticky="nsew")

        row += 1
        self.parent.var_resumen_facturado = tk.BooleanVar()
        self.parent.check_resumen_facturado = ttk.Checkbutton(
            self.parent.check_frame_recuperos, text="Resumen Facturado", 
            variable=self.parent.var_resumen_facturado
        )
        self.parent.check_resumen_facturado.grid(row=row, column=0, padx=padx_checkbox, pady=pady_checkbox, sticky="nsew")

        row += 1
        self.parent.var_resumen_recaudado = tk.BooleanVar()
        self.parent.check_resumen_recaudado = ttk.Checkbutton(
            self.parent.check_frame_recuperos, text="Resumen Recaudado", 
            variable=self.parent.var_resumen_recaudado
        )
        self.parent.check_resumen_recaudado.grid(row=row, column=0, padx=padx_checkbox, pady=pady_checkbox, sticky="nsew")

    def setupSistemasPropiosWidgets(
        self, row_frame = None, column_frame:int = None, 
        rowspan_frame:int = None, columnspan_frame:int = None,
        padding_frame:int = None, padx_frame:int = None, pady_frame:int = None,
        padx_checkbox:int = None, pady_checkbox:int = None
    ):
        if row_frame is None:
            row_frame = self.row_frame
        if column_frame is None:
            column_frame = self.column_frame
        if rowspan_frame is None:
            rowspan_frame = self.rowspan_frame
        if columnspan_frame is None:
            columnspan_frame = self.columnspan_frame
        if padding_frame is None:
            padding_frame = self.padding_frame    
        if padx_frame is None:
            padx_frame = self.padx_frame
        if pady_frame is None:
            pady_frame = self.pady_frame
        if padx_checkbox is None:
            padx_checkbox = self.padx_checkbox
        if pady_checkbox is None:
            pady_checkbox = self.pady_checkbox

        # Create a Frame for SGV
        self.parent.check_frame_propios = ttk.LabelFrame(self.parent, text="Sistemas de Propios", padding=padding_frame)
        self.parent.check_frame_propios.grid(
            row=row_frame, column=column_frame, padx=padx_frame, pady=pady_frame, sticky="nsew",
            rowspan=rowspan_frame, columnspan=columnspan_frame
        )

        # Checkbuttons
        self.parent.var_icaro = tk.BooleanVar()
        self.parent.check_icaro = ttk.Checkbutton(
            self.parent.check_frame_propios, text="Icaro", 
            variable=self.parent.var_icaro
        )
        # self.check_icaro.pack(fill = 'x', side='left', pady=(20, 10))
        self.parent.check_icaro.grid(row=0, column=0, padx=5, pady=10, sticky="nsew")

        self.parent.var_saihp = tk.BooleanVar()
        self.parent.check_saihp = ttk.Checkbutton(
            self.parent.check_frame_propios, text="Sist Automático de Imputación de Hon.", 
            variable=self.parent.var_saihp
        )
        # self.check_saihp.pack(fill = 'x', side='right', pady=(20, 10))
        self.parent.check_saihp.grid(row=0, column=1, padx=5, pady=10, sticky="nsew")