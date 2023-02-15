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
class UploadGoogleSheet():
    """Upload DataFrame to Google Sheets
    :param path_credentials_file: json file download from Google
    :param update_db: Should sqlite files be updated?
    :param input_path: If update_db is True '/Base de Datos' path must be given
    :param output_path: If update_db is True 'Python Output/SQLite Files' must be given
    """
    path_credentials_file:str
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
        """Update and Upload all DataFrames"""
        self.upload_ejecucion_pres()

    # --------------------------------------------------
    def upload_ejecucion_pres(self):
        """Update and Upload Ejecucion Presupuestaria"""
        ejecucion_obras = EjecucionObras(
            input_path=self.input_path, db_path=self.output_path,
            update_db= self.update_db
        )
        self.df = ejecucion_obras.import_siif_obras_desc()
        spreadsheet_key = '1SRmgep84KGJNj_nKxiwXLe28gVUiIu2Uha4j_C7BzeU'
        wks_name = 'siif_ejec_obras'
        self.gs.to_google_sheets(
            self.df,  
            spreadsheet_key = spreadsheet_key,
            wks_name = wks_name
        )
        print('-- Ejecucion Obras --')
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

    test = UploadGoogleSheet(
        path_credentials_file=google_credentials_path,
        update_db=False,
        input_path=input_path,
        output_path=output_path
    )
    test.upload_ejecucion_pres()



# --------------------------------------------------
if __name__ == '__main__':
    main()
    # From invicoDB.src
    # python -m invicodb.upload_db
