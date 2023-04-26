#!/usr/bin/env python3
"""
Author: Fernando Corrales <fscorrales@gmail.com>
Purpose: Update set of INVICO DB' sqlite files
Packages:
 - invicodatpy (pip install -e '/home/kanou/IT/R Apps/R Gestion INVICO/invicodatpy')
"""
import argparse
import os
from dataclasses import dataclass

from invicodatpy.icaro import *
from invicodatpy.sgf import *
from invicodatpy.siif import *
from invicodatpy.slave import *
from invicodatpy.sscc import *
from invicodatpy.sgv import *

from ..hangling_path import HanglingPath


# --------------------------------------------------
@dataclass
class UpdateSIIF():
    """Read, process and write INVICO DB"""
    input_path:str
    output_path:str

    # --------------------------------------------------
    def update_all_siif_tables(self):
        print("-- Iniciando proceso de actualización de DB SIIF --")
        self.update_comprobantes_gtos_rcg01_uejp()
        self.update_comprobantes_gtos_gpo_part_gto_rpa03g()
        self.update_comprobantes_rec_rci02()
        self.update_deuda_flotante_rdeu012()
        self.update_deuda_flotante_rdeu012b2_c()
        self.update_mayor_contable_rcocc31()
        self.update_ppto_gtos_desc_rf610()
        self.update_ppto_gtos_fte_rf602()
        self.update_resumen_fdos_rfondo07tp()
        self.update_detalle_partidas_rog01() 

    # --------------------------------------------------
    def update_comprobantes_gtos_rcg01_uejp(self):
        print("- Actualizando SIIF's rcg01_uejp -")
        df = comprobantes_gtos_rcg01_uejp.ComprobantesGtosRcg01Uejp()
        df.update_sql_db(
            self.input_path + '/Comprobantes de Gastos (rcg01_uejp)',
            output_path=self.output_path, clean_first=True)

    # --------------------------------------------------
    def update_comprobantes_gtos_gpo_part_gto_rpa03g(self):
        print("- Actualizando SIIF's gto_rpa03g -")
        df = comprobantes_gtos_gpo_part_gto_rpa03g.ComprobantesGtosGpoPartGtoRpa03g()
        df.update_sql_db(
            self.input_path + '/Comprobantes de Gastos por Grupo Partida (gto_rpa03g)',
            output_path=self.output_path, clean_first=True)

    # --------------------------------------------------
    def update_comprobantes_rec_rci02(self):
        print("- Actualizando SIIF's rec_rci02 -")
        df = comprobantes_rec_rci02.ComprobantesRecRci02()
        df.update_sql_db(
            self.input_path + '/Comprobantes de Recursos (rci02)',
            output_path=self.output_path, clean_first=True)

    # --------------------------------------------------
    def update_deuda_flotante_rdeu012(self):
        print("- Actualizando SIIF's rdeu012 -")
        df = deuda_flotante_rdeu012.DeudaFlotanteRdeu012()
        df.update_sql_db(
            self.input_path + '/Deuda Flotante (rdeu)',
            output_path=self.output_path, clean_first=True)

    # --------------------------------------------------
    def update_deuda_flotante_rdeu012b2_c(self):
        print("- Actualizando SIIF's rdeu012b2_c -")
        df = deuda_flotante_rdeu012b2_c.DeudaFlotanteRdeu012b2C()
        df.update_sql_db(
            self.input_path + '/Deuda Flotante TG (rdeu012b2_C)',
            output_path=self.output_path, clean_first=True)

    # --------------------------------------------------
    def update_mayor_contable_rcocc31(self):
        print("- Actualizando SIIF's rcocc31 -")
        df = mayor_contable_rcocc31.MayorContableRcocc31()
        df.update_sql_db(
            self.input_path + '/Movimientos Contables (rcocc31)',
            output_path=self.output_path, clean_first=True)

    # --------------------------------------------------
    def update_ppto_gtos_desc_rf610(self):
        print("- Actualizando SIIF's rf610 -")
        df = ppto_gtos_desc_rf610.PptoGtosDescRf610()
        df.update_sql_db(
            self.input_path + '/Ejecucion Presupuestaria con Descripcion (rf610)',
            output_path=self.output_path, clean_first=True)

    # --------------------------------------------------
    def update_ppto_gtos_fte_rf602(self):
        print("- Actualizando SIIF's rf602 -")
        df = ppto_gtos_fte_rf602.PptoGtosFteRf602()
        df.update_sql_db(
            self.input_path + '/Ejecucion Presupuestaria con Fuente (rf602)',
            output_path=self.output_path, clean_first=True)

    # --------------------------------------------------
    def update_resumen_fdos_rfondo07tp(self):
        print("- Actualizando SIIF's rfondo07tp -")
        df = resumen_fdos_rfondo07tp.ResumenFdosRfondo07tp()
        df.update_sql_db(
            self.input_path + '/Comprobantes de Fondos Regularizados por Tipo (rfondo07tp)',
            output_path=self.output_path, clean_first=True)
        
    # --------------------------------------------------
    def update_detalle_partidas_rog01(self):
        print("- Actualizando SIIF's rog01 -")
        df = detalle_partidas_rog01.DetallePartidasRog01()
        df.update_sql_db(
            self.input_path + '/Listado Partidas (rog01)',
            output_path=self.output_path, clean_first=True)

