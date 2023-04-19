#!/usr/bin/env python3
"""
Author: Fernando Corrales <fscorrales@gmail.com>
Purpose: Upload set of INVICO DB' sqlite files to Google Sheets
Packages:
 - invicodatpy (pip install '/home/kanou/IT/R Apps/R Gestion INVICO/invicodatpy')
"""
import argparse
import datetime as dt
import json
import os
import shutil
from dataclasses import dataclass, field

from invicodatpy.sgf import *
from invicodatpy.siif import *
from invicodatpy.sscc import *
from selenium import webdriver

from ..hangling_path import HanglingPath


# --------------------------------------------------
@dataclass
class DownloadSIIF():
    """Download SIIF' reports
    :param path_credentials_file: json file with SIIF' credentials
    :param input_path: If update_db is True '/Base de Datos' path must be given
    :param output_path: If update_db is True 'Python Output/SQLite Files' must be given
    """
    path_credentials_file:str
    output_path:str
    download_all:bool = field(init=False, repr=False, default=False)
    siif_connection:webdriver = field(init=False, repr=False)

    # --------------------------------------------------
    def __post_init__(self):
        print('--- Iniciando descarga de DB SIIF ---')
        print('- Connect to SIIF -')
        if os.path.isfile(self.path_credentials_file):
            with open(self.path_credentials_file) as json_file:
                data_json = json.load(json_file)
                self.siif_connection = connect_siif.ConnectSIIF(
                    data_json['username'], data_json['password']
                )
            json_file.close()
        else:
            print('El ruta del archivo json con las credenciales de acceso no es válida')
            print(self.path_credentials_file)

    # --------------------------------------------------
    def download_all_siif_tables(self):
        try:
            print("- Iniciando descarga masiva de reportes SIIF -")
            int_ejercicio = dt.datetime.now().year
            ejercicio_actual = str(int_ejercicio)
            fecha_limite = dt.datetime(year=int_ejercicio, month=3, day=31)
            if dt.datetime.now() < fecha_limite:
                ejercicio_anterior = str(dt.datetime.now().year - 1)
                ejercicios = [ejercicio_anterior, ejercicio_actual]
            else:
                ejercicios = [ejercicio_actual]
            self.download_all = True
            self.download_ppto_gtos_desc_rf610(ejercicios)
            self.download_ppto_gtos_fte_rf602(ejercicios)
            self.download_comprobantes_gtos_rcg01_uejp(ejercicios)
            self.download_comprobantes_gtos_gpo_part_gto_rpa03g(ejercicios)
            self.download_resumen_fdos_rfondo07tp(ejercicios)
            self.download_comprobantes_rec_rci02(ejercicios)
            self.download_mayor_contable_rcocc31(
                ejercicios, 
                ctas_contables = [
                    '1112-2-6', '1141-1-4', '2111-1-1', '2111-1-2',
                    '2113-2-9', '2121-1-1', '2122-1-2',
                ]
            )
            mes_actual = dt.datetime.strftime(dt.datetime.now(), '%Y-%m')
            mes_anterior = int(mes_actual[-2:]) - 1
            if mes_anterior == 0:
                mes_anterior = 12
            mes_anterior = mes_actual[:-2] + str(mes_anterior).zfill(2) 
            meses = [mes_anterior, mes_actual]
            self.download_deuda_flotante_rdeu012(meses)
            # self.download_deuda_flotante_rdeu012b2_c()
            # self.download_detalle_partidas_rog01()
        except Exception as e:
            print(f"Ocurrió un error: {e}, {type(e)}")
            self.siif_connection.disconnect() 
        finally:
            self.quit()

    # --------------------------------------------------
    def download_ppto_gtos_desc_rf610(self, ejercicios:list):
        print("- Descargando SIIF's rf610 -")
        df = ppto_gtos_desc_rf610.PptoGtosDescRf610(siif = self.siif_connection)
        df.download_report(
            os.path.join(
                self.output_path, 'Ejecucion Presupuestaria con Descripcion (rf610)'
            ),
            ejercicios = ejercicios
        )
        if not self.download_all:
            self.quit()

    # --------------------------------------------------
    def download_ppto_gtos_fte_rf602(self, ejercicios:list):
        print("- Descargando SIIF's rf602 -")
        df = ppto_gtos_fte_rf602.PptoGtosFteRf602(siif = self.siif_connection)
        df.download_report(
            os.path.join(
                self.output_path, 'Ejecucion Presupuestaria con Fuente (rf602)'
            ), 
            ejercicios=ejercicios
        )
        if not self.download_all:
            self.quit()

    # --------------------------------------------------
    def download_comprobantes_gtos_rcg01_uejp(self, ejercicios:list):
        print("- Descargando SIIF's rcg01_uejp -")
        df = comprobantes_gtos_rcg01_uejp.ComprobantesGtosRcg01Uejp(siif = self.siif_connection)
        df.download_report(
            os.path.join(
                self.output_path, 'Comprobantes de Gastos (rcg01_uejp)'
            ),
            ejercicios= ejercicios
        )
        if not self.download_all:
            self.quit()

    # --------------------------------------------------
    def download_comprobantes_gtos_gpo_part_gto_rpa03g(self, ejercicios:list):
        print("- Descargando SIIF's gto_rpa03g -")
        df = comprobantes_gtos_gpo_part_gto_rpa03g.ComprobantesGtosGpoPartGtoRpa03g(
            siif = self.siif_connection
        )
        df.download_report(
            os.path.join(
                self.output_path, 'Comprobantes de Gastos por Grupo Partida (gto_rpa03g)'
            ),
            ejercicios= ejercicios
        )
        if not self.download_all:
            self.quit()

    # --------------------------------------------------
    def download_resumen_fdos_rfondo07tp(self, ejercicios:list):
        print("- Descargando SIIF's rfondo07tp -")
        df = resumen_fdos_rfondo07tp.ResumenFdosRfondo07tp(
            siif = self.siif_connection
        )
        df.download_report(
            os.path.join(
                self.output_path, 'Comprobantes de Fondos Regularizados por Tipo (rfondo07tp)'
            ),
            ejercicios= ejercicios
        )
        if not self.download_all:
            self.quit()

    # --------------------------------------------------
    def download_comprobantes_rec_rci02(self, ejercicios:list):
        print("- Descargando SIIF's rci02 -")
        df = comprobantes_rec_rci02.ComprobantesRecRci02(
            siif = self.siif_connection
        )
        df.download_report(
            os.path.join(
                self.output_path, 'Comprobantes de Recursos (rci02)'
            ),
            ejercicios= ejercicios
        )
        if not self.download_all:
            self.quit()

    # --------------------------------------------------
    def download_deuda_flotante_rdeu012(self, meses:list):
        print("- Descargando SIIF's rdeu012 -")
        df = deuda_flotante_rdeu012.DeudaFlotanteRdeu012(
            siif = self.siif_connection
        )
        df.download_report(
            os.path.join(
                self.output_path, 'Deuda Flotante (rdeu)'
            ),
            meses = meses
        )
        if not self.download_all:
            self.quit()

    # --------------------------------------------------
    def download_mayor_contable_rcocc31(
        self, ejercicios:list, ctas_contables:list = '1112-2-6'
    ):
        print("- Descargando SIIF's rcocc31 -")
        df = mayor_contable_rcocc31.MayorContableRcocc31(
            siif = self.siif_connection
        )
        df.download_report(
            os.path.join(
                self.output_path, 'Movimientos Contables (rcocc31)'
            ),
            ejercicios= ejercicios,
            ctas_contables= ctas_contables
        )
        if not self.download_all:
            self.quit()

    # --------------------------------------------------
    def remove_html_files(self):
        root_dir = self.output_path
        for folder, subfolders, files in os.walk(root_dir):
            if folder != root_dir:
                for f in files:
                    if f.endswith(".html"):
                        file_path = os.path.join(folder, f)
                        os.remove(file_path)
                        print(f"File: {file_path} removed")

    # --------------------------------------------------
    def quit(self):
        self.remove_html_files()
        self.siif_connection.disconnect()

