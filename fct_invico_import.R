#SETUP---------------------

##LOAD LIBRARY
library(invicodatr)

##INPUT & OUTOPUT PATH
input_path <- paste(getwd(), "Base de Datos",sep = "/") # Does I need it?
#output_path define inside invicodatr (Should I change it?)

#INVICO-------

##as

#SIIF--------

##Ejecución Presupuestaria con Fuente SIIF (rf602)
siif_ppto_gtos_fte <- rpw_siif_ppto_gtos_fte(
  dir("Base de Datos/Reportes SIIF/Ejecucion Presupuestaria con Fuente (rf602)/", 
      full.names = TRUE), 
  write_csv = TRUE, write_sqlite = TRUE)



