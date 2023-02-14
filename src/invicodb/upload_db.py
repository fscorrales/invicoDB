#!/usr/bin/env python3
"""
Author: Fernando Corrales <fscorrales@gmail.com>
Purpose: Upload set of INVICO DB' sqlite files to Google Sheets
Packages:
 - invicodatpy (pip install -e '/home/kanou/IT/R Apps/R Gestion INVICO/invicodatpy')
"""
import argparse
import os
from dataclasses import dataclass, field
import pandas as pd

from invicoctrlpy.gastos.ejecucion_obras.ejecucion_obras import EjecucionObras
from invicodatpy.utils.google_sheets import GoogleSheets

from .hangling_path import HanglingPath

# --------------------------------------------------
@dataclass
class UploadEjecucionObras():
    spreadsheet_key:str = '119DPlbkDm-MQ3-R4K8VGR_BNkHpDM1sgTn5CaiRc418'
    wks_name:str = 'Hoja 1'
    df:pd.DataFrame = field(init=False, repr=False)
    """Update and Upload Ejecución Presupuestaria to Google Sheet"""

    # --------------------------------------------------
    def update_all_sscc_tables(self):
        pass
        # self.update_banco_invico()
        # self.update_ctas_ctes()
        # self.update_sdo_final_banco_invico()

#     # --------------------------------------------------
#     def update_banco_invico(self):
#         df = banco_invico.BancoINVICO()
#         df.update_sql_db(
#             self.input_path + '/Movimientos Generales SSCC',
#             output_path=self.output_path, clean_first=True)

#     # --------------------------------------------------
#     def update_sdo_final_banco_invico(self):
#         df = sdo_final_banco_invico.SdoFinalBancoINVICO()
#         df.update_sql_db(
#             self.input_path + '/saldos_sscc',
#             output_path=self.output_path, clean_first=True)

#     # --------------------------------------------------
#     def update_ctas_ctes(self):
#         df = ctas_ctes.CtasCtes()
#         df.update_sql_db(
#             self.input_path + '/cta_cte/cta_cte.xlsx',
#             output_path=self.output_path, clean_first=True)

# --------------------------------------------------
def get_args():
    """Get needed params from user input"""
    parser = argparse.ArgumentParser(
        description = "Upload DataFrame to Google Sheets",
        formatter_class = argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        '-s', '--spreadsheet_key', 
        metavar = "spreadsheet_key",
        type=str,
        help = "can be found in the URL of a previously created sheet")

    parser.add_argument(
        '-c', '--credentials', 
        metavar = "json_credentials",
        default='google_credentials.json',
        type=str,
        help = "Google's json file credentials name. Must be in the same folder")

    parser.add_argument(
        '-w', '--wks_name', 
        metavar = "worksheet_name",
        default= None,
        type=str,
        help = "worksheet_name")

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
    if args.input_path == None:
        input_path = HanglingPath().get_update_path_input()
    else:
        input_path = args.input_path

    if args.output_path == None:
        output_path = HanglingPath().get_db_path()
    else:
        output_path = args.output_path

    test = EjecucionObras(
        input_path=input_path, db_path=output_path,
        update_db= True
    )
    df = test.import_siif_obras_desc()

    gs = GoogleSheets(args.credentials)
    gs.to_google_sheets(
        df,  
        spreadsheet_key = args.spreadsheet_key,
        wks_name = args.wks_name
    )



# --------------------------------------------------
if __name__ == '__main__':
    main()
    # From invicoDB.src
    # python -m invicodb.upload_db