# --------------------------------------------------
@dataclass
class UpdateSGF():
    """Read, process and write INVICO DB"""
    input_path:str
    output_path:str

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

# --------------------------------------------------
@dataclass
class UpdateSSCC():
    input_path:str
    output_path:str
    """Read, process and write INVICO DB"""

    # --------------------------------------------------
    def update_all_sscc_tables(self):
        print("-- Iniciando proceso de actualización de DB SSCC --")
        self.update_banco_invico()
        self.update_ctas_ctes()
        self.update_sdo_final_banco_invico()

    # --------------------------------------------------
    def update_banco_invico(self):
        print("- Actualizando SSCC's Banco INVICO -")
        df = banco_invico.BancoINVICO()
        df.update_sql_db(
            self.input_path + '/Movimientos Generales SSCC',
            output_path=self.output_path, clean_first=True)

    # --------------------------------------------------
    def update_sdo_final_banco_invico(self):
        print("- Actualizando SSCC's Saldo Final Banco INVICO -")
        df = sdo_final_banco_invico.SdoFinalBancoINVICO()
        df.update_sql_db(
            self.input_path + '/saldos_sscc',
            output_path=self.output_path, clean_first=True)

    # --------------------------------------------------
    def update_ctas_ctes(self):
        print("- Actualizando SSCC's Ctas Ctes -")
        df = ctas_ctes.CtasCtes()
        df.update_sql_db(
            self.input_path + '/cta_cte/cta_cte.xlsx',
            output_path=self.output_path, clean_first=True)

# --------------------------------------------------
@dataclass
class UpdateIcaro():
    """Read, process and write INVICO DB"""
    input_path:str
    output_path:str

    # --------------------------------------------------
    def migrate_icaro(self):
        print("-- Actualizando Icaro' DB --")
        migrate_icaro.MigrateIcaro(
            self.input_path, self.output_path
        ).migrate_all()

# --------------------------------------------------
@dataclass
class UpdateSlave():
    """Read, process and write SLAVE DB from mdb to sqlite"""
    input_path:str
    output_path:str

    # --------------------------------------------------
    def migrate_slave(self):
        migrate_slave.MigrateSlave(
            self.input_path, self.output_path
        ).migrate_all()

