#!/usr/bin/env python3
"""
Author: Fernando Corrales <fscorrales@gmail.com>
Purpose: Upload set of INVICO DB' sqlite files to Google Sheets
Packages:
 - invicodatpy (pip install -e '/home/kanou/IT/R Apps/R Gestion INVICO/invicodatpy')
"""
import argparse
import datetime as dt
import os
import time
from dataclasses import dataclass, field

import pandas as pd

from invicoctrlpy.banco.flujo_caja import FlujoCaja
from invicoctrlpy.gastos.control_debitos_bancarios.control_debitos_bancarios import \
    ControlDebitosBancarios
from invicoctrlpy.gastos.control_escribanos.control_escribanos import \
    ControlEscribanos
from invicoctrlpy.gastos.control_haberes.control_haberes import ControlHaberes
from invicoctrlpy.gastos.control_honorarios.control_honorarios import \
    ControlHonorarios
from invicoctrlpy.gastos.control_obras.control_obras import ControlObras
from invicoctrlpy.gastos.control_obras.listado_obras import ListadoObras
from invicoctrlpy.gastos.control_retenciones.control_retenciones import \
    ControlRetenciones
from invicoctrlpy.gastos.ejecucion_gastos.ejecucion_gastos import \
    EjecucionGastos
from invicoctrlpy.gastos.ejecucion_obras import EjecucionObras
from invicoctrlpy.gastos.fondos_perm_cajas_chicas.fondos_perm_cajas_chicas import \
    FondosPermCajasChicas
from invicoctrlpy.icaro.icaro_vs_siif.icaro_vs_siif import IcaroVsSIIF
from invicoctrlpy.recursos.aporte_empresario.aporte_empresario import \
    ControlAporteEmpresario
from invicoctrlpy.recursos.control_recursos.control_recursos import \
    ControlRecursos
from invicodatpy.utils.google_sheets import GoogleSheets

from ..hangling_path import HanglingPath


