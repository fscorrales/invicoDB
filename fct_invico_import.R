#SETUP---------------------

##In Windows, there is no distinction between lowercase 
##and uppercase DB' name (Beware)

##LOAD LIBRARY
library(invicodatr)
library(magrittr)

##INPUT & OUTOPUT PATH
input_path <- paste(getwd(), "Base de Datos",sep = "/") # Does I need it?
#output_path define inside invicodatr (Should I change it?)
div_path <- function(full_path){
  
  Ans <- stringr::str_split(full_path, "/", simplify = T) %>%
    as.vector()
  
}

output_path <- function(){
  
  # Ans <- stringr::str_split(getwd(), "/", simplify = T)
  Ans <- div_path(getwd())
  Ans <- Ans[1:(length(Ans)-1)] %>%
    sapply(function(x) paste0(x, "/")) %>%
    paste(collapse = "") %>%
    paste0("R Output")
  
  return(Ans)
  
}

#Primary Key -----

##Primary Key Cuentas Corrientes
cta_cte <- rpw_cta_cte("Base de Datos/Primary Key/primary_key_cta_cte.xlsx",
                       write_csv = TRUE, write_sqlite = TRUE)

#INVICO Sistema de Seguimiento de Cuentas Corrientes (SSCC)-------

##BD Mov SSCC (INVICO)
sscc_banco_invico <- rpw_sscc_banco_invico(
  dir("Base de Datos/Sistema de Seguimiento de Cuentas Corrientes/Movimientos Generales SSCC/", 
      full.names = TRUE), 
  write_csv = TRUE, write_sqlite = TRUE)

##Importamos Imputaciones SSCC (INVICO) - NOT Working yet

###Joinning Mov SSCC + Imputaciones SSCC (not working yet)

#INVICO Sistema Gestion Financiera (SGF)-------

##Resumen de Rendiciones INVICO SGF
sgf_resumen_rend_prov <- rpw_sgf_resumen_rend_prov(
  dir("Base de Datos/Sistema Gestion Financiera/Resumen de Rendiciones SGF/", 
      full.names = TRUE), 
  write_csv = TRUE, write_sqlite = TRUE)

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

#SIIF RECURSOS--------- 

##Recursos SIIF (rci02)
siif_comprobantes_rec <- rpw_siif_comprobantes_rec(
  dir("Base de Datos/Reportes SIIF/Comprobantes de Recursos (rci02)/", 
      full.names = TRUE), 
  write_csv = TRUE, write_sqlite = TRUE)

##Recursos SIIF por Código (ri102) - NOT Working yet

#SIIF CONTABILIDAD--------------

##Movimientos Contables SIIF (rcocc31)
siif_mayor_contable <- rpw_siif_mayor_contable(
  dir("Base de Datos/Reportes SIIF/Movimientos Contables (rcocc31)/", 
      full.names = TRUE), 
  write_csv = TRUE, write_sqlite = TRUE)
#ICARO ------

##Transmute old ICARO DB to new version (I put the old version
##outsite of SQLite Files to prevent overwritting)

icaro <- transmute_icaro_old_to_new(
  paste0(output_path(), "/ICARO.sqlite"), 
  write_csv = TRUE, write_sqlite = TRUE)