# --------------------------------------------------
@dataclass
class DownloadSSCC():
    """Download SSCC' reports
    :param path_credentials_file: json file with INVICO' credentials
    :param input_path: If update_db is True '/Base de Datos' path must be given
    :param output_path: If update_db is True 'Python Output/SQLite Files' must be given
    """
    path_credentials_file:str
    output_path:str
    download_all:bool = field(init=False, repr=False, default=False)
    sscc_connection:connect_sscc.ConnectSSCC = field(init=False, repr=False)

    # --------------------------------------------------
    def __post_init__(self):
        print('--- Iniciando descarga de DB SSCC ---')
        print('- Connect to SSCC -')
        if os.path.isfile(self.path_credentials_file):
            with open(self.path_credentials_file) as json_file:
                data_json = json.load(json_file)
                self.sscc_connection = connect_sscc.ConnectSSCC(
                    data_json['username'], data_json['password']
                )
            json_file.close()
        else:
            print('El ruta del archivo json con las credenciales de acceso no es válida')
            print(self.path_credentials_file)

    # --------------------------------------------------
    def download_all_sscc_tables(self):
        try:
            print("- Iniciando descarga masiva de reportes SSCC -")
            int_ejercicio = dt.datetime.now().year
            ejercicio_actual = str(int_ejercicio)
            fecha_limite = dt.datetime(year=int_ejercicio, month=1, day=31)
            if dt.datetime.now() < fecha_limite:
                ejercicio_anterior = str(dt.datetime.now().year - 1)
                ejercicios = [ejercicio_anterior, ejercicio_actual]
            else:
                ejercicios = [ejercicio_actual]
            self.download_all = True
            self.download_banco_invico(ejercicios=ejercicios)
        except Exception as e:
            print(f"Ocurrió un error: {e}, {type(e)}")
            self.quit() 
        finally:
            self.quit()

    # --------------------------------------------------
    def download_banco_invico(self, ejercicios:list):
        print("- Descargando SSCC's Resumen General de Movimientos -")
        df = banco_invico.BancoINVICO(sscc = self.sscc_connection)
        df.download_report(
            os.path.join(
                self.output_path, 'Movimientos Generales SSCC'
            ),
            ejercicios = ejercicios
        )
        if not self.download_all:
            self.quit()

    # --------------------------------------------------
    def quit(self):
        self.sscc_connection.quit()