# --------------------------------------------------
@dataclass
class UploadGoogleSheet():
    """Upload DataFrame to Google Sheets
    :param path_credentials_file: json file download from Google
    :param input_path: If update_db is True '/Base de Datos' path must be given
    :param output_path: If update_db is True 'Python Output/SQLite Files' must be given
    """
    path_credentials_file:str
    ejercicio:str = str(dt.datetime.now().year)
    # update_db:bool = False
    input_path:str = None
    output_path:str = None
    gs:GoogleSheets = field(init=False, repr=False)
    df:pd.DataFrame = field(init=False, repr=False)

    # --------------------------------------------------
    def __post_init__(self):
        # if self.input_path == None or self.output_path == None:
        #     self.update_db = False
        self.gs = GoogleSheets(path_credentials_file=self.path_credentials_file)

    # --------------------------------------------------
    def upload_all_dfs(self):
        """Update and Upload all DataFrames
        Update requires:
            - Icaro
            - SIIF rfp_p605b
            - SIIF rf602
            - SIIF rf610
            - SIIF gto_rpa03g
            - SIIF rcg01_uejp
            - SIIF rdeu012
            - SIIF rfondo07tp
            - SIIF rci02
            - SIIF rog01
            - SIIF rcocc31 (
                2111-1-2 Contratistas
                2122-1-2 Retenciones
                1112-2-6 Banco)
            - SGF Resumen Rend por Proveedor
            - SSCC Resumen General de Movimientos
            - SSCC ctas_ctes (manual data)
        """
        ejercicio_actual = str(dt.datetime.now().year)
        ejercicio_anterior = str(dt.datetime.now().year - 1)
        ejercicio_siguiente = str(dt.datetime.now().year + 1)
        ejercicios_varios = range(int(ejercicio_actual)-5, int(ejercicio_actual)+1)
        ejercicios_varios = [str(x) for x in ejercicios_varios]
        self.upload_formulacion_presupuesto(ejercicio_actual)
        self.upload_formulacion_gtos([ejercicio_actual, ejercicio_siguiente])
        #Incluyo menos años porque es muy lento Google Sheet
        self.upload_ejecucion_gtos(range(int(ejercicio_actual)-3, int(ejercicio_actual)+1))
        self.upload_ejecucion_pres()
        self.upload_planillometro()
        self.upload_ejecucion_obras_fondos_prov(ejercicios_varios)
        self.upload_fondos_perm_cajas_chicas(ejercicios_varios)
        self.upload_control_icaro(ejercicios_varios)
        # self.upload_comprobantes_gastos()
        self.upload_control_recursos(ejercicios_varios)
        time.sleep(120)
        self.upload_flujo_caja(ejercicios_varios)
        self.upload_control_obras(ejercicios_varios)
        self.upload_listado_obras()
        self.upload_control_haberes([ejercicio_actual, ejercicio_anterior])
        self.upload_control_retenciones([ejercicio_actual, ejercicio_anterior])
        self.upload_control_escribanos([ejercicio_actual, ejercicio_anterior])
        self.upload_control_honorarios([ejercicio_actual, ejercicio_anterior])
        self.upload_control_debitos_bancarios([ejercicio_actual, ejercicio_anterior])
        self.upload_control_3_porciento_invico([ejercicio_actual, ejercicio_anterior])

    # NO IMPLEMENTADO AÚN
    # --------------------------------------------------
    def upload_dbs(self, ejercicio:str = None):
        """Update and Upload Formulacion Gastos
        Update requires:
            - SSCC
            - SSCC Ctas Ctes (manual data)
        """
        if ejercicio is None:
            ejercicio_metodo = self.ejercicio
        else:
            ejercicio_metodo = ejercicio

        db = FlujoCaja(
            input_path=self.input_path, db_path=self.output_path,
            # update_db= self.update_db, 
            ejercicio=ejercicio_metodo
        )

        # DB SSCC
        self.df = db.import_banco_invico()
        self.df = self.df.fillna('')
        self.df['fecha'] = self.df['fecha'].dt.strftime('%d-%m-%Y')
        spreadsheet_key = '1rJSM9_duCVWDyw9RrfFCc4vrUKqeFv-MynxoC-atez4'
        wks_name = 'sscc'
        self.gs.to_google_sheets(
            self.df,  
            spreadsheet_key = spreadsheet_key,
            wks_name = wks_name
        )
        print('-- DB SSCC --')
        print(self.df.head())

    # --------------------------------------------------
    def upload_formulacion_presupuesto(self, ejercicio:str = None):
        """Update and Upload Formulacion Presupuesto
            - SIIF rf602
            - SIIF rf610
            - SIIF ri102
            - SIIF rfp_p605b
            - ICARO
        """
        if ejercicio is None:
            ejercicio_metodo = self.ejercicio
        else:
            ejercicio_metodo = ejercicio

        ejecucion_obras = EjecucionObras(
            input_path=self.input_path, db_path=self.output_path,
            # update_db= self.update_db, 
            ejercicio=ejercicio_metodo
        )

        # Formulación Gastos SIIF
        self.df = ejecucion_obras.reporte_planillometro_contabilidad(
            ultimos_ejercicios = '2',
            es_desc_siif = False,
            incluir_desc_subprog = True,
            date_up_to = dt.date(int(ejercicio_metodo), 8, 31),
            include_pa6 = True,
        )
        self.df['ejercicio'] = self.df['ejercicio'].astype(int)
        spreadsheet_key = '1hJyBOkA8sj5otGjYGVOzYViqSpmv_b4L8dXNju_GJ5Q'
        wks_name = 'planillometro_contabilidad'
        self.gs.to_google_sheets(
            self.df,  
            spreadsheet_key = spreadsheet_key,
            wks_name = wks_name
        )
        print('-- Planillometro Contabilidad para Formulación --')
        print(self.df.head())

        
        ejercicios_varios = range(
            int(ejercicio_metodo) - 2, 
            int(ejercicio_metodo) + 2 #Para incluir el año siguiente (Formulación)
        )
        ejercicios_varios = [str(x) for x in ejercicios_varios]

        # Ejecucion Gastos SIIF
        ejecucion_gastos = EjecucionGastos(
            input_path=self.input_path, db_path=self.output_path,
            # update_db= self.update_db, 
            ejercicio=ejercicios_varios
        )

        self.df = ejecucion_gastos.import_siif_gtos_desc()
        self.df.loc[self.df['programa'] == 11, 'desc_prog'] = '11 - CONSTR. DE VIVIENDAS C/EQUIPAMIENTO COMUNITARIOS'
        self.df['fuente'] = self.df['fuente'].astype(int)
        spreadsheet_key = '1hJyBOkA8sj5otGjYGVOzYViqSpmv_b4L8dXNju_GJ5Q'
        wks_name = 'siif_ejec_gastos'
        self.gs.to_google_sheets(
            self.df,  
            spreadsheet_key = spreadsheet_key,
            wks_name = wks_name
        )
        print('-- Ejecucion Gastos SIIF --')
        print(self.df.head())

        # Formulación Gastos SIIF
        self.df = ejecucion_gastos.import_siif_rfp_p605b()
        spreadsheet_key = '1hJyBOkA8sj5otGjYGVOzYViqSpmv_b4L8dXNju_GJ5Q'
        wks_name = 'siif_carga_form_gastos'
        self.gs.to_google_sheets(
            self.df,  
            spreadsheet_key = spreadsheet_key,
            wks_name = wks_name
        )
        print('-- Formulación Gastos SIIF --')
        print(self.df.head())


        # SIIF Recursos Anual por Código
        control_recursos = ControlRecursos(
            input_path=self.input_path, db_path=self.output_path,
            # update_db= self.update_db, 
            ejercicio=ejercicios_varios
        )

        self.df = control_recursos.import_siif_ri102()
        self.df = self.df.fillna('')
        spreadsheet_key = '1hJyBOkA8sj5otGjYGVOzYViqSpmv_b4L8dXNju_GJ5Q'
        wks_name = 'siif_recursos_cod'
        self.gs.to_google_sheets(
            self.df,  
            spreadsheet_key = spreadsheet_key,
            wks_name = wks_name
        )
        print('-- SIIF Recursos Anual por Código --')
        print(self.df.head())


    # --------------------------------------------------
    def upload_formulacion_gtos(self, ejercicio:str = None):
        """Update and Upload Formulacion Gastos
        Update requires:
            - SIIF rfp_p605b
            - SIIF rf602
            - SIIF rf610
            - SIIF gto_rpa03g
            - SIIF rcg01_uejp
        """
        if ejercicio is None:
            ejercicio_metodo = self.ejercicio
        else:
            ejercicio_metodo = ejercicio

        ejecucion_gastos = EjecucionGastos(
            input_path=self.input_path, db_path=self.output_path,
            # update_db= self.update_db, 
            ejercicio=ejercicio_metodo
        )

        # Formulación Gastos SIIF
        self.df = ejecucion_gastos.import_siif_rfp_p605b()
        spreadsheet_key = '1SRmgep84KGJNj_nKxiwXLe28gVUiIu2Uha4j_C7BzeU'
        wks_name = 'siif_form_gastos'
        self.gs.to_google_sheets(
            self.df,  
            spreadsheet_key = spreadsheet_key,
            wks_name = wks_name
        )
        print('-- Formulación Gastos SIIF --')
        print(self.df.head())

    # --------------------------------------------------
    def upload_ejecucion_gtos(self, ejercicio:str = None):
        """Update and Upload Ejecucion Gastos
        Update requires:
            - SIIF rf602
            - SIIF rf610
            - SIIF gto_rpa03g
            - SIIF rcg01_uejp
            - SIIF rfp_p605b (no obligatorio)
            - SSCC Ctas Ctes (manual data)
        """
        if ejercicio is None:
            ejercicio_metodo = self.ejercicio
        else:
            ejercicio_metodo = ejercicio

        ejecucion_gastos = EjecucionGastos(
            input_path=self.input_path, db_path=self.output_path,
            # update_db= self.update_db, 
            ejercicio=ejercicio_metodo
        )

        # Ejecucion Gastos SIIF
        self.df = ejecucion_gastos.import_siif_gtos_desc()
        spreadsheet_key = '1SRmgep84KGJNj_nKxiwXLe28gVUiIu2Uha4j_C7BzeU'
        wks_name = 'siif_ejec_gastos'
        self.gs.to_google_sheets(
            self.df,  
            spreadsheet_key = spreadsheet_key,
            wks_name = wks_name
        )
        print('-- Ejecucion Gastos SIIF --')
        print(self.df.head())

        # CAMBIÉ A OTRO ARCHIVO (Comprobantes Gastos)
        # Comprobantes Gastos SIIF
        self.df = ejecucion_gastos.import_siif_comprobantes()
        self.df['fecha'] = self.df['fecha'].dt.strftime('%d-%m-%Y')
        self.df = self.df.fillna('')
        spreadsheet_key = '1Ox1YXlCEQZtHCTefZUSYdd-hpu71Z6poqq0XlPoNf2A'
        wks_name = 'siif_gastos'
        self.gs.to_google_sheets(
            self.df,  
            spreadsheet_key = spreadsheet_key,
            wks_name = wks_name
        )
        print('-- Comprobantes Gastos SIIF --')
        print(self.df.head())

    # --------------------------------------------------
    def upload_ejecucion_pres(self):
        """Update and Upload Ejecucion Presupuestaria
        Update requires:
            - SIIF rf602
            - SIIF rf610
            - Icaro
        """
        ejecucion_obras = EjecucionObras(
            input_path=self.input_path, db_path=self.output_path,
            # update_db= self.update_db, 
            ejercicio=self.ejercicio
        )

        # Ejecucion Obras SIIF
        self.df = ejecucion_obras.import_siif_ppto_gto_con_desc()
        spreadsheet_key = '1SRmgep84KGJNj_nKxiwXLe28gVUiIu2Uha4j_C7BzeU'
        wks_name = 'siif_ejec_obras'
        self.gs.to_google_sheets(
            self.df,  
            spreadsheet_key = spreadsheet_key,
            wks_name = wks_name
        )
        print('-- Ejecucion Obras SIIF --')
        print(self.df.head())

        # Ejecucion Obras SIIF con Descripcion Unificada
        self.df = ejecucion_obras.import_siif_obras_desc()
        spreadsheet_key = '1SRmgep84KGJNj_nKxiwXLe28gVUiIu2Uha4j_C7BzeU'
        wks_name = 'siif_ejec_obras_desc_unif'
        self.gs.to_google_sheets(
            self.df,  
            spreadsheet_key = spreadsheet_key,
            wks_name = wks_name
        )
        print('-- Ejecucion Obras SIIF con Descripcion Unificada --')
        print(self.df.head())

        # Ejecucion Icaro
        self.df = ejecucion_obras.import_icaro_carga_desc(es_desc_siif=False)
        self.df['estructura'] = self.df['actividad'] + '-' + self.df['partida']
        self.df = self.df.groupby([
            'ejercicio', 'estructura', 'fuente',
            'desc_prog', 'desc_subprog', 'desc_proy', 'desc_act',
            'obra'
        ]).importe.sum().to_frame()
        self.df.reset_index(drop=False, inplace=True)
        spreadsheet_key = '1SRmgep84KGJNj_nKxiwXLe28gVUiIu2Uha4j_C7BzeU'
        wks_name = 'icaro'
        self.gs.to_google_sheets(
            self.df,  
            spreadsheet_key = spreadsheet_key,
            wks_name = wks_name
        )
        print('-- Ejecucion Icaro --')
        print(self.df.head())

        # Ejecucion Modulos Basicos Icaro
        self.df = ejecucion_obras.import_icaro_mod_basicos(
            es_desc_siif=True, neto_reg=False, neto_pa6=False
        )
        self.df['fecha'] = self.df['fecha'].dt.strftime('%d-%m-%Y')
        self.df = self.df.fillna('')
        spreadsheet_key = '195qPSga7cU1kx3z2-gadEWNC2eupdkbR-rb-O8SPWuA'
        wks_name = 'mod_basicos'
        self.gs.to_google_sheets(
            self.df,  
            spreadsheet_key = spreadsheet_key,
            wks_name = wks_name
        )
        print('-- Ejecucion Modulos Básicos --')
        print(self.df.head())

    # --------------------------------------------------
    def upload_ejecucion_obras_fondos_prov(self, ejercicio:list = None):
        """Update and Upload Ejecucion Obras Fondos Prov
        Update requires:
            - SIIF rf602
            - SIIF rf610
            - Icaro
        """
        if ejercicio is None:
            ejercicio = self.ejercicio
        ejecucion_obras = EjecucionObras(
            input_path=self.input_path, db_path=self.output_path,
            # update_db= self.update_db, 
            ejercicio=ejercicio
        )

        # Ejecucion Obras SIIF con Descripcion Unificada
        self.df = ejecucion_obras.import_siif_obras_desc()
        self.df = self.df.loc[self.df['fuente'] != '11']
        self.df = self.df.fillna('')
        spreadsheet_key = '1oB0B2Z0SKL3RVXkgENAcfd4-zXte2geTZtpmTxOj_tg'
        wks_name = 'siif_ejec_obras_desc_unif'
        self.gs.to_google_sheets(
            self.df,  
            spreadsheet_key = spreadsheet_key,
            wks_name = wks_name
        )
        print('-- Ejecucion Obras SIIF con Descripcion Unificada --')
        print(self.df.head())

        # Ejecucion Icaro
        self.df = ejecucion_obras.import_icaro_carga_desc(es_desc_siif=False)
        self.df = self.df.loc[self.df['fuente'] != '11']
        self.df = self.df.fillna('')
        self.df['fecha'] = self.df['fecha'].dt.strftime('%d-%m-%Y')
        self.df['estructura'] = self.df['actividad'] + '-' + self.df['partida']
        # self.df = self.df.groupby([
        #     'ejercicio', 'estructura', 'fuente',
        #     'desc_prog', 'desc_subprog', 'desc_proy', 'desc_act',
        #     'obra', 'proveedor'
        # ]).importe.sum().to_frame()
        
        self.df.reset_index(drop=True, inplace=True)
        spreadsheet_key = '1oB0B2Z0SKL3RVXkgENAcfd4-zXte2geTZtpmTxOj_tg'
        wks_name = 'icaro'
        self.gs.to_google_sheets(
            self.df,  
            spreadsheet_key = spreadsheet_key,
            wks_name = wks_name
        )
        print('-- Ejecucion Icaro --')
        print(self.df.head())

    # --------------------------------------------------
    def upload_planillometro(self, ejercicio:str = None):
        """Update and Upload Ejecucion Presupuestaria
        Update requires:
            - SIIF rf602
            - SIIF rf610
            - Icaro
        """
        if ejercicio is None:
            ejercicio_metodo = self.ejercicio
        else:
            ejercicio_metodo = ejercicio

        ejecucion_obras = EjecucionObras(
            input_path=self.input_path, db_path=self.output_path,
            # update_db= self.update_db, 
            ejercicio=ejercicio_metodo
        )

        # Planillometro SIIF
        self.df = ejecucion_obras.reporte_planillometro(full_icaro=False, es_desc_siif=True)
        spreadsheet_key = '1DPn8eEVDyD9Ug6r03fIMGoK4NPxHsWD2a_3qITzPAIs'
        wks_name = 'planillometro_siif'
        self.gs.to_google_sheets(
            self.df,  
            spreadsheet_key = spreadsheet_key,
            wks_name = wks_name
        )
        print('-- Planillometro SIIF --')
        print(self.df.head())

        # Planillometro SIIF desc ICARO sin fuente
        self.df = ejecucion_obras.reporte_planillometro(
            full_icaro=False, es_desc_siif=False, desagregar_fuente=False
        )
        spreadsheet_key = '1DPn8eEVDyD9Ug6r03fIMGoK4NPxHsWD2a_3qITzPAIs'
        wks_name = 'planillometro_siif_sin_fte'
        self.gs.to_google_sheets(
            self.df,  
            spreadsheet_key = spreadsheet_key,
            wks_name = wks_name
        )
        print('-- Planillometro SIIF sin fuente --')
        print(self.df.head())


        # Planillometro Icaro
        self.df = ejecucion_obras.reporte_planillometro(full_icaro=True, es_desc_siif=False)
        spreadsheet_key = '1DPn8eEVDyD9Ug6r03fIMGoK4NPxHsWD2a_3qITzPAIs'
        wks_name = 'planillometro_icaro'
        self.gs.to_google_sheets(
            self.df,  
            spreadsheet_key = spreadsheet_key,
            wks_name = wks_name
        )
        print('-- Planillometro Icaro --')
        print(self.df.head())

        # Planillometro Icaro para Contabilidad
        self.df = ejecucion_obras.reporte_planillometro_contabilidad(
            ultimos_ejercicios = '5',
            es_desc_siif = False
        )
        self.df['ejercicio'] = self.df['ejercicio'].astype(int)
        spreadsheet_key = '1Hmb7xmzhZBoicnL5_tN7mr1kOj-r3gw8lCkPErR8Xd4'
        wks_name = 'bd_planillometro'
        self.gs.to_google_sheets(
            self.df,  
            spreadsheet_key = spreadsheet_key,
            wks_name = wks_name
        )
        print('-- Planillometro Icaro para Contabilidad --')
        print(self.df.head())

        # Variación Saldo por Barrio Recuperos
        self.df = ejecucion_obras.import_saldo_barrio_variacion() #no me cierra mucho
        spreadsheet_key = '1Hmb7xmzhZBoicnL5_tN7mr1kOj-r3gw8lCkPErR8Xd4'
        wks_name = 'bd_recuperos'
        self.gs.to_google_sheets(
            self.df,  
            spreadsheet_key = spreadsheet_key,
            wks_name = wks_name
        )
        print('-- Variación Saldo por Barrio Recuperos --')
        print(self.df.head())

    # --------------------------------------------------
    def upload_control_icaro(self, ejercicio:str = None):
        """Update and Upload Control Icaro
        Update requires:
            - Icaro
            - SIIF rf602
            - SIIF gto_rpa03g
            - SIIF rcg01_uejp
            - SIIF rfondo07tp
            - SSCC ctas_ctes (manual data)
        """

        if ejercicio is None:
            ejercicio_metodo = self.ejercicio
        else:
            ejercicio_metodo = ejercicio

        icaro_vs_siif = IcaroVsSIIF(
            input_path=self.input_path, db_path=self.output_path,
            # update_db= self.update_db, 
            ejercicio=ejercicio_metodo
        )

        # Control Ejecucion Anual
        self.df = icaro_vs_siif.control_ejecucion_anual()
        fields_to_update = ['ejecucion_siif', 'ejecucion_icaro', 'diferencia']
        self.df[fields_to_update] = self.df[fields_to_update].fillna(0)
        self.df = self.df.fillna('')
        spreadsheet_key = '1KKeeoop_v_Nf21s7eFp4sS6SmpxRZQ9DPa1A5wVqnZ0'
        wks_name = 'control_ejecucion_anual_db'
        self.gs.to_google_sheets(
            self.df,
            spreadsheet_key = spreadsheet_key,
            wks_name = wks_name
        )
        print('-- Control Ejecucion Anual --')
        print(self.df.head())

        # Control Comprobantes
        self.df = icaro_vs_siif.control_comprobantes()
        self.df = self.df.fillna('')
        self.df = self.df.astype(str)
        campos = [
            'siif_importe', 'icaro_importe',
        ]
        for campo in campos:
            self.df[campo] = self.df[campo].astype(float)
        spreadsheet_key = '1KKeeoop_v_Nf21s7eFp4sS6SmpxRZQ9DPa1A5wVqnZ0'
        wks_name = 'control_comprobantes_db'
        self.gs.to_google_sheets(
            self.df,
            spreadsheet_key = spreadsheet_key,
            wks_name = wks_name
        )
        print('-- Control Comprobantes SIIF vs Icaro --')
        print(self.df.head())

        # Control PA6
        self.df = icaro_vs_siif.control_pa6()
        self.df = self.df.fillna('')
        self.df = self.df.astype(str)
        campos = [
            'siif_importe_pa6', 'icaro_importe_pa6',
            'siif_importe_reg', 'icaro_importe_reg',
        ]
        for campo in campos:
            self.df[campo] = self.df[campo].astype(float)
        spreadsheet_key = '1KKeeoop_v_Nf21s7eFp4sS6SmpxRZQ9DPa1A5wVqnZ0'
        wks_name = 'control_pa6_db'
        self.gs.to_google_sheets(
            self.df,
            spreadsheet_key = spreadsheet_key,
            wks_name = wks_name
        )
        print('-- Control PA6 --')
        print(self.df.head())

    # --------------------------------------------------
    def upload_comprobantes_gastos(self):
        """Update and Upload Control Icaro
        Update requires:
            - Icaro
            - SIIF rf602
            - SIIF gto_rpa03g
            - SIIF rcg01_uejp
            - SIIF rfondo07tp
            - SSCC ctas_ctes (manual data)
        """
        icaro_vs_siif = IcaroVsSIIF(
            input_path=self.input_path, db_path=self.output_path,
            # update_db= self.update_db, 
            ejercicio=None
        )

        # ICARO Carga
        self.df = icaro_vs_siif.import_icaro_carga()
        self.df['fecha'] = self.df['fecha'].dt.strftime('%d-%m-%Y')
        spreadsheet_key = '175m7DAKoo3T1_26ZwP1ZL-Epts3MAv5XPQNbnQZEcqA'
        wks_name = 'icaro'
        self.gs.to_google_sheets(
            self.df,
            spreadsheet_key = spreadsheet_key,
            wks_name = wks_name
        )
        print('-- ICARO Carga --')
        print(self.df.head())

        # SIIF Comprobantes Gastos
        self.df = icaro_vs_siif.import_siif_comprobantes()
        self.df = self.df.fillna('')
        self.df['fecha'] = self.df['fecha'].dt.strftime('%d-%m-%Y')
        spreadsheet_key = '175m7DAKoo3T1_26ZwP1ZL-Epts3MAv5XPQNbnQZEcqA'
        wks_name = 'siif'
        self.gs.to_google_sheets(
            self.df,
            spreadsheet_key = spreadsheet_key,
            wks_name = wks_name
        )
        print('-- SIIF Comprobantes Gastos --')
        print(self.df.head())

    # --------------------------------------------------
    def upload_control_recursos(self, ejercicio:str = None):
        """Update and Upload Control Recursos
        Update requires:
            - SIIF rci02
            - SIIF ri102
            - SSCC Consulta General de Movimiento
            - SSCC ctas_ctes (manual data)
        """
        if ejercicio is None:
            ejercicio_metodo = self.ejercicio
        else:
            ejercicio_metodo = ejercicio

        control_recursos = ControlRecursos(
            input_path=self.input_path, db_path=self.output_path,
            # update_db= self.update_db, 
            ejercicio=ejercicio_metodo
        )
        # Control Recursos por Mes, Grupo y Cta Cte
        self.df = control_recursos.control_recursos()
        self.df = self.df.fillna('')
        spreadsheet_key = '1u_I5wN3w_rGX6rWIsItXkmwfIEuSox6ZsmKYbMZ2iUY'
        wks_name = 'control_recursos'
        self.gs.to_google_sheets(
            self.df,  
            spreadsheet_key = spreadsheet_key,
            wks_name = wks_name
        )
        print('-- Control Recursos por Mes, Grupo y Cta Cte --')
        print(self.df.head())

        # SIIF Recursos
        self.df = control_recursos.import_siif_rci02()
        self.df = self.df.fillna('')
        self.df['fecha'] = self.df['fecha'].dt.strftime('%d-%m-%Y')
        spreadsheet_key = '1u_I5wN3w_rGX6rWIsItXkmwfIEuSox6ZsmKYbMZ2iUY'
        wks_name = 'siif_recursos'
        self.gs.to_google_sheets(
            self.df,  
            spreadsheet_key = spreadsheet_key,
            wks_name = wks_name
        )
        print('-- SIIF Recursos --')
        print(self.df.head())

        # SIIF Recursos Anual por Código
        self.df = control_recursos.import_siif_ri102()
        self.df = self.df.fillna('')
        spreadsheet_key = '1u_I5wN3w_rGX6rWIsItXkmwfIEuSox6ZsmKYbMZ2iUY'
        wks_name = 'siif_recursos_cod'
        self.gs.to_google_sheets(
            self.df,  
            spreadsheet_key = spreadsheet_key,
            wks_name = wks_name
        )
        print('-- SIIF Recursos Anual por Código --')
        print(self.df.head())

        # SIIF Recursos Agrupado
        self.df = control_recursos.import_siif_rci02()
        self.df = self.df.groupby(
            ['ejercicio', 'mes', 'fuente', 'cta_cte', 'grupo',
            'es_remanente', 'es_invico']
        ).importe.sum().to_frame()
        self.df.reset_index(drop=False, inplace=True)
        spreadsheet_key = '1u_I5wN3w_rGX6rWIsItXkmwfIEuSox6ZsmKYbMZ2iUY'
        wks_name = 'siif_recursos_group'
        self.gs.to_google_sheets(
            self.df,  
            spreadsheet_key = spreadsheet_key,
            wks_name = wks_name
        )
        print('-- SIIF Recursos Agrupado --')
        print(self.df.head())

        # SSCC Banco INVICO
        self.df = control_recursos.import_banco_invico()
        self.df = self.df.fillna('')
        self.df['fecha'] = self.df['fecha'].dt.strftime('%d-%m-%Y')
        spreadsheet_key = '1u_I5wN3w_rGX6rWIsItXkmwfIEuSox6ZsmKYbMZ2iUY'
        wks_name = 'banco_ingresos'
        self.gs.to_google_sheets(
            self.df,  
            spreadsheet_key = spreadsheet_key,
            wks_name = wks_name
        )
        print('-- SSCC Banco INVICO --')
        print(self.df.head())

        # SIIF Banco INVICO Agrupado
        self.df = control_recursos.import_banco_invico()
        self.df = self.df.groupby(
            ['ejercicio', 'mes', 'cta_cte','grupo', 'imputacion']
        ).importe.sum().to_frame()
        self.df.reset_index(drop=False, inplace=True)
        spreadsheet_key = '1u_I5wN3w_rGX6rWIsItXkmwfIEuSox6ZsmKYbMZ2iUY'
        wks_name = 'banco_ingresos_group'
        self.gs.to_google_sheets(
            self.df,  
            spreadsheet_key = spreadsheet_key,
            wks_name = wks_name
        )
        print('-- SIIF Banco INVICO Agrupado --')
        print(self.df.head())

    # --------------------------------------------------
    def upload_flujo_caja(self, ejercicio:str = None):
        """Update and Upload Control Recursos
        Update requires:
            - SSCC Consulta General de Movimiento
            - SSCC ctas_ctes (manual data)
        """
        if ejercicio is None:
            ejercicio_metodo = self.ejercicio
        else:
            ejercicio_metodo = ejercicio

        flujo_caja = FlujoCaja(
            input_path=self.input_path, db_path=self.output_path,
            # update_db= self.update_db, 
            ejercicio=ejercicio_metodo
        )
        # Flujo de Caja desde SSCC INVICO
        self.df = flujo_caja.import_banco_invico()
        self.df = self.df.fillna('')
        self.df['fecha'] = self.df['fecha'].dt.strftime('%d-%m-%Y')
        spreadsheet_key = '1acuIhba9v0DqPt_NwYh73zL9rnHwlfl3h5QD3T75Oo4'
        wks_name = 'bd_banco_invico'
        self.gs.to_google_sheets(
            self.df,  
            spreadsheet_key = spreadsheet_key,
            wks_name = wks_name
        )
        print('-- Flujo de Caja desde SSCC INVICO --')
        print(self.df.head())

    # --------------------------------------------------
    def upload_control_haberes(self, ejercicio:list = None):
        """Update and Upload Control Recursos
        Update requires:
            - SIIF rcg01_uejp
            - SIIF gto_rpa03g
            - SIIF rcocc31 (2122-1-2)
            - SIIF rdeu
            - SSCC Resumen General de Movimientos
            - SSCC ctas_ctes (manual data)
        """
        if ejercicio is None:
            ejercicio = self.ejercicio

        control_haberes = ControlHaberes(
            input_path=self.input_path, db_path=self.output_path,
            # update_db= self.update_db, 
            ejercicio=ejercicio
        )
        # Control Haberes Mensual
        self.df = control_haberes.control_cruzado()
        self.df = self.df.fillna('')
        spreadsheet_key = '1A9ypUkwm4kfLqUAwr6-55crcFElisOO9fOdI6iflMAc'
        wks_name = 'control_mes'
        self.gs.to_google_sheets(
            self.df,  
            spreadsheet_key = spreadsheet_key,
            wks_name = wks_name
        )
        print('-- Control Haberes mensual --')
        print(self.df.head())

        # Comprobantes SIIF de Haberes (rcg01_uejp + gto_rpa03g)
        self.df = control_haberes.siif_comprobantes_haberes_neto_rdeu
        self.df['fecha'] = self.df['fecha'].dt.strftime('%d-%m-%Y')
        self.df = self.df.fillna('')
        spreadsheet_key = '1A9ypUkwm4kfLqUAwr6-55crcFElisOO9fOdI6iflMAc'
        wks_name = 'siif_comprobantes_haberes_db'
        self.gs.to_google_sheets(
            self.df,  
            spreadsheet_key = spreadsheet_key,
            wks_name = wks_name
        )
        print('-- Comprobantes SIIF de Haberes (rcg01_uejp + gto_rpa03g) --')
        print(self.df.head())

        # Deuda Flotante SIIF (rdeu012)
        self.df = control_haberes.siif_rdeu012
        self.df = self.df.fillna('')
        self.df['fecha'] = self.df['fecha'].dt.strftime('%d-%m-%Y')
        self.df['fecha_aprobado'] = self.df['fecha_aprobado'].dt.strftime('%d-%m-%Y')
        self.df['fecha_desde'] = self.df['fecha_desde'].dt.strftime('%d-%m-%Y')
        self.df['fecha_hasta'] = self.df['fecha_hasta'].dt.strftime('%d-%m-%Y')
        spreadsheet_key = '1A9ypUkwm4kfLqUAwr6-55crcFElisOO9fOdI6iflMAc'
        wks_name = 'siif_rdeu_db'
        self.gs.to_google_sheets(
            self.df,  
            spreadsheet_key = spreadsheet_key,
            wks_name = wks_name
        )
        print('-- Deuda Flotante SIIF (rdeu012) --')
        print(self.df.head())

        # Resumen General de Movimentos (Sist. Seg. Ctas. Ctes. INVICO)
        self.df = control_haberes.sscc_banco_invico
        self.df = self.df.fillna('')
        self.df['fecha'] = self.df['fecha'].dt.strftime('%d-%m-%Y')
        spreadsheet_key = '1A9ypUkwm4kfLqUAwr6-55crcFElisOO9fOdI6iflMAc'
        wks_name = 'sscc_haberes_db'
        self.gs.to_google_sheets(
            self.df,  
            spreadsheet_key = spreadsheet_key,
            wks_name = wks_name
        )
        print('-- Resumen General de Movimentos (Sist. Seg. Ctas. Ctes. INVICO) --')
        print(self.df.head())

    # --------------------------------------------------
    def upload_control_retenciones(self, ejercicio:list = None):
        """Update and Upload Control Retenciones
        Update requires:
            - Icaro
            - SIIF rdeu012 (para netear Icaro)
            - SGF Resumen Rend por Proveedor
            - SSCC Resumen General de Movimientos
            - SSCC ctas_ctes (manual data)
            - SIIF rcocc31 (
                2111-1-2 Contratistas
                2122-1-2 Retenciones
                1112-2-6 Banco)
        """
        if ejercicio is None:
            ejercicio = self.ejercicio

        control_retenciones = ControlRetenciones(
            input_path=self.input_path, db_path=self.output_path,
            # update_db= self.update_db, 
            ejercicio=ejercicio
        )

        # Control Cruzado Icaro VS SSCC
        self.df = control_retenciones.icaro_vs_sscc(
            groupby_cols=['ejercicio', 'mes', 'cta_cte']
        )
        spreadsheet_key = '1FQt_TLY5dqZTon-2o71BNHK4uJJ9i9rQVar1E0Te6zM'
        wks_name = 'icaro_vs_sscc_db'
        self.gs.to_google_sheets(
            self.df,  
            spreadsheet_key = spreadsheet_key,
            wks_name = wks_name
        )
        print('-- Control Cruzado Icaro VS SSCC --')
        print(self.df.head())

        # Control Cruzado Icaro VS SGF
        self.df = control_retenciones.icaro_vs_sgf(
            groupby_cols=['ejercicio', 'mes', 'cta_cte', 'cuit']
        )
        spreadsheet_key = '1FQt_TLY5dqZTon-2o71BNHK4uJJ9i9rQVar1E0Te6zM'
        wks_name = 'icaro_vs_sgf_db'
        self.gs.to_google_sheets(
            self.df,  
            spreadsheet_key = spreadsheet_key,
            wks_name = wks_name
        )
        print('-- Control Cruzado Icaro VS SGF --')
        print(self.df.head())

        # Control Cruzado Icaro VS SIIF
        self.df = control_retenciones.icaro_vs_siif()
        spreadsheet_key = '1FQt_TLY5dqZTon-2o71BNHK4uJJ9i9rQVar1E0Te6zM'
        wks_name = 'icaro_vs_siif_db'
        self.gs.to_google_sheets(
            self.df,  
            spreadsheet_key = spreadsheet_key,
            wks_name = wks_name
        )
        print('-- Control Cruzado Icaro VS SIIF --')
        print(self.df.head())

        # Control Cruzado SGF VS SSCC
        self.df = control_retenciones.sgf_vs_sscc()
        spreadsheet_key = '1FQt_TLY5dqZTon-2o71BNHK4uJJ9i9rQVar1E0Te6zM'
        wks_name = 'sgf_vs_sscc_db'
        self.gs.to_google_sheets(
            self.df,  
            spreadsheet_key = spreadsheet_key,
            wks_name = wks_name
        )
        print('-- Control Cruzado SGF VS SSCC --')
        print(self.df.head())

        # Icaro Completo
        self.df = control_retenciones.import_icaro_carga_con_retenciones()
        self.df = self.df.fillna('')
        self.df['fecha'] = self.df['fecha'].dt.strftime('%d-%m-%Y')
        spreadsheet_key = '1FQt_TLY5dqZTon-2o71BNHK4uJJ9i9rQVar1E0Te6zM'
        wks_name = 'icaro_db'
        self.gs.to_google_sheets(
            self.df,  
            spreadsheet_key = spreadsheet_key,
            wks_name = wks_name
        )
        print('-- Icaro Completo --')
        print(self.df.head())

        # SGF Completo
        self.df = control_retenciones.import_resumen_rend_cuit()
        self.df = self.df.fillna('')
        self.df['fecha'] = self.df['fecha'].dt.strftime('%d-%m-%Y')
        spreadsheet_key = '1FQt_TLY5dqZTon-2o71BNHK4uJJ9i9rQVar1E0Te6zM'
        wks_name = 'sgf_db'
        self.gs.to_google_sheets(
            self.df,  
            spreadsheet_key = spreadsheet_key,
            wks_name = wks_name
        )
        print('-- SGF Completo --')
        print(self.df.head())

        # SSCC Completo
        self.df = control_retenciones.import_banco_invico()
        spreadsheet_key = '1FQt_TLY5dqZTon-2o71BNHK4uJJ9i9rQVar1E0Te6zM'
        self.df = self.df.fillna('')
        self.df['fecha'] = self.df['fecha'].dt.strftime('%d-%m-%Y')
        wks_name = 'sscc_db'
        self.gs.to_google_sheets(
            self.df,  
            spreadsheet_key = spreadsheet_key,
            wks_name = wks_name
        )
        print('-- SSCC Completo --')
        print(self.df.head())

        # SIIF Resumen
        self.df = control_retenciones.siif_summarize()
        spreadsheet_key = '1FQt_TLY5dqZTon-2o71BNHK4uJJ9i9rQVar1E0Te6zM'
        wks_name = 'siif_resumen_db'
        self.gs.to_google_sheets(
            self.df,  
            spreadsheet_key = spreadsheet_key,
            wks_name = wks_name
        )
        print('-- SIIF Resumen --')
        print(self.df.head())

    # --------------------------------------------------
    def upload_fondos_perm_cajas_chicas(self, ejercicio:list = None):
        """Update and Upload Fondos Permanentes y Cajas Chicas
        Update requires:
            - SIIF rcg01_uejp
            - SIIF gto_rpa03g
            - SIIF rog01 (solo una vez)
            - SSCC ctas_ctes (manual data)
        """
        if ejercicio is None:
            ejercicio = self.ejercicio
        fondos_perm = FondosPermCajasChicas(
            input_path=self.input_path, db_path=self.output_path,
            # update_db= self.update_db, 
            ejercicio=ejercicio
        )

        # Comprobantes SIIF Fondos Permanentes y Cajas Chicas
        self.df = fondos_perm.import_siif_comprobantes_fondos_perm()
        self.df['fecha'] = self.df['fecha'].dt.strftime('%d-%m-%Y')
        self.df = self.df.fillna('')
        spreadsheet_key = '1dF8K5gslpK47jjVgJjd-I6k_2QLV2OSSwJ3Le40sFxc'
        wks_name = 'bd_siif_comprobantes'
        self.gs.to_google_sheets(
            self.df,  
            spreadsheet_key = spreadsheet_key,
            wks_name = wks_name
        )
        print('-- Comprobantes SIIF Fondos Permanentes y Cajas Chicas --')
        print(self.df.head())

    # --------------------------------------------------
    def upload_control_obras(self, ejercicio:list = None):
        """Update and Upload Control Obras
        Update requires:
            - Icaro
            - SIIF rdeu012
            - SGF Resumen de Rendiciones por Proveedor
            - SGF Listado Proveedores
            - SSCC Resumen General de Movimientos
            - SSCC ctas_ctes (manual data)
        """
        if ejercicio is None:
            ejercicio = self.ejercicio
        control_obras = ControlObras(
            input_path=self.input_path, db_path=self.output_path,
            # update_db= self.update_db,
            ejercicio=ejercicio
        )

        # Control Obras por Ejercicio, Mes, Cta. Cte. y CUIT
        self.df = control_obras.control_cruzado(
            groupby_cols=['ejercicio', 'mes', 'cta_cte', 'cuit']
        )
        self.df = self.df.fillna('')
        spreadsheet_key = '16v2ovmQnS1v73-WxTOK6b9Tx9DRugGc70ufpjVi-rPA'
        wks_name = 'control_mes_cta_cte_cuit_db'
        self.gs.to_google_sheets(
            self.df,  
            spreadsheet_key = spreadsheet_key,
            wks_name = wks_name
        )
        print('-- Control Obras por Ejercicio, Mes, Cta. Cte. y CUIT --')
        print(self.df.head())

    # --------------------------------------------------
    def upload_listado_obras(self):
        """Update and Upload Listado Obras
        Update requires:
            - Icaro
            - SGO Listado Obras
        """

        listado_obras = ListadoObras(
            input_path=self.input_path, db_path=self.output_path,
            # update_db= self.update_db
        )

        # Listado de Obras Icaro con Codigo Obras SGO
        self.df = listado_obras.icaroObrasConCodObras()
        self.df = self.df.fillna('')
        spreadsheet_key = '1KnKs7RXzN7QPjNjxkXQY89DWzzGecwcXoPpAYiNRxkU'
        wks_name = 'icaro'
        self.gs.to_google_sheets(
            self.df,  
            spreadsheet_key = spreadsheet_key,
            wks_name = wks_name
        )
        print('-- Listado de Obras Icaro con Codigo Obras SGO --')
        print(self.df.head())

        # Listado de Obras SGO con Imnputacion SIIF
        self.df = listado_obras.sgoObrasConImputacion()
        self.df['fecha_inicio'] = self.df['fecha_inicio'].dt.strftime('%d-%m-%Y')
        self.df['fecha_fin'] = self.df['fecha_fin'].dt.strftime('%d-%m-%Y')
        self.df = self.df.fillna('')
        self.df = self.df.loc[:, [
            'imputacion','cod_obra', 'obra', 
            'contratista', 'localidad', 'tipo_obra',
            'operatoria', 
            'fecha_inicio', 'fecha_fin', 
            'avance_fis_real',
            'nro_ultimo_certif', 'mes_obra_certif', 'monto_pagado', 
        ]]  
        # to_numeric_cols = [
        #     'avance_fis_real'
        # ]
        # self.df[to_numeric_cols] = self.df[to_numeric_cols].apply(lambda x: x.round(4))
        spreadsheet_key = '1KnKs7RXzN7QPjNjxkXQY89DWzzGecwcXoPpAYiNRxkU'
        wks_name = 'sistema_gestion_obras'
        self.gs.to_google_sheets(
            self.df,  
            spreadsheet_key = spreadsheet_key,
            wks_name = wks_name
        )
        print('-- Listado de Obras SGO con Imnputacion SIIF --')
        print(self.df.head())

    # --------------------------------------------------
    def upload_control_escribanos(self, ejercicio:list = None):
        """Update and Upload Control Obras
        Update requires:
            - SGF Resumen Rend por Proveedor
            - SSCC Resumen General de Movimientos
            - SSCC ctas_ctes (manual data)
            - SIIF rcocc31 (2113-2-9 Escribanos)
        """
        if ejercicio is None:
            ejercicio = self.ejercicio
        control_escribanos = ControlEscribanos(
            input_path=self.input_path, db_path=self.output_path,
            # update_db= self.update_db, 
            ejercicio=ejercicio
        )

        # Control Escribanos SIIF vs SGF
        self.df = control_escribanos.siif_vs_sgf()
        self.df = self.df.fillna('')
        spreadsheet_key = '1Tz3uvUGBL8ZDSFsYRBP8hgIis-hlhs_sQ6V5bI4LaTg'
        wks_name = 'siif_vs_sgf_db'
        self.gs.to_google_sheets(
            self.df,  
            spreadsheet_key = spreadsheet_key,
            wks_name = wks_name
        )
        print('-- Control Escribanos SIIF vs SGF --')
        print(self.df.head())

        # Control Escribanos SGF vs SSCC
        self.df = control_escribanos.sgf_vs_sscc()
        self.df = self.df.fillna('')
        spreadsheet_key = '1Tz3uvUGBL8ZDSFsYRBP8hgIis-hlhs_sQ6V5bI4LaTg'
        wks_name = 'sgf_vs_sscc_db'
        self.gs.to_google_sheets(
            self.df,  
            spreadsheet_key = spreadsheet_key,
            wks_name = wks_name
        )
        print('-- Control Escribanos SGF vs SSCC --')
        print(self.df.head())

        # Control Escribanos SIIF Completo
        self.df = control_escribanos.import_siif_escribanos()
        self.df = self.df.fillna('')
        self.df['fecha'] = self.df['fecha'].dt.strftime('%d-%m-%Y')
        self.df['fecha_aprobado'] = self.df['fecha_aprobado'].dt.strftime('%d-%m-%Y')
        spreadsheet_key = '1Tz3uvUGBL8ZDSFsYRBP8hgIis-hlhs_sQ6V5bI4LaTg'
        wks_name = 'siif_db'
        self.gs.to_google_sheets(
            self.df,  
            spreadsheet_key = spreadsheet_key,
            wks_name = wks_name
        )
        print('-- Control Escribanos SIIF Completo --')
        print(self.df.head())

        # Control Escribanos SGF Completo
        self.df = control_escribanos.import_resumen_rend_cuit()
        self.df = self.df.fillna('')
        self.df['fecha'] = self.df['fecha'].dt.strftime('%d-%m-%Y')
        spreadsheet_key = '1Tz3uvUGBL8ZDSFsYRBP8hgIis-hlhs_sQ6V5bI4LaTg'
        wks_name = 'sgf_db'
        self.gs.to_google_sheets(
            self.df,  
            spreadsheet_key = spreadsheet_key,
            wks_name = wks_name
        )
        print('-- Control Escribanos SGF Completo --')
        print(self.df.head())

        # Control Escribanos SSCC Completo
        self.df = control_escribanos.import_banco_invico()
        self.df = self.df.fillna('')
        self.df['fecha'] = self.df['fecha'].dt.strftime('%d-%m-%Y')
        spreadsheet_key = '1Tz3uvUGBL8ZDSFsYRBP8hgIis-hlhs_sQ6V5bI4LaTg'
        wks_name = 'sscc_db'
        self.gs.to_google_sheets(
            self.df,  
            spreadsheet_key = spreadsheet_key,
            wks_name = wks_name
        )
        print('-- Control Escribanos SSCC Completo --')
        print(self.df.head())

    # --------------------------------------------------
    def upload_control_honorarios(self, ejercicio:list = None):
        """Update and Upload Control Obras
        Update requires:
            - Slave
            - SIIF rcg01_uejp
            - SIIF gto_rpa03g
            - SGF Resumen Rendicions por Proveedor
            - SSCC Resumen General de Movimientos (para agregar dep. emb. x alim. 130832-05)
            - SSCC ctas_ctes (manual data)
        """
        if ejercicio is None:
            ejercicio = self.ejercicio
        control_honorarios = ControlHonorarios(
            input_path=self.input_path, db_path=self.output_path,
            # update_db= self.update_db, 
            ejercicio=ejercicio
        )

        # Control Honorarios SIIF vs Slave
        self.df = control_honorarios.siif_vs_slave()
        self.df = self.df.fillna('')
        self.df = self.df.astype(str)
        spreadsheet_key = '1fQhp1CdESnvqzrp3QMV5bFSHmGdi7SNoaBRWtmw-JgA'
        wks_name = 'siif_vs_slave_db'
        self.gs.to_google_sheets(
            self.df,  
            spreadsheet_key = spreadsheet_key,
            wks_name = wks_name
        )
        print('-- Control Honorarios SIIF vs Slave --')
        print(self.df.head())

        # Control Honorarios Slave vs SGF
        self.df = control_honorarios.slave_vs_sgf(only_diff=True)
        self.df = self.df.fillna('')
        spreadsheet_key = '1fQhp1CdESnvqzrp3QMV5bFSHmGdi7SNoaBRWtmw-JgA'
        wks_name = 'slave_vs_sgf_db'
        self.gs.to_google_sheets(
            self.df,  
            spreadsheet_key = spreadsheet_key,
            wks_name = wks_name
        )
        print('-- Control Honorarios Slave vs SGF --')
        print(self.df.head())

        # Control Honorarios SIIF Completo
        self.df = control_honorarios.import_siif_comprobantes()
        self.df = self.df.fillna('')
        self.df['fecha'] = self.df['fecha'].dt.strftime('%d-%m-%Y')
        spreadsheet_key = '1fQhp1CdESnvqzrp3QMV5bFSHmGdi7SNoaBRWtmw-JgA'
        wks_name = 'siif_db'
        self.gs.to_google_sheets(
            self.df,  
            spreadsheet_key = spreadsheet_key,
            wks_name = wks_name
        )
        print('-- Control Honorarios SIIF Completo --')
        print(self.df.head())

        # Control Honorarios SGF Completo
        self.df = control_honorarios.import_resumen_rend_honorarios()
        self.df = self.df.fillna('')
        self.df['fecha'] = self.df['fecha'].dt.strftime('%d-%m-%Y')
        spreadsheet_key = '1fQhp1CdESnvqzrp3QMV5bFSHmGdi7SNoaBRWtmw-JgA'
        wks_name = 'sgf_db'
        self.gs.to_google_sheets(
            self.df,  
            spreadsheet_key = spreadsheet_key,
            wks_name = wks_name
        )
        print('-- Control Honorarios SGF Completo --')
        print(self.df.head())

        # Control Honorarios Slave Completo
        self.df = control_honorarios.import_slave()
        self.df = self.df.fillna('')
        self.df['fecha'] = self.df['fecha'].dt.strftime('%d-%m-%Y')
        spreadsheet_key = '1fQhp1CdESnvqzrp3QMV5bFSHmGdi7SNoaBRWtmw-JgA'
        wks_name = 'slave_db'
        self.gs.to_google_sheets(
            self.df,  
            spreadsheet_key = spreadsheet_key,
            wks_name = wks_name
        )
        print('-- Control Honorarios Slave Completo --')
        print(self.df.head())

    # --------------------------------------------------
    def upload_control_debitos_bancarios(self, ejercicio:list = None):
        """Update and Upload Control Debitos Bancarios
        Update requires:
            - SIIF gto_rpa03g
            - SIIF rcg01_uejp
            - SSCC Movimientos Generales
            - SSCC ctas_ctes (manual data)
        """
        if ejercicio is None:
            ejercicio = self.ejercicio
        control_debitos = ControlDebitosBancarios(
            input_path=self.input_path, db_path=self.output_path,
            # update_db= self.update_db, 
            ejercicio=ejercicio
        )

        # Control Debitos Bancarios SIIF vs SSCC
        self.df = control_debitos.siif_vs_sscc()
        self.df = self.df.fillna('')
        # self.df = self.df.astype(str)
        spreadsheet_key = '1i9vQ-fw_MkuHRE_YKa_diaVDu5RsiBE1UPTNAsmxLS4'
        wks_name = 'siif_vs_sscc_db'
        self.gs.to_google_sheets(
            self.df,  
            spreadsheet_key = spreadsheet_key,
            wks_name = wks_name
        )
        print('-- Control Debitos Bancarios SIIF vs SSCC --')
        print(self.df.head())

        # Control Debitos Bancarios SIIF Completo
        self.df = control_debitos.import_siif_debitos()
        self.df = self.df.fillna('')
        self.df['fecha'] = self.df['fecha'].dt.strftime('%d-%m-%Y')
        spreadsheet_key = '1i9vQ-fw_MkuHRE_YKa_diaVDu5RsiBE1UPTNAsmxLS4'
        wks_name = 'siif_db'
        self.gs.to_google_sheets(
            self.df,  
            spreadsheet_key = spreadsheet_key,
            wks_name = wks_name
        )
        print('-- Control Debitos Bancarios SIIF Completo --')
        print(self.df.head())

        # Control Debitos Bancarios SSCC Completo
        self.df = control_debitos.import_banco_invico()
        self.df = self.df.fillna('')
        self.df['fecha'] = self.df['fecha'].dt.strftime('%d-%m-%Y')
        spreadsheet_key = '1i9vQ-fw_MkuHRE_YKa_diaVDu5RsiBE1UPTNAsmxLS4'
        wks_name = 'sscc_db'
        self.gs.to_google_sheets(
            self.df,  
            spreadsheet_key = spreadsheet_key,
            wks_name = wks_name
        )
        print('-- Control Debitos Bancarios SSCC Completo --')
        print(self.df.head())

    # --------------------------------------------------
    def upload_control_3_porciento_invico(self, ejercicio:list = None):
        """Update and Upload Control INVICO 3%
        Update requires:
            - SIIF rci02
            - SIIF rcocc31 (
                1112-2-6 Banco INVICO
                2122-1-2 Retenciones
            )
            - SSCC ctas_ctes (manual data)
        """
        if ejercicio is None:
            ejercicio = self.ejercicio
        aporte_empresario = ControlAporteEmpresario(
            input_path=self.input_path, db_path=self.output_path,
            # update_db= self.update_db, 
            ejercicio=ejercicio
        )

        # Control INVICO 3% Recursos vs Retenciones
        self.df = aporte_empresario.siif_recurso_vs_retencion_337()
        self.df = self.df.fillna('')
        # self.df = self.df.astype(str)
        spreadsheet_key = '1bZnvl9YkHC-N1HbIbnFNrqU3Iq03PG81u7fdHe_v_pw'
        wks_name = 'siif_recurso_vs_retencion_337_db'
        self.gs.to_google_sheets(
            self.df,  
            spreadsheet_key = spreadsheet_key,
            wks_name = wks_name
        )
        print('-- Control INVICO 3% Recursos vs Retenciones --')
        print(self.df.head())

        # Control Recursos INVICO 3% COMPLETO
        self.df = aporte_empresario.import_siif_recurso_3_percent()
        self.df = self.df.fillna('')
        self.df['fecha'] = self.df['fecha'].dt.strftime('%d-%m-%Y')
        spreadsheet_key = '1bZnvl9YkHC-N1HbIbnFNrqU3Iq03PG81u7fdHe_v_pw'
        wks_name = 'siif_recurso_3_percent_db'
        self.gs.to_google_sheets(
            self.df,  
            spreadsheet_key = spreadsheet_key,
            wks_name = wks_name
        )
        print('-- Control Recursos INVICO 3% COMPLETO --')
        print(self.df.head())

        # Control SIIF Retención 337 COMPLETO
        self.df = aporte_empresario.import_siif_retencion_337()
        self.df = self.df.fillna('')
        self.df['fecha'] = self.df['fecha'].dt.strftime('%d-%m-%Y')
        spreadsheet_key = '1bZnvl9YkHC-N1HbIbnFNrqU3Iq03PG81u7fdHe_v_pw'
        wks_name = 'siif_retencion_337_db'
        self.gs.to_google_sheets(
            self.df,  
            spreadsheet_key = spreadsheet_key,
            wks_name = wks_name
        )
        print('-- Control SIIF Retención 337 COMPLETO --')
        print(self.df.head())