# --------------------------------------------------
@dataclass
class UpdateSGV():
    """Read, process and write INVICO DB"""
    input_path:str
    output_path:str

    # --------------------------------------------------
    def update_all_sgv_tables(self):
        self.update_barrios_nuevos()
        self.update_resumen_facturado()
        self.update_resumen_recaudado()
        self.update_saldo_barrio_variacion()
        self.update_saldo_barrio()
        self.update_saldo_motivo()
        self.update_saldo_motivo_entrega_viviendas()
        self.update_saldo_motivo_actualizacion_semestral()
        self.update_saldo_recuperos_cobrar_variacion()

    # --------------------------------------------------
    def update_barrios_nuevos(self):
        df = barrios_nuevos.BarriosNuevos()
        df.update_sql_db(
            self.input_path + '/Barrios Nuevos',
            output_path=self.output_path, clean_first=True)

    # --------------------------------------------------
    def update_resumen_facturado(self):
        df = resumen_facturado.ResumenFacturado()
        df.update_sql_db(
            self.input_path + '/Resumen Facturado',
            output_path=self.output_path, clean_first=True)

    # --------------------------------------------------
    def update_resumen_recaudado(self):
        df = resumen_recaudado.ResumenRecaudado()
        df.update_sql_db(
            self.input_path + '/Resumen Recaudado',
            output_path=self.output_path, clean_first=True)

    # --------------------------------------------------
    def update_saldo_barrio_variacion(self):
        df = saldo_barrio_variacion.SaldoBarrioVariacion()
        df.update_sql_db(
            self.input_path + '/Evolucion de Saldo Por Barrio',
            output_path=self.output_path, clean_first=True)

    # --------------------------------------------------
    def update_saldo_barrio(self):
        df = saldo_barrio.SaldoBarrio()
        df.update_sql_db(
            self.input_path + '/Saldo por Barrio',
            output_path=self.output_path, clean_first=True)

    # --------------------------------------------------
    def update_saldo_motivo(self):
        df = saldo_motivo.SaldoMotivo()
        df.update_sql_db(
            self.input_path + '/Evolucion de Saldo Por Motivo',
            output_path=self.output_path, clean_first=True)

    # --------------------------------------------------
    def update_saldo_motivo_entrega_viviendas(self):
        df = saldo_motivo_entrega_viviendas.SaldoMotivoEntregaViviendas()
        df.update_sql_db(
            self.input_path + '/Motivo Entrega de Viviendas',
            output_path=self.output_path, clean_first=False)

    # --------------------------------------------------
    def update_saldo_motivo_actualizacion_semestral(self):
        df = saldo_motivo_actualizacion_semestral.SaldoMotivoActualizacionSemestral()
        df.update_sql_db(
            self.input_path + '/Motivo Actualizacion Semestral',
            output_path=self.output_path, clean_first=False)

    # --------------------------------------------------
    def update_saldo_recuperos_cobrar_variacion(self):
        df = saldo_recuperos_cobrar_variacion.SaldoRecuperosCobrarVariacion()
        df.update_sql_db(
            self.input_path + '/Variación de Saldos Recuperos A Cobrar',
            output_path=self.output_path, clean_first=True)

# --------------------------------------------------
def get_args():
    """Get needed params from user input"""
    parser = argparse.ArgumentParser(
        description = "Read, process and write INVICO DB",
        formatter_class = argparse.ArgumentDefaultsHelpFormatter)

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

    UpdateSIIF(
        os.path.join(input_path, 'Reportes SIIF'), 
        os.path.join(output_path, 'siif.sqlite')
        ).update_all_siif_tables()
    UpdateSGF(
        os.path.join(input_path, 'Sistema Gestion Financiera'), 
        os.path.join(output_path, 'sgf.sqlite')
        ).update_all_sgf_tables()
    UpdateSSCC(
        os.path.join(input_path, 'Sistema de Seguimiento de Cuentas Corrientes'), 
        os.path.join(output_path,'sscc.sqlite')
    ).update_all_sscc_tables()
    UpdateIcaro(
        os.path.join(HanglingPath().get_outside_path(),
        'R Output/SQLite Files/ICARO.sqlite'), 
        os.path.join(output_path, 'icaro.sqlite')
        ).migrate_icaro()
    # UpdateSlave(
    #     os.path.join(input_path, 'Slave/Slave.mdb'), 
    #     os.path.join(output_path, 'slave.sqlite')
    #     ).migrate_slave()
    # UpdateSGV(
    #     os.path.join(input_path, 'Gestión Vivienda GV/Sistema Recuperos GV'), 
    #     os.path.join(output_path, 'sgv.sqlite')
    #     ).update_all_sgv_tables()
        
# --------------------------------------------------
if __name__ == '__main__':
    main()
    # From invicoDB.src
    # python -m invicodb.update.update_db
