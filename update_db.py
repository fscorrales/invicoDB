#!/usr/bin/env python3
"""
Author: Fernando Corrales <fscorrales@gmail.com>
Purpose: Update set of INVICO DB' sqlite files
Packages:
 - invicodatpy (pip install '/home/kanou/IT/R Apps/R Gestion INVICO/invicodatpy')
"""

import argparse
import inspect
import os

from invicodatpy.icaro import *
from invicodatpy.sgf import *
from invicodatpy.siif import *
from invicodatpy.sscc import *


class UpdateDB():
    def __init__(self, output_path:str = None) -> None:
        self.get_working_directory()
        if output_path == None:
            self.get_output_path()

    def get_working_directory(self):
        self.dir_path = os.path.dirname(
            os.path.abspath(
                inspect.getfile(
                    inspect.currentframe())))
        self.input_path = self.dir_path + '/Base de Datos' 
        return self.input_path

    def get_output_path(self):
        self.output_path = (os.path.dirname(self.dir_path) +
        '/Python Output/SQLite Files')
        return self.output_path

class UpdateSIIF(UpdateDB):
    """Read, process and write INVICO DB"""
    def __init__(self, output_path:str = None) -> None:
        super().__init__(output_path=output_path)
        self.input_path += '/Reportes SIIF'
        self.output_path += '/siif.sqlite'

    # --------------------------------------------------
    def update_all_siif_tables(self):
        self.update_comprobantes_gtos_rcg01_uejp()
        self.update_comprobantes_gtos_gpo_part_gto_rpa03g()
        self.update_comprobantes_rec_rci02()
        self.update_deuda_flotante_rdeu012()
        self.update_mayor_contable_rcocc31()
        self.update_ppto_gtos_desc_rf610()
        self.update_ppto_gtos_fte_rf602()
        self.update_resumen_fdos_rfondo07tp() 

    # --------------------------------------------------
    def update_comprobantes_gtos_rcg01_uejp(self):
        df = comprobantes_gtos_rcg01_uejp.ComprobantesGtosRcg01Uejp()
        df.update_sql_db(
            self.input_path + '/Comprobantes de Gastos (rcg01_uejp)',
            output_path=self.output_path, clean_first=True)

    # --------------------------------------------------
    def update_comprobantes_gtos_gpo_part_gto_rpa03g(self):
        df = comprobantes_gtos_gpo_part_gto_rpa03g.ComprobantesGtosGpoPartGtoRpa03g()
        df.update_sql_db(
            self.input_path + '/Comprobantes de Gastos por Grupo Partida (gto_rpa03g)',
            output_path=self.output_path, clean_first=True)

    # --------------------------------------------------
    def update_comprobantes_rec_rci02(self):
        df = comprobantes_rec_rci02.ComprobantesRecRci02()
        df.update_sql_db(
            self.input_path + '/Comprobantes de Recursos (rci02)',
            output_path=self.output_path, clean_first=True)

    # --------------------------------------------------
    def update_deuda_flotante_rdeu012(self):
        df = deuda_flotante_rdeu012.DeudaFlotanteRdeu012()
        df.update_sql_db(
            self.input_path + '/Deuda Flotante (rdeu)',
            output_path=self.output_path, clean_first=True)

    # --------------------------------------------------
    def update_mayor_contable_rcocc31(self):
        df = mayor_contable_rcocc31.MayorContableRcocc31()
        df.update_sql_db(
            self.input_path + '/Movimientos Contables (rcocc31)',
            output_path=self.output_path, clean_first=True)

    # --------------------------------------------------
    def update_ppto_gtos_desc_rf610(self):
        df = ppto_gtos_desc_rf610.PptoGtosDescRf610()
        df.update_sql_db(
            self.input_path + '/Ejecucion Presupuestaria con Descripcion (rf610)',
            output_path=self.output_path, clean_first=True)

    # --------------------------------------------------
    def update_ppto_gtos_fte_rf602(self):
        df = ppto_gtos_fte_rf602.PptoGtosFteRf602()
        df.update_sql_db(
            self.input_path + '/Ejecucion Presupuestaria con Fuente (rf602)',
            output_path=self.output_path, clean_first=True)

    # --------------------------------------------------
    def update_resumen_fdos_rfondo07tp(self):
        df = resumen_fdos_rfondo07tp.ResumenFdosRfondo07tp()
        df.update_sql_db(
            self.input_path + '/Comprobantes de Fondos Regularizados por Tipo (rfondo07tp)',
            output_path=self.output_path, clean_first=True)

