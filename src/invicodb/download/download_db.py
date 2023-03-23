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
from dataclasses import dataclass, field

from invicodatpy.siif import *

from ..hangling_path import HanglingPath
from selenium import webdriver


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
        print('--- Connect to SIIF ---')
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
            self.download_all = True
            self.download_ppto_gtos_desc_rf610()
            self.download_ppto_gtos_fte_rf602()
            self.download_comprobantes_gtos_rcg01_uejp()
            self.download_comprobantes_gtos_gpo_part_gto_rpa03g()
            self.download_resumen_fdos_rfondo07tp()
            self.download_comprobantes_rec_rci02()
            self.download_deuda_flotante_rdeu012()
            # self.download_deuda_flotante_rdeu012b2_c()
            self.download_mayor_contable_rcocc31()
            # self.download_detalle_partidas_rog01()
        except Exception as e:
            print(f"Ocurrió un error: {e}, {type(e)}")
            self.disconnect() 
        finally:
            self.quit()

    # --------------------------------------------------
    def download_ppto_gtos_desc_rf610(self):
        df = ppto_gtos_desc_rf610.PptoGtosDescRf610(siif = self.siif_connection)
        df.download_report(
            os.path.join(
                self.output_path, 'Ejecucion Presupuestaria con Descripcion (rf610)'
            )
        )
        if not self.download_all:
            self.quit()

    # --------------------------------------------------
    def download_ppto_gtos_fte_rf602(self):
        df = ppto_gtos_fte_rf602.PptoGtosFteRf602(siif = self.siif_connection)
        df.download_report(
            os.path.join(
                self.output_path, 'Ejecucion Presupuestaria con Fuente (rf602)'
            )
        )
        if not self.download_all:
            self.quit()

    # --------------------------------------------------
    def download_comprobantes_gtos_rcg01_uejp(self):
        df = comprobantes_gtos_rcg01_uejp.ComprobantesGtosRcg01Uejp(siif = self.siif_connection)
        df.download_report(
            os.path.join(
                self.output_path, 'Comprobantes de Gastos (rcg01_uejp)'
            )
        )
        if not self.download_all:
            self.quit()

    # --------------------------------------------------
    def download_comprobantes_gtos_gpo_part_gto_rpa03g(self):
        df = comprobantes_gtos_gpo_part_gto_rpa03g.ComprobantesGtosGpoPartGtoRpa03g(
            siif = self.siif_connection
        )
        df.download_report(
            os.path.join(
                self.output_path, 'Comprobantes de Gastos por Grupo Partida (gto_rpa03g)'
            )
        )
        if not self.download_all:
            self.quit()

    # --------------------------------------------------
    def download_resumen_fdos_rfondo07tp(self):
        df = resumen_fdos_rfondo07tp.ResumenFdosRfondo07tp(
            siif = self.siif_connection
        )
        df.download_report(
            os.path.join(
                self.output_path, 'Comprobantes de Fondos Regularizados por Tipo (rfondo07tp)'
            )
        )
        if not self.download_all:
            self.quit()

    # --------------------------------------------------
    def download_comprobantes_rec_rci02(self):
        df = comprobantes_rec_rci02.ComprobantesRecRci02(
            siif = self.siif_connection
        )
        df.download_report(
            os.path.join(
                self.output_path, 'Comprobantes de Recursos (rci02)'
            )
        )
        if not self.download_all:
            self.quit()

    # --------------------------------------------------
    def download_deuda_flotante_rdeu012(self):
        df = deuda_flotante_rdeu012.DeudaFlotanteRdeu012(
            siif = self.siif_connection
        )
        df.download_report(
            os.path.join(
                self.output_path, 'Deuda Flotante (rdeu)'
            )
        )
        if not self.download_all:
            self.quit()

    # --------------------------------------------------
    def download_mayor_contable_rcocc31(self):
        df = mayor_contable_rcocc31.MayorContableRcocc31(
            siif = self.siif_connection
        )
        df.download_report(
            os.path.join(
                self.output_path, 'Movimientos Contables (rcocc31)'
            )
        )
        if not self.download_all:
            self.quit()

    # --------------------------------------------------
    def quit(self):
        self.siif_connection.disconnect()

# --------------------------------------------------
def get_args():
    """Get needed params from user input"""
    parser = argparse.ArgumentParser(
        description = "Download SIIF's reports",
        formatter_class = argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        '-c', '--credentials', 
        metavar = "json_credentials",
        default=None,
        type=str,
        help = "SIIF's json file credentials name. Must be in the same folder")

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

    if args.credentials == None:
        siif_credentials_path = HanglingPath().get_invicodb_path()
        siif_credentials_path = os.path.join(
            siif_credentials_path, 'download'
        )
        siif_credentials_path = os.path.join(
            siif_credentials_path, 'siif_credentials.json'
        )
    else:
        siif_credentials_path = args.credentials

    if args.output_path == None:
        output_path = HanglingPath().get_update_path_input()
    else:
        output_path = args.output_path

    DownloadSIIF(
        path_credentials_file=siif_credentials_path,
        output_path=os.path.join(output_path, 'Reportes SIIF')
        ).download_all_siif_tables()
        
# --------------------------------------------------
if __name__ == '__main__':
    main()
    # From invicoDB.src
    # python -m invicodb.download.download_db
