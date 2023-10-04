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
from dataclasses import dataclass, field

import pandas as pd
from invicoctrlpy.banco.flujo_caja import FlujoCaja
from invicoctrlpy.gastos.control_haberes.control_haberes import ControlHaberes
from invicoctrlpy.gastos.control_obras.control_obras import ControlObras
from invicoctrlpy.gastos.control_retenciones.control_retenciones import \
    ControlRetenciones
from invicoctrlpy.gastos.ejecucion_gastos.ejecucion_gastos import \
    EjecucionGastos
from invicoctrlpy.gastos.ejecucion_obras.ejecucion_obras import EjecucionObras
from invicoctrlpy.gastos.fondos_perm_cajas_chicas.fondos_perm_cajas_chicas import \
    FondosPermCajasChicas
from invicoctrlpy.icaro.icaro_vs_siif.icaro_vs_siif import IcaroVsSIIF
from invicoctrlpy.recursos.control_recursos.control_recursos import \
    ControlRecursos
from invicodatpy.utils.google_sheets import GoogleSheets

from ..hangling_path import HanglingPath


# --------------------------------------------------
@dataclass
class UploadGoogleSheet():
    """Upload DataFrame to Google Sheets
    :param path_credentials_file: json file download from Google
    :param update_db: Should sqlite files be updated?
    :param input_path: If update_db is True '/Base de Datos' path must be given
    :param output_path: If update_db is True 'Python Output/SQLite Files' must be given
    """
    path_credentials_file:str
    ejercicio:str = str(dt.datetime.now().year)
    update_db:bool = False
    input_path:str = None
    output_path:str = None
    gs:GoogleSheets = field(init=False, repr=False)
    df:pd.DataFrame = field(init=False, repr=False)

    # --------------------------------------------------
    def __post_init__(self):
        if self.input_path == None or self.output_path == None:
            self.update_db = False
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
        self.upload_formulacion_gtos([ejercicio_actual, ejercicio_siguiente])
        self.upload_ejecucion_gtos(ejercicios_varios)
        self.upload_ejecucion_pres()
        self.upload_planillometro()
        self.upload_ejecucion_obras_fondos_prov(ejercicios_varios)
        self.upload_fondos_perm_cajas_chicas(ejercicios_varios)
        self.upload_control_icaro(ejercicios_varios)
        # self.upload_comprobantes_gastos()
        self.upload_control_recursos(ejercicios_varios)
        self.upload_flujo_caja(ejercicios_varios)
        self.upload_control_obras(ejercicios_varios)
        self.upload_control_haberes(ejercicios_varios)
        self.upload_control_retenciones([ejercicio_actual, ejercicio_anterior])

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
        if ejercicio == None:
            ejercicio_metodo = self.ejercicio
        else:
            ejercicio_metodo = ejercicio

        ejecucion_gastos = EjecucionGastos(
            input_path=self.input_path, db_path=self.output_path,
            update_db= self.update_db, ejercicio=ejercicio_metodo
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
        """
        if ejercicio == None:
            ejercicio_metodo = self.ejercicio
        else:
            ejercicio_metodo = ejercicio

        ejecucion_gastos = EjecucionGastos(
            input_path=self.input_path, db_path=self.output_path,
            update_db= self.update_db, ejercicio=ejercicio_metodo
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

        # Comprobantes Gastos SIIF
        self.df = ejecucion_gastos.import_siif_comprobantes()
        self.df['fecha'] = self.df['fecha'].dt.strftime('%d-%m-%Y')
        self.df = self.df.fillna('')
        spreadsheet_key = '1SRmgep84KGJNj_nKxiwXLe28gVUiIu2Uha4j_C7BzeU'
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
            update_db= self.update_db, ejercicio=self.ejercicio
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
        if ejercicio == None:
            ejercicio = self.ejercicio
        ejecucion_obras = EjecucionObras(
            input_path=self.input_path, db_path=self.output_path,
            update_db= self.update_db, ejercicio=ejercicio
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
        if ejercicio == None:
            ejercicio_metodo = self.ejercicio
        else:
            ejercicio_metodo = ejercicio

        ejecucion_obras = EjecucionObras(
            input_path=self.input_path, db_path=self.output_path,
            update_db= self.update_db, ejercicio=ejercicio_metodo
        )

        # Planillometro SIIF
        self.df = ejecucion_obras.reporte_planillometro(full_icaro=False, es_desc_siif=True)
        spreadsheet_key = '1AYeTncc1ewP8Duj13t7o6HCwAHNEWILRMNQiZHAs82I'
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
        spreadsheet_key = '1AYeTncc1ewP8Duj13t7o6HCwAHNEWILRMNQiZHAs82I'
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
        spreadsheet_key = '1AYeTncc1ewP8Duj13t7o6HCwAHNEWILRMNQiZHAs82I'
        wks_name = 'planillometro_icaro'
        self.gs.to_google_sheets(
            self.df,  
            spreadsheet_key = spreadsheet_key,
            wks_name = wks_name
        )
        print('-- Planillometro Icaro --')
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

        if ejercicio == None:
            ejercicio_metodo = self.ejercicio
        else:
            ejercicio_metodo = ejercicio

        icaro_vs_siif = IcaroVsSIIF(
            input_path=self.input_path, db_path=self.output_path,
            update_db= self.update_db, ejercicio=ejercicio_metodo
        )

        # Control Ejecucion Anual
        self.df = icaro_vs_siif.control_ejecucion_anual()
        self.df = self.df.fillna(0)
        spreadsheet_key = '1KKeeoop_v_Nf21s7eFp4sS6SmpxRZQ9DPa1A5wVqnZ0'
        wks_name = 'control_ejecucion_anual'
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
        spreadsheet_key = '1KKeeoop_v_Nf21s7eFp4sS6SmpxRZQ9DPa1A5wVqnZ0'
        wks_name = 'control_comprobantes'
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
        spreadsheet_key = '1KKeeoop_v_Nf21s7eFp4sS6SmpxRZQ9DPa1A5wVqnZ0'
        wks_name = 'control_pa6'
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
            update_db= self.update_db, ejercicio=None
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
            - SSCC Consulta General de Movimiento
            - SSCC ctas_ctes (manual data)
        """
        if ejercicio == None:
            ejercicio_metodo = self.ejercicio
        else:
            ejercicio_metodo = ejercicio

        control_recursos = ControlRecursos(
            input_path=self.input_path, db_path=self.output_path,
            update_db= self.update_db, ejercicio=ejercicio_metodo
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
        if ejercicio == None:
            ejercicio_metodo = self.ejercicio
        else:
            ejercicio_metodo = ejercicio

        flujo_caja = FlujoCaja(
            input_path=self.input_path, db_path=self.output_path,
            update_db= self.update_db, ejercicio=ejercicio_metodo
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
        if ejercicio == None:
            ejercicio = self.ejercicio

        control_haberes = ControlHaberes(
            input_path=self.input_path, db_path=self.output_path,
            update_db= self.update_db, ejercicio=ejercicio
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
        if ejercicio == None:
            ejercicio = self.ejercicio

        control_retenciones = ControlRetenciones(
            input_path=self.input_path, db_path=self.output_path,
            update_db= self.update_db, ejercicio=ejercicio
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
        self.df = control_retenciones.icaro_vs_invico(
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
        if ejercicio == None:
            ejercicio = self.ejercicio
        fondos_perm = FondosPermCajasChicas(
            input_path=self.input_path, db_path=self.output_path,
            update_db= self.update_db, ejercicio=ejercicio
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
            - SIIF rdeu012 (para netear Icaro)
            - SGF Resumen Rend por Proveedor
        """
        if ejercicio == None:
            ejercicio = self.ejercicio
        control_obras = ControlObras(
            input_path=self.input_path, db_path=self.output_path,
            update_db= self.update_db, ejercicio=ejercicio
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

    if args.credentials == None:
        google_credentials_path = HanglingPath().get_invicodb_path()
        google_credentials_path = os.path.join(
            google_credentials_path, 'upload'
        )
        google_credentials_path = os.path.join(
            google_credentials_path, 'google_credentials.json'
        )
    else:
        google_credentials_path = args.credentials

    if args.input_path == None:
        input_path = HanglingPath().get_update_path_input()
    else:
        input_path = args.input_path

    if args.output_path == None:
        output_path = HanglingPath().get_db_path()
    else:
        output_path = args.output_path

    upload = UploadGoogleSheet(
        path_credentials_file=google_credentials_path,
        ejercicio='2023',
        update_db=False,
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
    # upload.upload_control_haberes(['2020', '2021', '2022', '2023'])
    
    # Requiere
    #     
    # upload.upload_control_retenciones(['2022', '2023'])

    upload.upload_all_dfs()

# --------------------------------------------------
if __name__ == '__main__':
    main()
    # From invicoDB.src
    # python -m invicodb.upload.upload_db
