#SETUP---------------------

##LOAD LIBRARY
library(invicodatr)

##INPUT & OUTOPUT PATH
input_path <- paste(getwd(), "Base de Datos",sep = "/") # Does I need it?
#output_path define inside invicodatr (Should I change it?)

#INVICO-------

##as

#SIIF GASTOS--------

##Ejecución Presupuestaria con Fuente SIIF (rf602)
siif_ppto_gtos_fte <- rpw_siif_ppto_gtos_fte(
  dir("Base de Datos/Reportes SIIF/Ejecucion Presupuestaria con Fuente (rf602)/", 
      full.names = TRUE), 
  write_csv = TRUE, write_sqlite = TRUE)

##Ejecución Presupuestaria con Descripcion SIIF (rf610)
siif_ppto_gtos_desc <- rpw_siif_ppto_gtos_desc(
  dir("Base de Datos/Reportes SIIF/Ejecucion Presupuestaria con Descripcion (rf610)/", 
      full.names = TRUE), 
  write_csv = TRUE, write_sqlite = TRUE)

###Joinning rf602 and rf610 (not working yet)

##Comprobantes Gastos Ingresados (rcg01_uejp)
siif_comprobantes_gtos <- rpw_siif_comprobantes_gtos(
  dir("Base de Datos/Reportes SIIF/Comprobantes de Gastos (rcg01_uejp)/", 
      full.names = TRUE), 
  write_csv = TRUE, write_sqlite = TRUE)

###Filter MAP from rcg01_uejp (Should I do it? NOT working yet)

##Comprobantes Gastos Ingresados con Partida sin REM (rcg01_par) - WARNING not working well (solo comprobantes pagados?)
siif_comprobantes_gtos_partida <- rpw_siif_comprobantes_gtos_partida(
  dir("Base de Datos/Reportes SIIF/Comprobantes de Gastos con Partida Pagados sin REM (rcg01_par)/", 
      full.names = TRUE), 
  write_csv = TRUE, write_sqlite = TRUE)

###Joinning rcg01_par + REM rcg01_uejp (not working yet)

##Comprobantes Gastos Ingresados por Grupo Partida (gto_rpa03g)
siif_comprobantes_gtos_gpo_partida <- rpw_siif_comprobantes_gtos_gpo_partida(
  dir("Base de Datos/Reportes SIIF/Comprobantes de Gastos por Grupo Partida (gto_rpa03g)/", 
      full.names = TRUE), 
  write_csv = TRUE, write_sqlite = TRUE)

###Joinning gto_rpa03g + rcg01_uejp (not working yet)

##Listado Analitico Retenciones SIIF (rao01)
siif_retenciones_por_codigo <- rpw_siif_retenciones_por_codigo(
  dir("Base de Datos/Reportes SIIF/Listado Retenciones Practicadas por Codigo (rao01)/", 
      full.names = TRUE), 
  write_csv = TRUE, write_sqlite = TRUE)

###Joinning rcg01_uejp + rao01 (not working yet)

##Resumen de Fondo SIIF (rfondo07tp)
siif_resumen_fdos <- rpw_siif_resumen_fdos(
  dir("Base de Datos/Reportes SIIF/Comprobantes de Fondos Regularizados por Tipo (rfondo07tp)/", 
      full.names = TRUE), 
  write_csv = TRUE, write_sqlite = TRUE)

##Deuda Flotante SIIF (rdeu012)
siif_deuda_flotante <- rpw_siif_deuda_flotante(
  dir("Base de Datos/Reportes SIIF/Deuda Flotante (rdeu)/", 
      full.names = TRUE), 
  write_csv = TRUE, write_sqlite = TRUE)

##Deuda Flotante SIIF TG (rdeu012b2_C)
siif_deuda_flotante_tg <- rpw_siif_deuda_flotante_tg(
  dir("Base de Datos/Reportes SIIF/Deuda Flotante TG (rdeu012b2_C)/", 
      full.names = TRUE), 
  write_csv = TRUE, write_sqlite = TRUE)

##Listado de Pagos Tesorería SIIF (rtr03)
siif_pagos <- rpw_siif_pagos(
  dir("Base de Datos/Reportes SIIF/Listado Pagos Tesoreria (rtr03)/", 
      full.names = TRUE), 
  write_csv = TRUE, write_sqlite = TRUE)