# --------------------------------------------------
@dataclass
class DownloadSGF():
    """Download SGF' reports
    :param path_credentials_file: json file with INVICO' credentials
    :param input_path: If update_db is True '/Base de Datos' path must be given
    :param output_path: If update_db is True 'Python Output/SQLite Files' must be given
    """
    path_credentials_file:str
    output_path:str
    download_all:bool = field(init=False, repr=False, default=False)
    sgf_connection:connect_sgf.ConnectSGF = field(init=False, repr=False)

    # --------------------------------------------------
    def __post_init__(self):
        print('--- Iniciando descarga de DB SGF ---')
        print('- Connect to SGF -')
        if os.path.isfile(self.path_credentials_file):
            with open(self.path_credentials_file) as json_file:
                data_json = json.load(json_file)
                self.sgf_connection = connect_sgf.ConnectSGF(
                    data_json['username'], data_json['password']
                )
            json_file.close()
        else:
            print('El ruta del archivo json con las credenciales de acceso no es válida')
            print(self.path_credentials_file)

    # --------------------------------------------------
    def download_all_sgf_tables(self):
        try:
            print("- Iniciando descarga masiva de reportes SGF -")
            int_ejercicio = dt.datetime.now().year
            ejercicio_actual = str(int_ejercicio)
            fecha_limite = dt.datetime(year=int_ejercicio, month=1, day=31)
            if dt.datetime.now() < fecha_limite:
                ejercicio_anterior = str(dt.datetime.now().year - 1)
                ejercicios = [ejercicio_anterior, ejercicio_actual]
            else:
                ejercicios = [ejercicio_actual]
            self.download_all = True
            self.download_resumen_rend_prov(ejercicios=ejercicios)
        except Exception as e:
            print(f"Ocurrió un error: {e}, {type(e)}")
            self.quit() 
        finally:
            self.quit()

    # --------------------------------------------------
    def download_resumen_rend_prov(self, ejercicios:list):
        print("- Descargando SGF's Resumen Rendiciones Proveedores -")
        df = resumen_rend_prov.ResumenRendProv(sgf = self.sgf_connection)
        df.download_report(
            os.path.join(
                self.output_path, 'Resumen de Rendiciones SGF'
            ),
            ejercicios = ejercicios
        )
        if not self.download_all:
            self.quit()

    # --------------------------------------------------
    def quit(self):
        self.sgf_connection.quit()