# --------------------------------------------------
def get_args():
    """Get needed params from user input"""
    parser = argparse.ArgumentParser(
        description = "Upload DataFrame to Google Sheets",
        formatter_class = argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        '-c', '--credentials', 
        metavar = "json_credentials",
        default=None,
        type=str,
        help = "Google's json file credentials name. Must be in the same folder")

    parser.add_argument(
        '-i', '--input_path', 
        metavar = "input_path",
        default= None,
        type=str,
        help = "Base de Datos main folder from where to import files. By default \
        files would be imported from R Gestion INVICO/invicoDB/Base de Datos")

    parser.add_argument(
        '-o', '--output_path', 
        metavar = "output_path",
        default= None,
        type=str,
        help = "output_path to where to save sqlite files. By default \
        files would be save to R Gestion INVICO/Python Output/SQLite Files")

    return parser.parse_args()

# --------------------------------------------------
def main():
    """Let's try it"""
    args = get_args()

    if args.credentials is None:
        google_credentials_path = HanglingPath().get_invicodb_path()
        google_credentials_path = os.path.join(
            google_credentials_path, 'upload'
        )
        google_credentials_path = os.path.join(
            google_credentials_path, 'google_credentials.json'
        )
    else:
        google_credentials_path = args.credentials

    if args.input_path is None:
        input_path = HanglingPath().get_update_path_input()
    else:
        input_path = args.input_path

    if args.output_path is None:
        output_path = HanglingPath().get_db_path()
    else:
        output_path = args.output_path

    upload = UploadGoogleSheet(
        path_credentials_file=google_credentials_path,
        ejercicio='2023',
        # update_db=False,
        input_path=input_path,
        output_path=output_path
    )

    # Requiere:
    # SIIF rf602, SIIF rf610, Icaro
    # upload.upload_ejecucion_gtos(['2019','2020', '2021', '2022', '2023'])
    # upload.upload_ejecucion_pres()
    # upload.upload_planillometro(ejercicio='2022')
    # upload.upload_ejecucion_obras_fondos_prov(['2018','2019','2020', '2021', '2022', '2023'])

    # Requiere:
    # SIIF rcg01_uejp, SIIF gto_rpa03g
    # upload.upload_fondos_perm_cajas_chicas(['2020', '2021', '2022', '2023'])

    # Adicionalmente a todo lo anterior, requiere:
    # SIIF rfondo07tp
    # upload.upload_control_icaro(['2019','2020', '2021', '2022', '2023'])    
    # upload.upload_comprobantes_gastos()

    # Requiere:
    # SIIF rci02, SIIF ri102, SSCC Consulta General de Movimiento
    # upload.upload_control_recursos(['2020', '2021', '2022', '2023'])
    # upload.upload_flujo_caja(['2022', '2023'])

    # Requiere
    # Icaro, rdeu012, SGF Resumen Rend por Proveedor
    # upload.upload_control_obras(['2020', '2021', '2022', '2023'])

    # Requiere
    # 
    # upload.upload_control_haberes(['2022', '2023'])
    
    # Requiere
    #     
    # upload.upload_control_retenciones(['2022', '2023'])

    # Requiere
    #     
    # upload.upload_control_escribanos(['2022', '2023'])

    # Requiere
    #     
    # upload.upload_control_honorarios(['2022', '2023'])

    # Requiere
    #     
    # upload.upload_control_debitos_bancarios(['2022', '2023'])

    # Requiere
    #     
    # upload.upload_control_3_porciento_invico(['2022', '2023'])

    upload.upload_listado_obras()

# --------------------------------------------------
if __name__ == '__main__':
    main()
    # From invicoDB.src
    # python -m invicodb.upload.upload_db
