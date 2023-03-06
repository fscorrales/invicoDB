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
from invicoctrlpy.gastos.control_retenciones.control_retenciones import \
    ControlRetenciones
from invicoctrlpy.gastos.ejecucion_obras.ejecucion_obras import EjecucionObras
from invicoctrlpy.gastos.control_haberes.control_haberes import ControlHaberes
from invicoctrlpy.gastos.fondos_perm_cajas_chicas.fondos_perm_cajas_chicas import FondosPermCajasChicas
from invicoctrlpy.icaro.icaro_vs_siif.icaro_vs_siif import IcaroVsSIIF
from invicoctrlpy.recursos.control_recursos.control_recursos import ControlRecursos
from invicodatpy.utils.google_sheets import GoogleSheets

from .hangling_path import HanglingPath


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
        self.upload_ejecucion_pres()
        self.upload_planillometro()
        self.upload_control_icaro()
        self.upload_comprobantes_gastos()
        self.upload_control_recursos()
        self.upload_control_retenciones()
        self.upload_fondos_perm_cajas_chicas()

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
        self.df = ejecucion_obras.reporte_icaro_mod_basicos()
        spreadsheet_key = '1EqZmq2uYrc-rJxGuGJKKUTRqhCvTWMhtkhHDef7E55o'
        wks_name = 'mod_basicos_convenios'
        self.gs.to_google_sheets(
            self.df,  
            spreadsheet_key = spreadsheet_key,
            wks_name = wks_name
        )
        print('-- Ejecucion Modulos Básicos por Convenio --')
        print(self.df.head())

        # Planillometro SIIF

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
        spreadsheet_key = '1yn3-B3blPJmF8RknUEBs5xCQW1RrFTYvBxECF4PBt2M'
        wks_name = 'siif'
        self.gs.to_google_sheets(
            self.df,  
            spreadsheet_key = spreadsheet_key,
            wks_name = wks_name
        )
        print('-- Planillometro SIIF --')
        print(self.df.head())


        # Planillometro Icaro
        self.df = ejecucion_obras.reporte_planillometro(full_icaro=True, es_desc_siif=False)
        spreadsheet_key = '1yn3-B3blPJmF8RknUEBs5xCQW1RrFTYvBxECF4PBt2M'
        wks_name = 'icaro'
        self.gs.to_google_sheets(
            self.df,  
            spreadsheet_key = spreadsheet_key,
            wks_name = wks_name
        )
        print('-- Planillometro Icaro --')
        print(self.df.head())


    # --------------------------------------------------
    def upload_control_icaro(self):
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
            update_db= self.update_db, ejercicio=self.ejercicio
        )

        # Control Ejecucion Anual
        self.df = icaro_vs_siif.control_ejecucion_anual()
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
        self.df = control_recursos.control_mes_grupo_cta_cte()
        self.df = self.df.fillna('')
        spreadsheet_key = '1u_I5wN3w_rGX6rWIsItXkmwfIEuSox6ZsmKYbMZ2iUY'
        wks_name = 'control_mes_grupo_cta_cte'
        self.gs.to_google_sheets(
            self.df,  
            spreadsheet_key = spreadsheet_key,
            wks_name = wks_name
        )
        print('-- Control Recursos por Mes, Grupo y Cta Cte --')
        print(self.df.head())

        # Control Recursos por Mes y Grupo
        self.df = control_recursos.control_mes_grupo()
        self.df = self.df.fillna('')
        spreadsheet_key = '1u_I5wN3w_rGX6rWIsItXkmwfIEuSox6ZsmKYbMZ2iUY'
        wks_name = 'control_mes_grupo'
        self.gs.to_google_sheets(
            self.df,  
            spreadsheet_key = spreadsheet_key,
            wks_name = wks_name
        )
        print('-- Control Recursos por Mes y Grupo --')
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

        # SSCC Banco INVICO
        self.df = control_recursos.import_banco_invico()
        self.df = self.df.fillna('')
        self.df['fecha'] = self.df['fecha'].dt.strftime('%d-%m-%Y')
        spreadsheet_key = '1u_I5wN3w_rGX6rWIsItXkmwfIEuSox6ZsmKYbMZ2iUY'
        wks_name = 'banco_invico'
        self.gs.to_google_sheets(
            self.df,  
            spreadsheet_key = spreadsheet_key,
            wks_name = wks_name
        )
        print('-- SSCC Banco INVICO --')
        print(self.df.head())

    # --------------------------------------------------
    def upload_control_haberes(self, ejercicio:str = None):
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
            ejercicio_metodo = self.ejercicio
        else:
            ejercicio_metodo = ejercicio

        control_haberes = ControlHaberes(
            input_path=self.input_path, db_path=self.output_path,
            update_db= self.update_db, ejercicio=ejercicio_metodo
        )
        # Control Haberes Mensual
        self.df = control_haberes.control_mes()
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
    def upload_control_retenciones(self):
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
        control_retenciones = ControlRetenciones(
            input_path=self.input_path, db_path=self.output_path,
            update_db= self.update_db, ejercicio=self.ejercicio
        )

        # Control Retenciones Icaro
        self.df = control_retenciones.control_retenciones_mensual_cta_cte()
        spreadsheet_key = '1hPYm25LQ13LmPXM-4skv7LhhAWL-GC4WAnm-DXKmk0I'
        wks_name = 'icaro_retenciones'
        self.gs.to_google_sheets(
            self.df,  
            spreadsheet_key = spreadsheet_key,
            wks_name = wks_name
        )
        print('-- Control Retenciones Icaro --')
        print(self.df.head())

    # --------------------------------------------------
    def upload_fondos_perm_cajas_chicas(self, ejercicio:list = None):
        """Update and Upload Fondos Permanentes y Cajas Chicas
        Update requires:
            - SIIF rcg01_uejp
            - SIIF gto_rpa03g
            - SIIF rog01
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
        update_db=True,
        input_path=input_path,
        output_path=output_path
    )
    # upload.upload_all_dfs()
    # upload.upload_ejecucion_pres()
    # upload.upload_control_icaro()
    # upload.upload_planillometro(ejercicio='2022')
    # upload.upload_comprobantes_gastos()
    # upload.upload_control_recursos(ejercicio='2023')
    upload.upload_fondos_perm_cajas_chicas(['2020', '2021', '2022', '2023'])


# --------------------------------------------------
if __name__ == '__main__':
    main()
    # From invicoDB.src
    # python -m invicodb.upload_db