# --------------------------------------------------
@dataclass
class CopyIcaro():
    """Copy Icaro DB from Exequiel's PC to mine
    :param exequiel_path
    :param my_path
    """
    exequiel_path:str
    my_path:str

    def __post_init__(self):
        print("- Copiando Icaro desde la PC de Exequiel -")
        try:
            shutil.copy(self.exequiel_path, self.my_path, follow_symlinks=True)
        except Exception as e:
            print(f"No se pudo copiar ICARO por el siguiente error: {e}, {type(e)}")
# --------------------------------------------------
def get_args():
    """Get needed params from user input"""
    parser = argparse.ArgumentParser(
        description = "Download SIIF's reports",
        formatter_class = argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        '-o', '--output_path', 
        metavar = "output_path",
        default= None,
        type=str,
        help = "Base de Datos main folder to where to save files. By default \
        files would be saved from R Gestion INVICO/invicoDB/Base de Datos")

    return parser.parse_args()

# --------------------------------------------------
def main():
    """Let's try it"""
    args = get_args()

    if args.output_path == None:
        output_path = HanglingPath().get_update_path_input()
    else:
        output_path = args.output_path

    credentials_path = HanglingPath().get_invicodb_path()
    credentials_path = os.path.join(
        credentials_path, 'download'
    )
    
    # siif_credentials_path = os.path.join(
    #     credentials_path, 'siif_credentials.json'
    # )

    # DownloadSIIF(
    #     path_credentials_file=siif_credentials_path,
    #     output_path=os.path.join(output_path, 'Reportes SIIF')
    #     ).download_all_siif_tables()

    invico_credentials_path = os.path.join(
        credentials_path, 'invico_credentials.json'
    )

    # DownloadSSCC(
    #     path_credentials_file=invico_credentials_path,
    #     output_path=os.path.join(output_path, 'Sistema de Seguimiento de Cuentas Corrientes')
    #     ).download_all_sscc_tables()

    DownloadSGF(
        path_credentials_file=invico_credentials_path,
        output_path=os.path.join(output_path, 'Sistema Gestion Financiera')
        ).download_all_sgf_tables()

    # output_path = HanglingPath().get_outside_path()
    # exequiel_path = HanglingPath().get_exequiel_path()

    # CopyIcaro(
    #     exequiel_path = os.path.join(exequiel_path, 'ICARO.sqlite'),
    #     my_path = os.path.join(output_path, 'R Output/SQLite Files/ICARO.sqlite')
    # )
        
# --------------------------------------------------
if __name__ == '__main__':
    main()
    # From invicoDB.src
    # python -m invicodb.download.download_db