class UpdateSGF(UpdateDB):
    """Read, process and write INVICO DB"""
    def __init__(self, output_path:str = None) -> None:
        super().__init__(output_path=output_path)
        self.input_path += '/Sistema Gestion Financiera'
        self.output_path += '/sgf.sqlite'

    # --------------------------------------------------
    def update_all_sgf_tables(self):
        self.update_certificados_obras()
        self.update_listado_prov()
        self.update_resumen_rend_obras()
        self.update_resumen_rend_prov()

    # --------------------------------------------------
    def update_certificados_obras(self):
        df = certificados_obras.CertificadosObras()
        df.update_sql_db(
            self.input_path + '/Informe para Contable SGF',
            output_path=self.output_path, clean_first=True)

    # --------------------------------------------------
    def update_listado_prov(self):
        df = listado_prov.ListadoProv()
        df.update_sql_db(
            self.input_path + '/Otros Reportes/Listado de Proveedores.csv',
            output_path=self.output_path, clean_first=True)

    # --------------------------------------------------
    def update_resumen_rend_obras(self):
        df = resumen_rend_obras.ResumenRendObras()
        df.update_sql_db(
            self.input_path + '/Resumen de Rendiciones EPAM por OBRA SGF',
            output_path=self.output_path, clean_first=True)

    # --------------------------------------------------
    def update_resumen_rend_prov(self):
        df = resumen_rend_prov.ResumenRendProv()
        df.update_sql_db(
            self.input_path + '/Resumen de Rendiciones SGF',
            output_path=self.output_path, clean_first=True)

class UpdateSSCC(UpdateDB):
    """Read, process and write INVICO DB"""
    def __init__(self, output_path:str = None) -> None:
        super().__init__(output_path=output_path)
        self.input_path += '/Sistema de Seguimiento de Cuentas Corrientes'
        self.output_path += '/sscc.sqlite'

    # --------------------------------------------------
    def update_all_sscc_tables(self):
        self.update_banco_invico()
        self.update_ctas_ctes()

    # --------------------------------------------------
    def update_banco_invico(self):
        df = banco_invico.BancoINVICO()
        df.update_sql_db(
            self.input_path + '/Movimientos Generales SSCC',
            output_path=self.output_path, clean_first=True)

    # --------------------------------------------------
    def update_ctas_ctes(self):
        df = ctas_ctes.CtasCtes()
        df.update_sql_db(
            self.input_path + '/cta_cte/cta_cte.xlsx',
            output_path=self.output_path, clean_first=True)

class UpdateIcaro(UpdateDB):
    """Read, process and write INVICO DB"""
    def __init__(self, output_path:str = None) -> None:
        super().__init__(output_path=output_path)
        self.input_path = (os.path.dirname(self.dir_path) +
        '/R Output/SQLite Files/ICARO.sqlite')
        self.output_path += '/icaro.sqlite'
        migrate_icaro.MigrateIcaro(
            self.input_path, self.output_path
        ).migrate_all()

# --------------------------------------------------
def get_args():
    """Get needed params from user input"""
    parser = argparse.ArgumentParser(
        description = "Read, process and write INVICO DB",
        formatter_class = argparse.ArgumentDefaultsHelpFormatter)

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
    UpdateSIIF(args.output_path).update_all_siif_tables()
    UpdateSGF(args.output_path).update_all_sgf_tables()
    UpdateSSCC(args.output_path).update_all_sscc_tables()
    UpdateIcaro(args.output_path)

# --------------------------------------------------
if __name__ == '__main__':
    main()
    # From invicoDB
    # python update_db.py