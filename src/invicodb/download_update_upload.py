#!/usr/bin/env python3
"""
Author: Fernando Corrales <fscorrales@gmail.com>
Purpose: Download, Update and Upload set of INVICO DB' sqlite files to Google Sheets
Packages:
 - invicodatpy (pip install '/home/kanou/IT/R Apps/R Gestion INVICO/invicodatpy')
"""

import os

from .download.download_db import (CopyIcaro, DownloadSGF, DownloadSIIF,
                                   DownloadSSCC)
from .hangling_path import HanglingPath
from .update.update_db import UpdateIcaro, UpdateSGF, UpdateSIIF, UpdateSSCC
from .upload.upload_db import UploadGoogleSheet


# --------------------------------------------------
def main():
    """Let's try it"""
    
    # Download module
    output_path = HanglingPath().get_update_path_input()
    credentials_path = HanglingPath().get_invicodb_path()
    credentials_path = os.path.join(
        credentials_path, 'download'
    )

    siif_credentials_path = os.path.join(
        credentials_path, 'siif_credentials.json'
    )

    DownloadSIIF(
        path_credentials_file=siif_credentials_path,
        output_path=os.path.join(output_path, 'Reportes SIIF')
        ).download_all_siif_tables()

    invico_credentials_path = os.path.join(
        credentials_path, 'invico_credentials.json'
    )

    DownloadSSCC(
        path_credentials_file=invico_credentials_path,
        output_path=os.path.join(output_path, 'Sistema de Seguimiento de Cuentas Corrientes')
        ).download_all_sscc_tables()

    DownloadSGF(
        path_credentials_file=invico_credentials_path,
        output_path=os.path.join(output_path, 'Sistema Gestion Financiera')
        ).download_all_sgf_tables()

    output_path = HanglingPath().get_outside_path()
    exequiel_path = HanglingPath().get_exequiel_path()

    CopyIcaro(
        exequiel_path= os.path.join(exequiel_path, 'ICARO.sqlite'),
        my_path= os.path.join(output_path, 'R Output/SQLite Files/ICARO.sqlite')
    )

    # Update module
    input_path = HanglingPath().get_update_path_input()
    output_path = HanglingPath().get_db_path()

    UpdateSIIF(
        os.path.join(input_path, 'Reportes SIIF'), 
        os.path.join(output_path, 'siif.sqlite')
        ).update_all_siif_tables()

    UpdateSSCC(
        os.path.join(input_path, 'Sistema de Seguimiento de Cuentas Corrientes'), 
        os.path.join(output_path,'sscc.sqlite')
    ).update_all_sscc_tables()

    UpdateSGF(
        os.path.join(input_path, 'Sistema Gestion Financiera'), 
        os.path.join(output_path,'sgf.sqlite')
    ).update_all_sscc_tables()

    UpdateIcaro(
        os.path.join(HanglingPath().get_outside_path(),
        'R Output/SQLite Files/ICARO.sqlite'), 
        os.path.join(output_path, 'icaro.sqlite')
        ).migrate_icaro()

    # Upload module
    input_path = HanglingPath().get_update_path_input()
    output_path = HanglingPath().get_db_path()
    google_credentials_path = HanglingPath().get_invicodb_path()
    google_credentials_path = os.path.join(
        google_credentials_path, 'upload'
    )
    google_credentials_path = os.path.join(
        google_credentials_path, 'google_credentials.json'
    )

    UploadGoogleSheet(
        path_credentials_file=google_credentials_path,
        ejercicio='2023',
        update_db=False,
        input_path=input_path,
        output_path=output_path
    ).upload_all_dfs()
    
# --------------------------------------------------
if __name__ == '__main__':
    main()
    # From invicoDB.src
    # python -m invicodb.download_update_upload
