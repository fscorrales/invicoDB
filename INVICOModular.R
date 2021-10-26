#SETUP INICIAL---------------------
##Cargamos Librarías
library(tidyverse)
library(lubridate)
library(RSQLite)
library(DBI)
# library(readxl)

##INPUT & OUTOPUT PATH
output_path <- str_split(getwd(), "/", simplify = T)
output_path <- output_path[1:(length(output_path)-1)] %>% 
  sapply(function(x) paste0(x, "/")) %>% 
  paste(collapse = "") %>% 
  paste0("R Output")

input_path <- paste(getwd(), "Base de Datos",sep = "/") 


##Funciones Personalizadas
cbind.fill <- function(...) {                                                                                                                                                       
  transpoted <- lapply(list(...),t)                                                                                                                                                 
  transpoted_dataframe <- lapply(transpoted, as.data.frame)                                                                                                                         
  return (data.frame(t(plyr::rbind.fill(transpoted_dataframe))))                                                                                                                          
}

ConectarBD <-function(DBName){
  
  Archivo <- paste0(output_path, "/SQLite Files/", DBName, ".sqlite")
  con <- dbConnect(SQLite(), dbname = Archivo)
  
}

DesconectarBD <-function(ConexionActiva){
  
  DBI::dbDisconnect(ConexionActiva)
  
}

AgregarRegistrosBD <- function(DB, Tabla, Data, append = FALSE, 
                               overwrite = FALSE) {
  
  con <- ConectarBD(DB)
  DBI::dbWriteTable(con, name = Tabla, value = Data,
                    append = append, overwrite = overwrite)
  DesconectarBD(con)
  
}

OrdenarTablaBD <- function(DB, TablaOrdenar, strSQLOrderBy = "") {
  
  con <- ConectarBD(DB)
  SQLquery <- paste0("CREATE TABLE COPY AS SELECT * FROM ",
                     TablaOrdenar , " ", 
                     "ORDER BY " , strSQLOrderBy)
  DBI::dbExecute(con, SQLquery)
  SQLquery <- paste0("DROP TABLE ", TablaOrdenar)
  DBI::dbExecute(con, SQLquery)
  SQLquery <- paste0("ALTER TABLE COPY RENAME TO ", TablaOrdenar)
  DBI::dbExecute(con, SQLquery)
  DesconectarBD(con)
  
}

LeerBD <- function(DB, Tabla) {
  
  con <- ConectarBD(DB)
  Ans <- dbReadTable(con, Tabla)
  DesconectarBD(con)
  return(Ans)
  
}

FiltrarBD <- function(DB, SQLquery, params = NULL) {
  
  con <- ConectarBD(DB)
  Ans <- dbGetQuery(con, SQLquery, params = params)
  DesconectarBD(con)
  return(Ans)
  
}

EjecutarBD <- function(DB, SQLquery, params = NULL) {
  
  con <- ConectarBD(DB)
  dbExecute(con, SQLquery, params = params)
  DesconectarBD(con)
  
}

writeCSV <- function(DT, file_name){
  
  file_dir <- paste0(output_path, "/CSV Files/", file_name)
  
  write_excel_csv(DT, file_dir)
  
}
  

#SISTEMAS INVICO---------------------------------------

##SISTEMA DE SEGUIMIENTO DE CUENTAS CORRIENTES
###Importamos la BD Mov SSCC (INVICO)
MovSSCC <- dir("Base de Datos/Sistema de Seguimiento de Cuentas Corrientes/Movimientos Generales SSCC/",
               full.names = T) %>% map_df(read_csv, col_names = F, 
                                          col_types = str_c(rep("c",33), collapse = ""), 
                                          locale = locale(encoding = 'ISO-8859-1'))

MovSSCC <- MovSSCC %>% select(X21:X29)
names(MovSSCC) <- c("Fecha","Movimiento","Cuenta", "Concepto", 
                    "Beneficiario","Moneda","Libramiento",
                    "Imputacion", "Monto")
MovSSCC <- MovSSCC %>% 
  mutate_all(., str_replace_all, pattern = "[\r\n]", replacement = "") %>% 
  mutate(Fecha = dmy(Fecha),
         Monto = round(parse_number(Monto), 2),
         Libramiento = ifelse(is.na(Libramiento), "", Libramiento), #Decidí reemplazar NAs con ""
         CodigoImputacion = parse_integer(str_sub(Imputacion, 1, 3)),
         Imputacion = str_sub(Imputacion, 5),
         EsCheque =  !is.na(as.numeric(Movimiento)),
         Mes = str_c(str_pad(month(Fecha), 2, pad = "0"),
                     year(Fecha), sep = "/"))
  # filter(!str_detect(Libramiento, "22766")) #Tengo un problema en excel con este registro

###Importamos Imputaciones SSCC (INVICO)
ImputacionesSSCC <- dir("Base de Datos/Sistema de Seguimiento de Cuentas Corrientes/Listado Imputaciones SSCC/",
                        full.names = T) %>% map_df(read_csv, col_names = F, 
                                                   col_types = str_c(rep("c",10), collapse = ""),
                                                   locale = locale(encoding = 'ISO-8859-1'))

ImputacionesSSCC <- ImputacionesSSCC %>% select(-X1:-X6)
names(ImputacionesSSCC) <- c("CodigoImputacion", "Imputacion",
                             "Tipo", "ImputacionFONAVI")
ImputacionesSSCC <- ImputacionesSSCC %>% 
  mutate(CodigoImputacion = parse_integer(CodigoImputacion))

###Combinamos Imputaciones con Movimientos SSCCC
MovSSCCconImputaciones <- left_join(MovSSCC, select(ImputacionesSSCC, -Imputacion))

##SISTEMA DE GESTIÓN FINANCIERA
###Importamos Resumen de Rendiciones INVICO SGF
readResumenRendSGF <- function(archivoCSV){
  BD <- read_csv(archivoCSV, col_names = F, 
                 col_types = str_c(rep("c",53), collapse = ""), 
                 locale = locale(encoding = 'ISO-8859-1'))
  
  Origen.vec <- str_split(str_split(BD$X7[1]," - ", simplify = T)[1],
                          " = ", simplify = T)[2] %>% 
    str_remove_all('\\"')
  
  BD <- BD %>% 
    mutate(Origen = Origen.vec)
  
  if (Origen.vec == "OBRAS") {
    BD <- BD %>%
      select(-X1:-X23) %>%
      select(-X37:-X47) %>% 
      rename(Beneficiario = X24, Cuenta = X25,
             LibramientoSGF = X26, Fecha = X27, Movimiento = X28,
             ImporteNeto = X36, Gcias = X30, Sellos = X31,
             IIBB = X32, SUSS = X33,
             INVICO = X34, Otras = X35, ImporteBruto = X29)
  } else {
    BD <- BD %>%
      select(-X1:-X26) %>%
      select(-X42:-X53) %>% 
      rename(Beneficiario = X27, Destino = X28, Cuenta = X29, 
             LibramientoSGF = X30, Fecha = X31, Movimiento = X32, 
             ImporteNeto = X33, Gcias = X34, Sellos = X35, 
             IIBB = X36, SUSS = X37, Seguro = X38,
             Salud = X39, Mutual = X40, ImporteBruto = X41)
  }
  BD <- BD %>%
    select(Origen, everything())
}
ResumenRendSGF <- dir("Base de Datos/Sistema Gestion Financiera/Resumen de Rendiciones SGF/",
                      full.names = T) %>% map_df(readResumenRendSGF)
ResumenRendSGF <- ResumenRendSGF %>%
  mutate(Fecha = dmy(Fecha),
         Movimiento = ifelse(Movimiento == "TRANSF.",
                             "DEBITO", Movimiento),
         Cuenta = ifelse(is.na(Cuenta) & Beneficiario == "CREDITO ESPECIAL",
                         "130832-07", Cuenta),
         ImporteNeto = round(parse_number(ImporteNeto), 2),
         Gcias = parse_number(Gcias),
         Sellos = parse_number(Sellos),
         IIBB = parse_number(IIBB),
         SUSS = parse_number(SUSS),
         Seguro = parse_number(Seguro),
         Salud = parse_number(Salud),
         Mutual = parse_number(Mutual),
         ImporteBruto = parse_number(ImporteBruto),
         INVICO = parse_number(INVICO),
         Otras = parse_number(Otras))

###Importamos Pago a Cuenta Contratistas SGF (es necesario ABRIR el archivo y GUARDAR COMO)
readPagoACuentaSGF <- function(archivoExcel){
  BD <- readxl::read_excel(archivoExcel,
                           col_types = "text",
                           col_names = paste("X", 1:16, sep = ""))
  
  BD <- BD %>% 
    mutate(Periodo = str_sub(X10[4], -4)) %>% 
    tail(-16) %>% 
    head(-4) %>% 
    filter(!is.na(X1)) %>% 
    mutate(Beneficiario = ifelse(is.na(X6), X1, NA))
  
  BD <- BD %>%
    transmute(Periodo = Periodo,
              Beneficiario = zoo::na.locf(Beneficiario),
              Obra = X1,
              NroCertificado = X6,
              Operatoria = ifelse(is.na(X7), X9, X7),
              Rubro = X10,
              MontoCertificado = X11,
              Retenciones = X12,
              ImporteAPagar = X13,
              ImportePagado = X14,
              Movimiento = X15,
              Fecha = X16) %>% 
    filter(!is.na(Operatoria))
  
  BD <- BD %>%
    mutate(Fecha =as.Date(parse_integer(Fecha), origin = "1899-12-30"),
           MontoCertificado = parse_double(MontoCertificado),
           Retenciones = parse_double(Retenciones),
           ImporteAPagar = parse_double(ImporteAPagar),
           ImportePagado = parse_double(ImportePagado),
           Movimiento = ifelse(Movimiento == "2", "DEBITO", Movimiento))
  
  ImportePagoAcum.vec <- BD %>%
    arrange(Beneficiario, Obra, MontoCertificado, Fecha, Movimiento) %>%
    group_by(Beneficiario, Obra, MontoCertificado) %>%
    group_map(~ cumsum(.x$ImportePagado)) %>%  simplify()
  
  BD <- BD %>%
    arrange(Beneficiario, Obra, MontoCertificado, Fecha, Movimiento) %>% 
    mutate(ImportePagoAcum = ImportePagoAcum.vec,
           RetencionesReal = ifelse(near(ImporteAPagar, ImportePagoAcum),
                                    Retenciones, 0))
  
}
PagoACuentaSGF <- dir("Base de Datos/Sistema Gestion Financiera/Pago a Cuenta Certificados de Obra SGF/",
                      full.names = T) %>% map_df(readPagoACuentaSGF)

###Creamos la columna Retenciones Reales en Resumen de Rendiciones SGF
ResumenRendSGFCompleto <- PagoACuentaSGF %>%
  select(Movimiento, Fecha, Beneficiario, ImportePagado, RetencionesReal) %>%
  rename(ImporteNeto = ImportePagado) %>% 
  left_join(ResumenRendSGF, .)

###Creamos la columna Reemplazado en Resumen de Rendiciones SGF
ResumenRendSGFCompleto <- MovSSCCconImputaciones %>%
  filter(CodigoImputacion == 55) %>%
  select(Cuenta, Movimiento, EsCheque) %>%
  left_join(ResumenRendSGFCompleto, .) %>% 
  rename(Reemplazado = EsCheque) %>% 
  mutate(Reemplazado = ifelse(!is.na(Reemplazado) & is.na(RetencionesReal), T, NA))

###Creamos la columna Reingresado en Resumen de Rendiciones SGF
ResumenRendSGFCompleto <- MovSSCCconImputaciones %>%
  filter(CodigoImputacion == 3, Libramiento != "0") %>%
  select(Cuenta, Libramiento, Monto, EsCheque) %>%
  rename(LibramientoSGF = Libramiento, ImporteNeto = Monto) %>%
  distinct() %>% 
  left_join(ResumenRendSGFCompleto, .) %>%
  rename(Reingresado = EsCheque) %>%
  mutate(Reingresado = ifelse(!is.na(Reingresado) & is.na(RetencionesReal), T, NA))

###Incluimos una columna de fecha o movimiento original
ResumenRendSGFCompleto <- ResumenRendSGFCompleto %>% 
  filter(Reemplazado == TRUE | Reingresado == TRUE) %>%
  mutate(Monto = ImporteNeto * (-1)) %>% 
  rename(Libramiento = LibramientoSGF) %>% 
  select(Beneficiario, Monto, Libramiento, Cuenta) %>% 
  semi_join(MovSSCCconImputaciones, .) %>%
  filter(CodigoImputacion != 55) %>% 
  select(Fecha, Movimiento, Cuenta, Beneficiario, Libramiento, Monto) %>% 
  distinct(Cuenta, Beneficiario, Libramiento, Monto, .keep_all = T) %>% 
  mutate(Monto = abs(Monto)) %>%
  rename(FechaOriginal = Fecha, MovimientoOriginal = Movimiento, 
         LibramientoSGF = Libramiento, ImporteNeto = Monto) %>% 
  left_join(ResumenRendSGFCompleto, .) %>% 
  mutate(FechaOriginal = if_else(is.na(FechaOriginal), Fecha, FechaOriginal),
         MovimientoOriginal = if_else(is.na(MovimientoOriginal), Movimiento, MovimientoOriginal))

###Creamos un Resumen de Rendiciones EXCLUSIVO de Factureros
HonorariosFacturerosSGF <- ResumenRendSGFCompleto %>% 
  filter((str_detect(Destino, "HONORARIOS") & !str_detect(Destino, "ESCRIBANOS")),
         between(Fecha, as.Date(last(Fecha) + duration(month = -6)), last(Fecha))) %>% 
  select(Beneficiario) %>% 
  unique() %>% 
  left_join(ResumenRendSGFCompleto) %>% 
  filter(ImporteNeto != ImporteBruto,
         Origen != "OBRAS")

###Importamos Resumen de Rendiciones EPAM por obra SGF CSV
readResumenRendEPAMSGF <- function(archivoCSV){
  BD <- read_csv(archivoCSV, locale = locale(encoding = 'ISO-8859-1'), 
                 col_names = F, col_types = str_c(rep("c",64), collapse = ""))
  
  BD <- BD %>% 
    select(-one_of(str_c("X", 1:25))) %>% 
    mutate(Obra = ifelse(is.na(X54), NA, X26))

  BD <- BD %>%
    transmute(Origen = "EPAM",
           Obra = zoo::na.locf(Obra, na.rm = F),
           Obra = ifelse(!is.na(Obra), Obra, X39),
           Beneficiario = ifelse(is.na(X54), X26, X37),
           LibramientoSGF = ifelse(is.na(X54), X27, X38),
           Destino = ifelse(is.na(X54), X28, X39),
           Fecha = ifelse(is.na(X54), X29, X40),
           Movimiento = ifelse(is.na(X54), X30, X41),
           ImporteNeto = ifelse(is.na(X54), X31, X42),
           Gcias = ifelse(is.na(X54), X32, X43),
           Sellos = ifelse(is.na(X54), X33, X44),
           TL = ifelse(is.na(X54), X34, X45),
           IIBB = ifelse(is.na(X54), X35, X46),
           SUSS = ifelse(is.na(X54), X36, X47),
           Seguro = ifelse(is.na(X54), X37, X48),
           Salud = ifelse(is.na(X54), X38, X49),
           Mutual = ifelse(is.na(X54), X39, X50),
           ImporteBruto = ifelse(is.na(X54), X40, X51))
    # filter(!is.na(LibramientoSGF))

  BD <- BD %>%
    mutate(Fecha = dmy(Fecha),
           ImporteNeto = parse_number(ImporteNeto),
           Gcias = parse_number(Gcias),
           Sellos = parse_number(Sellos),
           Sellos = ifelse(is.na(Sellos), 0, Sellos),
           TL = parse_number(TL),
           TL = ifelse(is.na(TL), 0, TL),
           IIBB = parse_number(IIBB),
           SUSS = parse_number(SUSS),
           Seguro = parse_number(Seguro),
           Salud = parse_number(Salud),
           Mutual = parse_number(Mutual),
           Retenciones = Gcias + Sellos + TL + IIBB + SUSS + Seguro + Salud + Mutual,
           ImporteBruto = parse_number(ImporteBruto),
           Movimiento = ifelse(Movimiento == "2", "DEBITO", Movimiento))
  
}
ResumenRendEPAMSGF <- dir("Base de Datos/Sistema Gestion Financiera/Resumen de Rendiciones EPAM por OBRA SGF/",
                          full.names = T) %>% map_df(readResumenRendEPAMSGF)

###Importamos Recibos Contratistas SGF (es necesario ABRIR el archivo y GUARDAR COMO)
readRecibosContratistasSGF <- function(archivoExcel){
  BD <- readxl::read_excel(archivoExcel,
                           col_types = "text", skip = 16,
                           col_names = paste("X", 1:16, sep = ""))
  
  BD <- BD %>% 
    head(-4) %>% 
    filter(!is.na(X1)) %>% 
    mutate(Beneficiario = ifelse(is.na(X6), X1, NA))
  
  BD <- BD %>%
    transmute(Origen = "OBRAS",
              Beneficiario = zoo::na.locf(Beneficiario),
              Obra = parse_character(X1, locale = locale(encoding = stringi::stri_enc_get())),
              CodigoObra = str_sub(Obra, 0, 9),
              NroCertificado = X6,
              Destino = ifelse(is.na(X7), X9, X7),
              Rubro = X10,
              MontoCertificado = X11,
              RetencionesSGF = X12,
              ImporteAPagar = X13,
              ImporteNeto = X14,
              Movimiento = X15,
              Fecha = X16) %>% 
    filter(!is.na(Destino))
  
  BD <- BD %>%
    mutate(Fecha =as.Date(parse_integer(Fecha), origin = "1899-12-30"),
           MontoCertificado = parse_number(MontoCertificado),
           RetencionesSGF = parse_number(RetencionesSGF),
           ImporteAPagar = parse_number(ImporteAPagar),
           ImporteNeto = parse_number(ImporteNeto),
           Movimiento = ifelse(Movimiento == "2", "DEBITO", Movimiento))
  
  ImportePagoAcum.vec <- BD %>%
    group_by(Beneficiario, Obra, MontoCertificado) %>%
    group_map(~ cumsum(.x$ImporteNeto)) %>%  simplify()
  
  BD <- BD %>%
    arrange(Beneficiario, Obra, MontoCertificado, Fecha, Movimiento) %>%
    mutate(ImportePagoAcum = ImportePagoAcum.vec,
           Retenciones = ifelse(near(ImporteAPagar, ImportePagoAcum),
                                RetencionesSGF, 0),
           ImporteBruto = ImporteNeto + Retenciones)
  
  
}
RecibosContratistasSGF <- dir("Base de Datos/Sistema Gestion Financiera/Recibos Certificados de Obra SGF/",
                              full.names = T) %>% map_df(readRecibosContratistasSGF)

###Unificamos las tablas Resumen Rend EPAM y Recibos Contratistas
PagosOBRASyEPAMSGF <- ResumenRendEPAMSGF %>%
  filter(Obra != "175-HONORARIOS EPAM") %>% 
  full_join(RecibosContratistasSGF)

###Importamos Informe para Contable SGF
readCertificadosObrasSGF <- function(archivoCSV){
  BD <- read_csv(archivoCSV, col_names = F,
                 col_types = str_c(rep("c",50), collapse = ""),
                 locale = locale(encoding = 'ISO-8859-1'))
  
  BD <- BD %>%
    transmute(Periodo = str_sub(X3[1], -4),
              Beneficiario = ifelse(X38 == "TOTALES" | X49 == "TOTALES", X22, NA),
              Obra = ifelse(X38 == "TOTALES" | X49 == "TOTALES", X23, X22),
              CodigoObra = str_sub(Obra, 0, 9),
              NroCertificado = ifelse(X38 == "TOTALES" | X49 == "TOTALES", X24, X23),
              NoSe = ifelse(X38 == "TOTALES" | X49 == "TOTALES", X25, X24),
              NoSe2 = ifelse(X38 == "TOTALES" | X49 == "TOTALES", X26, X25),
              MontoCertificado = ifelse(X38 == "TOTALES" | X49 == "TOTALES", X27, X26),
              FondoDeReparo = ifelse(X38 == "TOTALES" | X49 == "TOTALES", X28, X27),
              Otros = ifelse(X38 == "TOTALES" | X49 == "TOTALES", X29, X28),
              ImporteBruto = ifelse(X38 == "TOTALES" | X49 == "TOTALES", X30, X29),
              IIBB = ifelse(X38 == "TOTALES" | X49 == "TOTALES", X31, X30),
              LP = ifelse(X38 == "TOTALES" | X49 == "TOTALES", X32, X31),
              SUSS = ifelse(X38 == "TOTALES" | X49 == "TOTALES", X33, X32),
              Gcias = ifelse(X38 == "TOTALES" | X49 == "TOTALES", X34, X33),
              INVICO = ifelse(X38 == "TOTALES" | X49 == "TOTALES", X35, X34),
              Retenciones = ifelse(X38 == "TOTALES" | X49 == "TOTALES", X36, X35),
              ImporteNeto = ifelse(X38 == "TOTALES" | X49 == "TOTALES", X37, X36)) %>%
    select(-NoSe, -NoSe2) %>%
    zoo::na.locf()
  
  BD <- BD %>%
    mutate(MontoCertificado = parse_number(MontoCertificado),
           FondoDeReparo = parse_number(FondoDeReparo),
           Otros = parse_number(Otros),
           ImporteBruto = parse_number(ImporteBruto),
           IIBB = parse_number(IIBB),
           LP = parse_number(LP),
           SUSS = parse_number(SUSS),
           Gcias = parse_number(Gcias),
           INVICO = parse_number(INVICO),
           Retenciones = parse_number(Retenciones),
           ImporteNeto = parse_number(ImporteNeto))
  
}
CertificadosObrasSGF <- dir("Base de Datos/Sistema Gestion Financiera/Informe para Contable SGF/",
                            full.names = T) %>% map_df(readCertificadosObrasSGF)

###Fondo de Reparo Retenidos
FondoReparoRetenidoSGF <- CertificadosObrasSGF %>% 
  filter(!near(FondoDeReparo, 0)) %>% 
  inner_join(select(RecibosContratistasSGF, CodigoObra, Destino)) %>% 
  unique()

##SISTEMA GESTIÓN DE OBRAS

###Importamos Informe Completo Gestión Obras
readObrasGestionObras <- function(archivoExcel){
  BD <- readxl::read_excel(archivoExcel,
                           col_types = "text", skip = 4,
                           col_names = paste("X", 1:51, sep = ""))

  BD <- BD %>%
    transmute(CodigoObra = X1,
              BasicoObra = X2,
              CodigoContrato = X3,
              Descripcion = X4,
              BasicoContrato = X5,
              TipoObra = X6,
              Localidad = X7,
              Contratista = X8,
              Activa = X9,
              Monto = X10,
              MontoTotal = X11,
              RepresentanteTecnico = X12,
              Operatoria = X13,
              CantidadRubros = X14,
              Inspector = X15,
              Iniciador = X16,
              Estado = X17,
              FechaInicio = X18,
              FechaContrato = X19,
              FechaTerminacionReal = X21,
              PlazoOriginalDias = X22,
              PlazoOriginalFin = X23,
              PlazoConAmpliacionesDias = X24,
              PlazoConAmpliacionesFin = X25,
              AvanceFisicoReal = X26,
              AvanceFinancieroReal = X27,
              AvanceFisicoCronograma = X28,
              AvanceFinancieroCronograma = X29,
              MontoTotalCertificado = X30,
              MontoTotalCertificadoObra = X31,
              MontoPagado = X32,
              UltimoCertificadoNumero = X34,
              UltimoCertificadoTipoBC = X35,
              UltimoCertificadoMes = X36,
              UltimoCertificadoAno = X37,
              UltimoCertificadoFecha = X38,
              AnticipoAcumulado = X39,
              CantidadAnticipos = X40,
              PorcentajeAnticipo = X41,
              CantidadCertificadosAnticipo = X42,
              AcumuladoFondoReparo = X43,
              AcumuladoDescuentoFondoReparo = X44,
              MontoRedeterminado = X45,
              UltimaRedeterminacionNumero = X46,
              UltimoBasicoMes = X47,
              UltimoBasicoAno = X48,
              UltimaMedicionNumero = X49,
              UltimaMedicionMes = X50,
              UltimaMedicionAno = X51) 

  BD <- BD %>%
    mutate(FechaInicio =as.Date(parse_integer(FechaInicio), origin = "1899-12-30"),
           FechaContrato =as.Date(parse_integer(FechaContrato), origin = "1899-12-30"),
           PlazoOriginalFin =as.Date(parse_integer(PlazoOriginalFin), origin = "1899-12-30"),
           PlazoConAmpliacionesFin =as.Date(parse_integer(PlazoConAmpliacionesFin), origin = "1899-12-30"),
           UltimoCertificadoFecha =as.Date(parse_integer(UltimoCertificadoFecha), origin = "1899-12-30"),
           FechaTerminacionReal =as.Date(parse_integer(FechaTerminacionReal), origin = "1899-12-30"),
           Monto = round(parse_double(Monto), 2),
           MontoTotal = round(parse_double(MontoTotal), 2),
           MontoTotalCertificado = round(parse_double(MontoTotalCertificado), 2),
           MontoTotalCertificadoObra = round(parse_double(MontoTotalCertificadoObra), 2),
           MontoPagado = round(parse_double(MontoPagado), 2),
           AnticipoAcumulado = round(parse_double(AnticipoAcumulado), 2),
           AcumuladoFondoReparo = round(parse_double(AcumuladoFondoReparo), 2),
           AcumuladoDescuentoFondoReparo = round(parse_double(AcumuladoDescuentoFondoReparo), 2),
           MontoRedeterminado = round(parse_double(MontoRedeterminado), 2),
           AvanceFisicoReal = round(parse_double(AvanceFisicoReal), 4),
           AvanceFinancieroReal = round(parse_double(AvanceFinancieroReal), 4),
           AvanceFisicoCronograma = round(parse_double(AvanceFisicoCronograma), 4),
           AvanceFinancieroCronograma = round(parse_double(AvanceFinancieroCronograma), 4),
           PorcentajeAnticipo = round(parse_double(PorcentajeAnticipo), 4))
  #          MontoCertificado = parse_number(MontoCertificado),
  #          RetencionesSGF = parse_number(RetencionesSGF),
  #          ImporteAPagar = parse_number(ImporteAPagar),
  #          ImporteNeto = parse_number(ImporteNeto),
  #          Movimiento = ifelse(Movimiento == "2", "DEBITO", Movimiento))
  
}
ObrasGestionObras <- readObrasGestionObras("Base de Datos/Gestión Obras/ObrasCompleto.xls")

##Exportamos
###Exportamos SQLite
AgregarRegistrosBD("SSCC", "BancoINVICO", 
                   Data = MovSSCC, overwrite = TRUE)
AgregarRegistrosBD("SSCC", "ImputacionesBancoINVICO", 
                   Data = ImputacionesSSCC, overwrite = TRUE)

AgregarRegistrosBD("SGF", "ResumenRendSGF", 
                   Data = ResumenRendSGF, overwrite = TRUE)
x <- CertificadosObrasSGF %>% 
  select(-CodigoObra)
AgregarRegistrosBD("SGF", "CertificadosObrasSGF", 
                   Data = x, overwrite = TRUE)
AgregarRegistrosBD("SGF", "ResumenRendEPAMPorObraSGF", 
                   Data = ResumenRendEPAMSGF, overwrite = TRUE)

AgregarRegistrosBD("SGO", "ObrasSGO", 
                   Data = ObrasGestionObras, overwrite = TRUE)


###Exportamos CSV
writeCSV(MovSSCCconImputaciones, "Movimientos SSCC.csv")

writeCSV(ResumenRendSGFCompleto, "Resumen Rendiciones SGF.csv")

writeCSV(CertificadosObrasSGF, "Certificados de Obras SGF.csv")

writeCSV(FondoReparoRetenidoSGF, "Fondo Reparo Retenido SGF.csv")

writeCSV(PagoACuentaSGF, "Pago a Cuenta SGF.csv")

writeCSV(PagosOBRASyEPAMSGF, "Pagos Obras y EPAM SGF.csv")

writeCSV(HonorariosFacturerosSGF, "Honorarios Factureros.csv")

writeCSV(ObrasGestionObras, "Obras Gestion Obras.csv")


#SISTEMAS GV----

##Importamos
###Importamos Resumen Recaudados Recuperos por Año
readRecaudadoRecuperosGV <- function(archivoXLSX){
  BD <- readxl::read_xlsx(archivoXLSX,
                          col_types = "text",
                          col_names = paste("X", 1:14, sep = ""))

  BD <- BD %>%
    mutate(Ejercicio = str_sub(X5[1], 42, 45)) %>% 
    head(-1) %>% 
    tail(-5)

  BD <- BD %>%
    transmute(Ejercicio = Ejercicio,
              Mes = X1,
              MesEjercicio = str_c(str_pad(Mes, 2, pad = "0"),
                                   Ejercicio, sep = "/"),
              CuotaAmort = X2,
              IntFinanc = X3,
              IntMora = X4,
              GtosAdm = X6,
              SegIncencio = X7,
              SegVida = X8,
              Subsidio = X9,
              PagoAmigable = X10,
              EscrituraRes100 = X12,
              PendienteAcreditacion = X13,
              RecaudadoTotal = X14)

  BD <- BD %>%
    mutate(CuotaAmort = parse_double(CuotaAmort),
           IntFinanc = parse_double(IntFinanc),
           IntMora = parse_double(IntMora),
           GtosAdm = parse_double(GtosAdm),
           SegIncencio = parse_double(SegIncencio),
           SegVida = parse_double(SegVida),
           Subsidio = parse_double(Subsidio),
           PagoAmigable = parse_double(PagoAmigable),
           EscrituraRes100 = parse_double(EscrituraRes100),
           PendienteAcreditacion = parse_double(PendienteAcreditacion),
           RecaudadoTotal = parse_double(RecaudadoTotal))

}
RecaudadoRecuperosGV <- dir("Base de Datos/Gestión Vivienda GV/Sistema Recuperos GV/Resumen Recaudado/",
                      full.names = T) %>% map_df(readRecaudadoRecuperosGV)


###Importamos Resumen Facturado por Recuperos Año
readFacturadoRecuperosGV <- function(archivoXLSX){
  BD <- readxl::read_xlsx(archivoXLSX,
                          col_types = "text",
                          col_names = paste("X", 1:13, sep = ""))

  BD <- BD %>%
    mutate(Ejercicio = str_sub(X6[1], 42, 45)) %>%
    head(-1) %>%
    tail(-5)

  BD <- BD %>%
    transmute(Ejercicio = Ejercicio,
              Mes = X1,
              MesEjercicio = str_c(str_pad(Mes, 2, pad = "0"),
                                   Ejercicio, sep = "/"),
              CuotaAmort = X2,
              IntFinanc = X3,
              IntMora = X4,
              GtosAdm = X5,
              SegIncencio = X7,
              SegVida = X8,
              Subsidio = X9,
              PagoAmigable = X10,
              EscrituraRes100 = X12,
              FacturadoTotal = X13)

  BD <- BD %>%
    mutate(CuotaAmort = parse_double(CuotaAmort),
           IntFinanc = parse_double(IntFinanc),
           IntMora = parse_double(IntMora),
           GtosAdm = parse_double(GtosAdm),
           SegIncencio = parse_double(SegIncencio),
           SegVida = parse_double(SegVida),
           Subsidio = parse_double(Subsidio),
           PagoAmigable = parse_double(PagoAmigable),
           EscrituraRes100 = parse_double(EscrituraRes100),
           FacturadoTotal = parse_double(FacturadoTotal))
  
}
FacturadoRecuperosGV <- dir("Base de Datos/Gestión Vivienda GV/Sistema Recuperos GV/Resumen Facturado/",
                            full.names = T) %>% map_df(readFacturadoRecuperosGV)



###Importamos Resumen Facturado por Recuperos Año
readFacturadoRecuperosGV <- function(archivoXLSX){
  BD <- readxl::read_xlsx(archivoXLSX,
                          col_types = "text",
                          col_names = paste("X", 1:13, sep = ""))
  
  BD <- BD %>%
    mutate(Ejercicio = str_sub(X6[1], 42, 45)) %>%
    head(-1) %>%
    tail(-5)
  
  BD <- BD %>%
    transmute(Ejercicio = Ejercicio,
              Mes = X1,
              MesEjercicio = str_c(str_pad(Mes, 2, pad = "0"),
                                   Ejercicio, sep = "/"),
              CuotaAmort = X2,
              IntFinanc = X3,
              IntMora = X4,
              GtosAdm = X5,
              SegIncencio = X7,
              SegVida = X8,
              Subsidio = X9,
              PagoAmigable = X10,
              EscrituraRes100 = X12,
              FacturadoTotal = X13)
  
  BD <- BD %>%
    mutate(CuotaAmort = parse_double(CuotaAmort),
           IntFinanc = parse_double(IntFinanc),
           IntMora = parse_double(IntMora),
           GtosAdm = parse_double(GtosAdm),
           SegIncencio = parse_double(SegIncencio),
           SegVida = parse_double(SegVida),
           Subsidio = parse_double(Subsidio),
           PagoAmigable = parse_double(PagoAmigable),
           EscrituraRes100 = parse_double(EscrituraRes100),
           FacturadoTotal = parse_double(FacturadoTotal))
  
}
FacturadoRecuperosGV <- dir("Base de Datos/Gestión Vivienda GV/Sistema Recuperos GV/Resumen Facturado/",
                            full.names = T) %>% map_df(readFacturadoRecuperosGV)


##Exportamos
###Exportamos SQLite
AgregarRegistrosBD("SGV", "RecaudadoRecuperosSGV", 
                   Data = RecaudadoRecuperosGV, overwrite = TRUE)
AgregarRegistrosBD("SGV", "FacturadoRecuperosSGV", 
                   Data = FacturadoRecuperosGV, overwrite = TRUE)

###Exportamos CSV
writeCSV(RecaudadoRecuperosGV, "Recaudado Recuperos GV.csv")

writeCSV(FacturadoRecuperosGV, "Facturado Recuperos GV.csv")


#SIIF GASTOS---------------------------------------

##SIIF
###Importamos Ejecución Presupuestaria con Fuente SIIF (rf602)
readEjecPresFteSIIF <- function(archivoExcel){
  BD <- readxl::read_excel(archivoExcel,
                           col_types = "text",
                           col_names = paste("X", 1:23, sep = ""))
  
  BD <- BD %>%
    transmute(Periodo = str_sub(X1[4], -4), Programa = str_pad(X1, 2, pad = "0"), Subprograma = str_pad(X2, 2, pad = "0"),
              Proyecto = str_pad(X5, 2, pad = "0"), Actividad = str_pad(X6, 2, pad = "0"),
              Partida = X7, Grupo = str_c(str_sub(X7, 1,1), "00", ""), Fuente = X8, Org = X9, CreditoOriginal = X12,
              CreditoVigente = X13, Comprometido = X14, Ordenado = X15, Saldo = X17, Pendiente = X19) %>%
    tail(-13) %>%
    filter(Programa != is.na(Programa)) %>% 
    mutate(CreditoOriginal = parse_number(CreditoOriginal, locale = locale(decimal_mark = ".")),
           CreditoVigente = parse_number(CreditoVigente, locale = locale(decimal_mark = ".")),
           Comprometido = parse_number(Comprometido, locale = locale(decimal_mark = ".")),
           Ordenado = parse_number(Ordenado, locale = locale(decimal_mark = ".")),
           Saldo = parse_number(Saldo, locale = locale(decimal_mark = ".")),
           Pendiente = parse_number(Pendiente, locale = locale(decimal_mark = ".")))
  
}
EjecPresFteSIIF <- dir("Base de Datos/Reportes SIIF/Ejecucion Presupuestaria con Fuente (rf602)/",
                       full.names = T) %>% map_df(readEjecPresFteSIIF)

###Importamos Ejecución Presupuestaria con Descripcion SIIF (rf610)
readEjecPresDescSIIF <- function(archivoExcel){
  BD <- readxl::read_excel(archivoExcel,
                           col_types = "text",
                           col_names = paste("X", 1:65, sep = ""))
  
  BD <- BD %>%
    transmute(Periodo = str_sub(X33[8], -4), Programa = X5, Subprograma = X9, Proyecto = X14, Actividad = X17,
              Grupo = X20, Partida = X21, DescPartida = X24, CreditoOriginal = X38,
              CreditoVigente = X44, Comprometido = X49, Ordenado = X55, Saldo = X60) %>%
    tail(-28) %>% 
    mutate(Programa = zoo::na.locf(Programa),
           Subprograma = zoo::na.locf(Subprograma, F),
           Proyecto = zoo::na.locf(Proyecto, F),
           Actividad = zoo::na.locf(Actividad, F),
           Grupo = zoo::na.locf(Grupo, F),
           Partida = zoo::na.locf(Partida, F),
           DescPartida = zoo::na.locf(DescPartida, F)) %>% 
    filter(CreditoOriginal != is.na(CreditoOriginal))
  
  BD <- BD %>%
    mutate(CreditoOriginal = parse_number(CreditoOriginal, locale = locale(decimal_mark = ".")),
           CreditoVigente = parse_number(CreditoVigente, locale = locale(decimal_mark = ".")),
           Comprometido = parse_number(Comprometido, locale = locale(decimal_mark = ".")),
           Ordenado = parse_number(Ordenado, locale = locale(decimal_mark = ".")),
           Saldo = parse_number(Saldo, locale = locale(decimal_mark = "."))) %>% 
    separate(Programa, c("Programa", "DescProg"), remove = T, extra = "merge") %>% 
    separate(Subprograma, c("Subprograma", "DescSubprog"), remove = T, extra = "merge") %>% 
    separate(Proyecto, c("Proyecto", "DescProy"), remove = T, extra = "merge") %>% 
    separate(Actividad, c("Actividad", "DescAct"), remove = T, extra = "merge") %>% 
    separate(Grupo, c("Grupo", "DescGpo"), remove = T, extra = "merge") %>% 
    mutate(Programa = str_pad(Programa, 2, pad = "0"),
           Subprograma = str_pad(Subprograma, 2, pad = "0"),
           Proyecto = str_pad(Proyecto, 2, pad = "0"),
           Actividad = str_pad(Actividad, 2, pad = "0"))
  
}
EjecPresDescSIIF <- dir("Base de Datos/Reportes SIIF/Ejecucion Presupuestaria con Descripcion (rf610)/",
                        full.names = T) %>% map_df(readEjecPresDescSIIF)

###Combinamos tablas de ejecución presupuestaria
EjecPresSIIF <- EjecPresDescSIIF %>% 
  select(-CreditoOriginal, -CreditoVigente,
         -Comprometido, -Ordenado, -Saldo)
EjecPresSIIF <- EjecPresFteSIIF %>% 
  left_join(EjecPresSIIF) %>% 
  select(Periodo, Programa, DescProg,
         Subprograma, DescSubprog,
         Proyecto, DescProy,
         Actividad, DescAct,
         Grupo, DescGpo,
         Partida, DescPartida, everything())

###Importamos Comprobantes Gastos Ingresados (rcg01_uejp)
readComprobantesGtoSIIF <- function(archivoExcel){
  BD <- readxl::read_excel(archivoExcel,
                           col_types = "text",
                           col_names = paste("X", 1:19, sep = ""))
  
  BD <- BD %>%
    mutate(Periodo = str_sub(X1[2], -4)) %>% 
    select(-X18, -X19)
  
  names(BD) <- c("NroEntrada", "NroOrigen", "Fuente", "ClaseReg",
                 "ClaseMod", "ClaseGto", "Fecha", "Monto", 
                 "CUIT", "Beneficiario", "NroExpediente","Cuenta", 
                 "Comprometido", "Verificado", "Aprobado", "Pagado",
                 "NroFondo", "Periodo")
  
  BD <- tail(BD, -15) %>%
    filter(CUIT != is.na(CUIT)) %>%
    filter(NroEntrada != is.na(NroEntrada))
  
}
ComprobantesGtoSIIF <- dir("Base de Datos/Reportes SIIF/Comprobantes de Gastos (rcg01_uejp)/",
                              full.names = T) %>% map_df(readComprobantesGtoSIIF)
ComprobantesGtoSIIF <- ComprobantesGtoSIIF %>% 
  mutate(Fecha = as.Date(parse_integer(Fecha), origin = "1899-12-30"),
         NroEntrada = parse_integer(NroEntrada),
         NroOrigen = parse_integer(NroOrigen),
         Monto = parse_number(Monto, locale = locale(decimal_mark = ".")),
         Comprometido = ifelse(Comprometido == "S", T, F),
         Verificado = ifelse(Verificado == "S", T, F),
         Aprobado = ifelse(Aprobado == "S", T, F),
         Pagado = ifelse(Pagado == "S", T, F))

###Depuramos los MAP
ComprobantesGtoSIIF <- ComprobantesGtoSIIF %>% 
  filter(ClaseMod == "MAP", Aprobado == TRUE) %>% 
  select(NroOrigen, MontoAjustado = Monto, Periodo) %>% 
  right_join(ComprobantesGtoSIIF) %>% 
  mutate(MontoAjustado = ifelse(is.na(MontoAjustado),
                                Monto, ifelse(ClaseMod == "MAP",
                                              0, (Monto + MontoAjustado))))
         
         
###Importamos Comprobantes Gastos Ingresados con Partida sin REM (rcg01_par) - SOLO CYO PAGADOS? WTF!!
readComprobantesGtoPartidaSIIF <- function(archivoExcel){
  BD <- readxl::read_excel(archivoExcel,
                           col_types = "text",
                           col_names = paste("X", 1:19, sep = ""))
  
  BD <- BD %>%
    mutate(Periodo = str_sub(X1[2], -4)) %>% 
    select(-X2, -X4, -X9)
  
  BD <- tail(BD, -14) %>%
    filter(X1 != is.na(X1)) %>% 
    transmute(Periodo = Periodo,
           NroEntrada =  parse_integer(X1),
           NroOrigen =  parse_integer(X3),
           Fuente =  X5,
           ClaseReg =  X6,
           ClaseGto =  X7,
           Fecha =  as.Date(parse_integer(X8), origin = "1899-12-30"),
           Partida =  X10,
           Grupo = str_c(str_sub(Partida, 1,1), "00", ""),
           Monto =  parse_number(X11, locale = locale(decimal_mark = ".")),
           CUIT =  X12,
           Beneficiario =  X13,
           NroExpediente = X14,
           Cuenta =  X15,
           Comprometido =  ifelse(X16 == "S", T, F),
           Verificado =  ifelse(X17 == "S", T, F),
           Aprobado =  ifelse(X18 == "S", T, F),
           Pagado = ifelse(X19 == "S", T, F))

}
ComprobantesGtoPartidaSIIF <- dir("Base de Datos/Reportes SIIF/Comprobantes de Gastos con Partida Pagados sin REM (rcg01_par)/",
                              full.names = T) %>% map_df(readComprobantesGtoPartidaSIIF)


###Combinamos BD Comprobantes Gastos Ingresados (rcg01_par + REM rcg01_uejp)
ComprobantesGtoPartidaCompletoSIIF <- ComprobantesGtoSIIF %>% 
  filter(ClaseGto == "REM", MontoAjustado > 0) %>% 
  mutate(Partida = "100",
         Grupo = "100") %>% 
  select(-NroFondo, -ClaseMod, -Monto, Monto = MontoAjustado) %>% 
  full_join(ComprobantesGtoPartidaSIIF)


###Importamos Comprobantes Gastos Ingresados por Grupo Partida (gto_rpa03g)
readComprobantesGtoGpoPartidaSIIF <- function(archivoExcel){
  BD <- readxl::read_excel(archivoExcel,
                           col_types = "text",
                           col_names = paste("X", 1:30, sep = ""))

  BD <- BD %>%
    mutate(Periodo = str_sub(X18[2], -4)) %>% 
    select(Periodo, X1, X5, X8, X11, 
           X14, X17, X19, X21, X23)

  BD <- tail(BD, -20) %>% 
    filter(X1 != is.na(X1)) %>% 
    transmute(Periodo = Periodo,
              NroEntrada =  parse_integer(X1),
              NroOrigen =  parse_integer(X5),
              Monto =  parse_number(X8, locale = locale(decimal_mark = ".")),
              Mes =  parse_integer(X11),
              Fecha =  as.Date(parse_integer(X14), origin = "1899-12-30"),
              Partida =  X17,
              Grupo = str_c(str_sub(Partida, 1,1), "00", ""),
              NroExpediente = X19,
              Glosa =  X21,
              Beneficiario =  X23)
  
}
ComprobantesGtoGpoPartidaSIIF <- dir("Base de Datos/Reportes SIIF/Comprobantes de Gastos por Grupo Partida (gto_rpa03g)/",
                                  full.names = T) %>% map_df(readComprobantesGtoGpoPartidaSIIF)


###Combinamos BD Comprobantes Gastos Ingresados (gto_rpa03g + rcg01_uejp)
ComprobantesGtoGpoPartidaCompletoSIIF <- ComprobantesGtoSIIF %>% 
  select(-Fecha, -NroOrigen, -Monto, -MontoAjustado, -Beneficiario, -NroExpediente) %>% 
  right_join(ComprobantesGtoGpoPartidaSIIF, by = c("Periodo", "NroEntrada"))


###Importamos Listado Analitico Retenciones SIIF (rao01)
readListadoRentecionesSIIF <- function(archivoExcel){
  BD <- readxl::read_excel(archivoExcel,
                           col_types = "text",
                           col_names = paste("X", 1:20, sep = ""))
  

  BD <- tail(BD, -16) %>% 
    filter(X1 != is.na(X1)) %>%
    transmute(Fecha = as.Date(parse_integer(X12), origin = "1899-12-30"),
              Periodo = as.character(year(Fecha)),
              NroEntrada = parse_integer(X1),
              CodRetencion = X4,
              Descripcion =  X7,
              Monto =  parse_number(X11, locale = locale(decimal_mark = ".")),
              Cuenta =  X14)
  
}
ListadoRetencionesSIIF <- dir("Base de Datos/Reportes SIIF/Listado Retenciones Practicadas por Codigo (rao01)/",
                        full.names = T) %>% map_df(readListadoRentecionesSIIF)

###Combinamos Listado de Retenciones con Comprobantes de Gastos
ListadoRetencionesSIIF <- ComprobantesGtoSIIF %>% 
  select(Periodo, NroEntrada, Fuente) %>% 
  right_join(ListadoRetencionesSIIF)

###Importamos Resumen de Fondo SIIF (rfondo07tp)
readResumenFondoSIIF <- function(archivoExcel){
  BD <- readxl::read_excel(archivoExcel,
                           col_types = "text",
                           col_names = paste("X", 1:20, sep = ""))

  BD <- BD %>%
    mutate(Periodo = str_sub(X1[3], -4),
           TipoComprobante = str_sub(X2[10], - (length(X2[10]) - 72)))

  BD <- tail(BD, -14) %>%
    filter(X10 != is.na(X10)) %>%
    transmute(TipoComprobante = TipoComprobante,
              Periodo = Periodo,
              Fecha = as.Date(parse_integer(X10), origin = "1899-12-30"),
              NroFondo =  parse_integer(X3),
              Descripcion =  X6,
              Ingresos =  parse_number(X12, locale = locale(decimal_mark = ".")),
              Egresos =  parse_number(X15, locale = locale(decimal_mark = ".")),
              Saldo =  parse_number(X18, locale = locale(decimal_mark = ".")))
  
}
ResumenFondoSIIF <- dir("Base de Datos/Reportes SIIF/Comprobantes de Fondos Regularizados por Tipo (rfondo07tp)/",
                                  full.names = T) %>% map_df(readResumenFondoSIIF)

###Importamos Deuda Flotante SIIF (rdeu012)
readDeudaFlotanteSIIF <- function(archivoExcel){
  BD <- readxl::read_excel(archivoExcel,
                           col_types = "text",
                           col_names = paste("X", 1:23, sep = ""))
  
  #No sé cómo obtener el Código Recurso
  
  BD <- BD %>%
    mutate(Fuente = ifelse(X5 == "27", NA, as.numeric(X5)),
           FechaDesde = str_sub(X1[14], 7 ,17),
           FechaHasta = str_sub(X1[14], -10)) %>% 
    tail(-11) %>% 
    transmute(Fuente = zoo::na.locf(Fuente),
              FechaDesde = dmy(FechaDesde),
              FechaHasta = dmy(FechaHasta),
              MesHasta = str_c(str_pad(month(FechaHasta), 2, pad = "0"),
                               year(FechaHasta), sep = "/"),
              NroEntrada = X1,
              NroOrigen = X3,
              FechaAprobado = X6,
              OrgFin = X8,
              Monto = X9,
              Saldo = X12,
              NroExpediente = X13,
              Cuenta = X14,
              Referencia = X16,
              CUIT = X17,
              Beneficiario = X18) %>% 
    filter(!is.na(CUIT),
           !is.na(NroEntrada)) %>% 
    mutate(FechaAprobado = as.Date(parse_integer(FechaAprobado), origin = "1899-12-30"),
           NroEntrada = parse_integer(NroEntrada),
           NroOrigen = parse_integer(NroOrigen),
           Monto = round(parse_double(Monto), 2),
           Saldo = round(parse_double(Saldo), 2))
  
}
DeudaFlotanteSIIF <- dir("Base de Datos/Reportes SIIF/Deuda Flotante (rdeu)/",
                         full.names = T) %>% map_df(readDeudaFlotanteSIIF)

###Importamos Deuda Flotante SIIF TG (rdeu012b2_C)
readDeudaFlotanteSIIFTG <- function(archivoCSV){
  # BD <- readxl::read_excel(archivoExcel,
  #                          col_types = "text",
  #                          col_names = paste("X", 1:12, sep = ""))
  
  BD <- read_csv(archivoCSV, col_names = F,
                 col_types = str_c(rep("c",12), collapse = ""),
                 locale = locale(encoding = stringi::stri_enc_get()))

  BD <- BD %>%
    mutate(FechaDesde = str_sub(X1[7], 7 ,17),
           FechaHasta = str_sub(X1[7], -10)) %>%
    filter(!is.na(X6)) %>% 
    head(-2) %>% 
    mutate(PeriodoDeuda = ifelse(is.na(X1), str_sub(X2[], -4), NA)) %>% 
    transmute(PeriodoDeuda = zoo::na.locf(PeriodoDeuda, fromLast = TRUE),
              Fuente = X3,
              FechaDesde = dmy(FechaDesde),
              FechaHasta = dmy(FechaHasta),
              MesHasta = str_c(str_pad(month(FechaHasta), 2, pad = "0"),
                               year(FechaHasta), sep = "/"),
              NroEntrada = X1,
              NroOrigen = X2,
              CC = str_c(NroEntrada, 
                         str_sub(PeriodoDeuda, -2), sep = "/"),
              OrgFin = X4,
              Monto = X5,
              Saldo = X6,
              NroExpediente = X7,
              Cuenta = X8,
              Descripcion = X9) %>% 
    filter(!is.na(Fuente),
           Fuente != "Fte") %>% 
    mutate(NroEntrada = parse_integer(NroEntrada),
           NroOrigen = parse_integer(NroOrigen),
           Monto = round(parse_number(Monto, locale = locale(decimal_mark = ",")), 2),
           Saldo = round(parse_number(Saldo, locale = locale(decimal_mark = ",")), 2))
  
}
DeudaFlotanteSIIFTG <- dir("Base de Datos/Reportes SIIF/Deuda Flotante TG (rdeu012b2_C)/",
                         full.names = T) %>% map_df(readDeudaFlotanteSIIFTG)

###Importamos Listado de Pagos Tesorería SIIF (rtr03)
readPagosSIIF <- function(archivoExcel){
  BD <- readxl::read_excel(archivoExcel,
                           col_types = "text",
                           col_names = paste("X", 1:42, sep = ""))

  BD <- BD %>%
    tail(-18) %>%
    mutate_all(., str_replace_all, pattern = "[\r\n]", replacement = "") %>% 
    transmute(Ejercicio = X9,
              Entidad = X6,
              NroEntrada = X8,
              EjercicioOrigen = X1,
              NroCAP = X10,
              Fuente = X12,
              FechaPago = X13,
              CuentaPago = X16,
              NroInterno = X18,
              ChequeBanco = X19,
              Tipo = X21,
              CUITPago = X23,
              Beneficiario = X25,
              Glosa = X27,
              Monto = X29,
              Ingresos = X38,
              Uej = X42) %>%
    filter(!is.na(EjercicioOrigen)) %>%
    mutate(FechaPago = as.Date(parse_integer(FechaPago), origin = "1899-12-30"),
           Monto = round(parse_double(Monto), 2),
           Ingresos = round(parse_double(Ingresos), 2))
  
  #Elimino algunos columnas sin sentido
  BD <- BD %>% 
    select(-Ingresos, -Uej, -ChequeBanco, 
           -NroInterno, -EjercicioOrigen, -Entidad)
  
  #ERROR con los ANP (el reporte solo trae un CAP por lo que el mov. queda anulado)
  BD <- BD %>%
    filter(Tipo != "ANP")
  
  # #Transformamos los ANP en CAP
  # BD <- BD %>% 
  #   mutate(Tipo = ifelse(Tipo == "ANP", "CAP", Tipo))
  
  #Generamos un proxy del Cta Cte Gasto
  CargaGasto <- BD %>%
    filter(!CUITPago %in% c(30709110078, 33693450239)) %>%
    group_by(NroEntrada, Tipo) %>%
    filter(Monto == max(Monto)) %>%
    select(NroEntrada, Tipo, Cuenta = CuentaPago, CUIT = CUITPago) %>%
    unique()

  BD <- BD %>%
    left_join(CargaGasto) %>% 
    mutate(Cuenta = if_else(is.na(Cuenta), CuentaPago, Cuenta),
           CUIT = if_else(is.na(CUIT), CUITPago, CUIT))
  
  # #Volvemos a crear el Tipo ANP
  # BD <- BD %>%
  #   mutate(Tipo = ifelse(Monto < 0, "ANP", Tipo))
  
  BD <- BD %>% 
    select(Ejercicio, NroEntrada, Tipo, Fuente, FechaPago, 
           Cuenta, CUIT, CuentaPago, CUITPago, Beneficiario,
           Monto, everything())
  
}
PagosSIIF <- dir("Base de Datos/Reportes SIIF/Listado Pagos Tesoreria (rtr03)/",
                             full.names = T) %>% map_df(readPagosSIIF)

###Incorporamos los MAPs al rtr03 hasta que se solucione el error ANP
PagosSIIF <- ComprobantesGtoSIIF %>% 
  filter(ClaseMod == "MAP" & Aprobado == TRUE) %>% 
  transmute(Ejercicio = Periodo,
            NroEntrada = as.character(NroOrigen),
            Tipo = "MAP",
            Fuente = Fuente,
            FechaPago = Fecha,
            Cuenta = Cuenta,
            CUIT = CUIT,
            CuentaPago = Cuenta,
            CUITPago = CUIT,
            Beneficiario = Beneficiario, 
            Monto = Monto, 
            NroCAP = as.character(NroEntrada),
            Glosa = NroExpediente) %>% 
  bind_rows(PagosSIIF, .)

##Exportamos
###SQLite Files
x <- EjecPresFteSIIF %>% 
  rename(Ejercicio = Periodo)
AgregarRegistrosBD("ICARO", "EjecPresPorFteSIIF", 
                   Data = x, overwrite = TRUE)
AgregarRegistrosBD("SIIF", "EjecPresPorFteSIIF", 
                   Data = x, overwrite = TRUE)

x <- EjecPresDescSIIF %>% 
  rename(Ejercicio = Periodo)
AgregarRegistrosBD("SIIF", "EjecPresConDescSIIF", 
                   Data = x, overwrite = TRUE)

x <- ComprobantesGtoPartidaSIIF %>% 
  rename(Ejercicio = Periodo)
AgregarRegistrosBD("ICARO", "ComprobantesGtosPorPartidaSIIF", 
                   Data = x, overwrite = TRUE)
AgregarRegistrosBD("SIIF", "ComprobantesGtosPorPartidaSIIF", 
                   Data = x, overwrite = TRUE)

x <- ComprobantesGtoSIIF %>% 
  rename(Ejercicio = Periodo)
AgregarRegistrosBD("SIIF", "ComprobantesGtosSIIF", 
                   Data = x, overwrite = TRUE)

x <- ComprobantesGtoGpoPartidaSIIF %>% 
  rename(Ejercicio = Periodo)
AgregarRegistrosBD("SIIF", "ComprobantesGtoGpoPartidaSIIF", 
                   Data = x, overwrite = TRUE)

AgregarRegistrosBD("SIIF", "DeudaFlotanteSIIF", 
                   Data = DeudaFlotanteSIIF, overwrite = TRUE)

x <- ListadoRetencionesSIIF %>% 
  rename(Ejercicio = Periodo)
AgregarRegistrosBD("SIIF", "RetencionesPracticadasSIIF", 
                   Data = x, overwrite = TRUE)

AgregarRegistrosBD("SIIF", "PagosSIIF", 
                   Data = PagosSIIF, overwrite = TRUE)

x <- ResumenFondoSIIF %>% 
  rename(Ejercicio = Periodo)
AgregarRegistrosBD("SIIF", "ComprobantesFondosPorTipoSIIF", 
                   Data = x, overwrite = TRUE)

###CSV Files
writeCSV(EjecPresDescSIIF, "Ejecucion Presupuesto con Descripcion SIIF.csv")

writeCSV(EjecPresFteSIIF, "Ejecucion Presupuesto por Fuente SIIF.csv")

writeCSV(EjecPresSIIF, "Ejecucion Presupuesto Completo SIIF.csv")

ComprobantesGtoSIIF <- ComprobantesGtoSIIF %>% 
  select(Periodo, Fecha, NroEntrada, NroOrigen, Fuente, ClaseReg,
         ClaseMod, ClaseGto, Monto, MontoAjustado, everything())
writeCSV(ComprobantesGtoSIIF, "Comprobantes Gastos Ingresados SIIF.csv")

ComprobantesGtoPartidaSIIF <- ComprobantesGtoPartidaSIIF %>% 
  select(Periodo, Fecha, NroEntrada, NroOrigen, Fuente, ClaseReg,
         ClaseGto, Monto, Grupo, Partida, everything())
writeCSV(ComprobantesGtoPartidaSIIF, "Comprobantes Gastos Ingresados (sin REM) con Partida SIIF.csv")

ComprobantesGtoPartidaCompletoSIIF <- ComprobantesGtoPartidaCompletoSIIF %>% 
  select(Periodo, Fecha, NroEntrada, NroOrigen, Fuente, ClaseReg,
         ClaseGto, Monto, Grupo, Partida, everything())
writeCSV(ComprobantesGtoPartidaCompletoSIIF, "Comprobantes Gastos Ingresados Completo SIIF.csv")

ComprobantesGtoGpoPartidaCompletoSIIF <- ComprobantesGtoGpoPartidaCompletoSIIF %>% 
  select(Periodo, Fecha, NroEntrada, NroOrigen, Fuente, ClaseReg,
         ClaseMod, ClaseGto, Monto, Grupo, Partida, CUIT, 
         Beneficiario, NroExpediente, Cuenta, everything())
writeCSV(ComprobantesGtoGpoPartidaCompletoSIIF, "Comprobantes Gastos Ingresados Completo SIIF.csv")

writeCSV(ListadoRetencionesSIIF, "Listado Retenciones SIIF.csv")

writeCSV(DeudaFlotanteSIIF, "Deuda Flotante SIIF.csv")

writeCSV(DeudaFlotanteSIIFTG, "Deuda Flotante SIIF TG.csv")

writeCSV(ResumenFondoSIIF, "Resumen Fondos SIIF.csv")

writeCSV(PagosSIIF, "Pagos SIIF.csv")

#SIIF RECURSOS---------------------------------------

##SIIF
###Importamos Recursos SIIF (rci02)
readRecursosSIIF <- function(archivoExcel){
  BD <- readxl::read_excel(archivoExcel,
                           col_types = "text",
                           col_names = paste("X", 1:43, sep = ""))
  
  BD <- BD %>%
    mutate(Periodo = X33[2])
  
  BD <- BD %>%
    select(Periodo, X1, X5, X9, X12, 
           X16, X22, X27, X31, X41)
  
  names(BD) <- c("Periodo", "NroEntrada", "Fuente",
                 "ClaseRegistro", "ClaseModif", "Fecha",
                 "Monto", "Cuenta", "Glosa", "Verificado")
  
  BD <- tail(BD, -20) %>% 
    filter(NroEntrada != is.na(NroEntrada))
  
  BD <- BD %>% 
    mutate(Fecha = as.Date(parse_integer(Fecha), origin = "1899-12-30"),
           Mes = str_c(str_pad(month(Fecha), 2, pad = "0"),
                       year(Fecha), sep = "/"),
           NroEntrada = parse_integer(NroEntrada),
           Monto = parse_number(Monto, locale = locale(decimal_mark = ".")),
           Remanente = ifelse(str_detect(Glosa, "REMANENTE"), T, F),
           INVICO = ifelse(str_detect(Glosa, "3*%"), T, F))
  
}
RecursosSIIF <- dir("Base de Datos/Reportes SIIF/Comprobantes de Recursos (rci02)/",
                    full.names = T) %>% map_df(readRecursosSIIF)

###Importamos Ejecucion Presupuesto Recursos SIIF por Código (ri102)
readRecursosPorCodigoSIIF <- function(archivoExcel){
  BD <- readxl::read_excel(archivoExcel,
                           col_types = "text",
                           col_names = paste("X", 1:28, sep = ""))
  
  BD <- BD %>%
    mutate(Periodo = X16[4])

  BD <- BD %>%
    select(Periodo, X1, X3, X10, X11, 
           X13, X14, X18, X21, X24)

  names(BD) <- c("Periodo", "CodRecurso", "Descripcion",
                 "Fuente", "OrgFin", "Presupuesto",
                 "Modificaciones", "PresupuestoVigente",
                 "Ingreso", "Saldo")

  BD <- tail(BD, -18) %>%
    filter(CodRecurso != is.na(CodRecurso))

  BD <- BD %>%
    mutate(Presupuesto = parse_number(Presupuesto, locale = locale(decimal_mark = ".")),
           Modificaciones = parse_number(Modificaciones, locale = locale(decimal_mark = ".")),
           PresupuestoVigente = parse_number(PresupuestoVigente, locale = locale(decimal_mark = ".")),
           Ingreso = parse_number(Ingreso, locale = locale(decimal_mark = ".")),
           Saldo = parse_number(Saldo, locale = locale(decimal_mark = ".")))
  
}
RecursosPorCodigoSIIF <- dir("Base de Datos/Reportes SIIF/Ejecucion Presupuestaria Recursos por Codigo (ri102)/",
                    full.names = T) %>% map_df(readRecursosPorCodigoSIIF)


##Exportamos
###Exportamos a SQLite
x <- RecursosSIIF %>% 
  rename(Ejercicio = Periodo)
AgregarRegistrosBD("SIIF", "ComprobantesRecursosSIIF", 
                   Data = x, overwrite = TRUE)

x <- RecursosPorCodigoSIIF %>% 
  rename(Ejercicio = Periodo)
AgregarRegistrosBD("SIIF", "EjecRecPorCodSIIF", 
                   Data = x, overwrite = TRUE)

###Exportamos a CSV
writeCSV(RecursosSIIF, "Recursos SIIF.csv")

writeCSV(RecursosPorCodigoSIIF, "Ejecucion Recursos por Codigo SIIF.csv")


#SIIF CONTABILIDAD---------------------------------------

##SIIF
###Importamos Movimientos Contables SIIF (rcocc31)
readMovContSIIF <- function(archivoExcel){
  BD <- readxl::read_excel(archivoExcel,
                           col_types = "text",
                           col_names = paste("X", 1:33, sep = ""))
  
  BD <- BD %>%
    mutate(Periodo = str_sub(X1[2], -4),
           Cuenta = paste(X6[9], X11[9], X12[9], sep = "-"))
  
  BD <- BD %>%
    select(Cuenta, Periodo, X3, X9, X14, 
           X19, X21, X24, X25, X27)
  names(BD) <- c("CuentaContable", "Periodo", "NroEntrada", "FechaAprobado", 
                 "Auxiliar1", "Auxiliar2", "TipoComprobante", 
                 "Debitos", "Creditos", "Saldo")
  BD <- tail(BD, -18) %>% 
    filter(NroEntrada != is.na(NroEntrada))
  #Null en Auxiliar 2?
  
}
MovContSIIF <- dir("Base de Datos/Reportes SIIF/Movimientos Contables (rcocc31)/",
                   full.names = T) %>% map_df(readMovContSIIF)
MovContSIIF <- MovContSIIF %>% 
  mutate(FechaAprobado = as.Date(parse_integer(FechaAprobado), origin = "1899-12-30"),
         Fecha = if_else(year(FechaAprobado) == Periodo, FechaAprobado,
                         dmy(str_c("31/12/", Periodo))),
         NroEntrada = parse_integer(NroEntrada),
         Debitos = parse_double(Debitos),
         Creditos = parse_double(Creditos),
         Saldo = parse_double(Saldo))

###Importamos Movimientos Contables Mensuales por Nivel SIIF (rcoasi81)
readMovContMensualSIIF <- function(archivoExcel){
  BD <- readxl::read_excel(archivoExcel,
                           col_types = "text",
                           col_names = paste("X", 1:20, sep = ""))

  BD <- BD %>%
    select(X1, X4, X6, X7, 
           X9, X11, X13, X16) 

  names(BD) <- c("Periodo", "Nivel", "Mayor",
                 "Subcuenta", "Auxiliar1", "Auxiliar2",
                 "Mes", "Saldo")
  
  BD <- tail(BD, -13) %>%
    filter(Periodo != is.na(Periodo))
  # #Null en Auxiliar 2?
  # 
}
MovContMensualSIIF <- dir("Base de Datos/Reportes SIIF/Movimientos Contables Mensuales por Nivel (rcoasi81)/",
                   full.names = T) %>% map_df(readMovContMensualSIIF)
MovContMensualSIIF <- MovContMensualSIIF %>% 
  mutate(Saldo = parse_number(Saldo, locale = locale(decimal_mark = ".")),
         CuentaContable = str_c(Nivel, Mayor, Subcuenta, sep = "-"),
         Fecha = dmy(str_c("01", Mes, Periodo, sep = "/")))

###Importamos Plan de Cuentas SIIF (rcopc02)
readPlanDeCuentasSIIF <- function(archivoExcel){
  BD <- readxl::read_excel(archivoExcel,
                           col_types = "text",
                           col_names = paste("X", 1:23, sep = ""))

  BD <- BD %>%
    select(X1, X4, X5, X6, X11, X13, 
           X14, X15, X16, X20, X22)
  
  names(BD) <- c("CuentaContable", "Mayor", "Subcuenta", 
                 "Descripcion", "Identificador",
                 "Auxiliar1", "DescripcionAuxiliar1",
                 "Auxiliar2", "DescripcionAuxiliar2",
                 "TotalDetalle", "NivelPub")
  
  BD <- tail(BD, -13)
  #   filter(NroEntrada != is.na(NroEntrada))
  # #Null en Auxiliar 2?
  
}
PlanDeCuentasSIIF <- dir("Base de Datos/Reportes SIIF/Plan de Cuentas (rcopc02)/",
                   full.names = T) %>% map_df(readPlanDeCuentasSIIF)

###Importamos tipo de Comprobante SIIF (archivo generado manualmente)
readAsientosTipoSIIF <- function(archivoExcel){
  BD <- readxl::read_excel(archivoExcel,
                           col_types = "text")
}
AsientosTipoSIIF <- readAsientosTipoSIIF("Base de Datos/Reportes SIIF/AsientosTiposSIIF.xlsx") 

##Exportamos
###Exportamos a SQLite
AgregarRegistrosBD("SIIF", "AsientosTipoSIIF", 
                   Data = AsientosTipoSIIF, overwrite = TRUE)

x <- MovContSIIF %>% 
  rename(Ejercicio = Periodo)
AgregarRegistrosBD("SIIF", "MayorPorCuentaSIIF", 
                   Data = x, overwrite = TRUE)

AgregarRegistrosBD("SIIF", "PlanDeCuentasSIIF", 
                   Data = PlanDeCuentasSIIF, overwrite = TRUE)

###Exportamos a CSV
MovContSIIF <- MovContSIIF %>% 
  select(CuentaContable, Periodo, Fecha, FechaAprobado, NroEntrada, everything())
writeCSV(MovContSIIF, "Movimientos Contables SIIF.csv")

MovContMensualSIIF <- MovContMensualSIIF %>% 
  select(CuentaContable, Periodo, Fecha, everything())
writeCSV(MovContMensualSIIF, "Movimientos Contables Mensuales SIIF.csv")

writeCSV(PlanDeCuentasSIIF, "Plan De Cuentas SIIF.csv")

writeCSV(AsientosTipoSIIF, "Asientos Tipo SIIF.csv")


#SIIF CLASIFICADORES----

##SIIF
###Importamos tipo de Comprobante SIIF (archivo generado manualmente)
readTipoComprobanteSIIF <- function(archivoExcel){
  BD <- readxl::read_excel(archivoExcel,
                           col_types = "text")
}
TipoComprobanteSIIF <- readTipoComprobanteSIIF("Base de Datos/Reportes SIIF/TipoComprobanteSIIF.xlsx") 

###Listado Fuentes Financiamiento SIIF (rff01)
readListadoFuentesSIIF <- function(archivoExcel){
  BD <- readxl::read_excel(archivoExcel,
                           col_types = "text",
                           col_names = paste("X", 1:20, sep = ""))

  BD <- BD %>%
    select(X2, X7, X15) %>% 
    transmute(Fuente = X2,
              Descripcion = X7,
              Abreviatura = X15) %>% 
    filter(!is.na(Fuente))

  
}
ListadoFuentesSIIF <- dir("Base de Datos/Reportes SIIF/Listado Fuentes (rff01)/",
                   full.names = T) %>% map_df(readListadoFuentesSIIF)

###Listado Partidas SIIF (rog01)
readListadoPartidasSIIF <- function(archivoExcel){
  BD <- readxl::read_excel(archivoExcel,
                           col_types = "text",
                           col_names = paste("X", 1:17, sep = ""))

  BD <- BD %>%
    tail(-12) %>% 
    select(X1, X3, X4, X5, X6, X10) %>%
    transmute(Grupo = X1,
              DescGrupo = X4,
              PartidaParcial = X3,
              DescPartidaParcial = X6,
              Partida = X5,
              DescPartida = X10) %>% 
    mutate(Grupo = zoo::na.locf(Grupo),
           DescGrupo = zoo::na.locf(DescGrupo)) %>% 
    tail(-1) %>% 
    mutate(PartidaParcial = zoo::na.locf(PartidaParcial),
           DescPartidaParcial = zoo::na.locf(DescPartidaParcial)) %>% 
    filter(!is.na(Partida))

  
}
ListadoPartidasSIIF <- dir("Base de Datos/Reportes SIIF/Listado Partidas (rog01)/",
                          full.names = T) %>% map_df(readListadoPartidasSIIF)

###Listado Cuentas Corrientes SIIF (rcu02)
readListadoCuentasCorrientesSIIF <- function(archivoExcel){
  BD <- readxl::read_excel(archivoExcel,
                           col_types = "text",
                           col_names = paste("X", 1:21, sep = ""))

  BD <- BD %>%
    select(X2, X7, X10, X15, X17) %>%
    transmute(CuentaAnterior = X2,
              Cuenta = X7,
              Descripcion = X10,
              Banco = X15,
              Activo = X17) %>%
    filter(!is.na(Descripcion)) %>% 
    mutate(Activo = ifelse(Activo == "S", 
                           "T", "F"),
           Activo = parse_logical(Activo))
  
}
ListadoCuentasCorrientesSIIF <- dir("Base de Datos/Reportes SIIF/Listado Cuentas Corrientes (rcu02)/",
                          full.names = T) %>% map_df(readListadoCuentasCorrientesSIIF)

##Exportamos
###Exportamos a SQLite
AgregarRegistrosBD("SIIF", "CuentasBancariasSIIF", 
                   Data = ListadoCuentasCorrientesSIIF, overwrite = TRUE)
x <- ListadoCuentasCorrientesSIIF %>% 
  filter(Activo == TRUE) %>% 
  select(-Activo)
AgregarRegistrosBD("ICARO", "CUENTASBANCARIAS", 
                   Data = x, overwrite = TRUE)


AgregarRegistrosBD("SIIF", "FuentesSIIF", 
                   Data = ListadoFuentesSIIF, overwrite = TRUE)
AgregarRegistrosBD("ICARO", "FUENTES", 
                   Data = ListadoFuentesSIIF, overwrite = TRUE)

AgregarRegistrosBD("SIIF", "PartidasSIIF", 
                   Data = ListadoPartidasSIIF, overwrite = TRUE)
AgregarRegistrosBD("ICARO", "PARTIDAS", 
                   Data = ListadoPartidasSIIF, overwrite = TRUE)

AgregarRegistrosBD("SIIF", "TipoComprobanteSIIF", 
                   Data = TipoComprobanteSIIF, overwrite = TRUE)

###Exportamos a CSV
writeCSV(TipoComprobanteSIIF, "Tipo Comprobante SIIF.csv")

writeCSV(ListadoFuentesSIIF, "Listado Fuentes SIIF.csv")

writeCSV(ListadoPartidasSIIF, "Listado Partidas SIIF.csv")

writeCSV(ListadoCuentasCorrientesSIIF, "Listado Cuentas Corrientes SIIF.csv")


#ICARO-----

##Importamos
###Comprobantes Cargados en ICARO
CargaICARO <- LeerBD("ICARO", "CARGA") %>% 
  as_tibble() %>% 
  mutate(Fecha = zoo::as.Date(Fecha))

###Retenciones Cargados en ICARO
RetencionesICARO <- LeerBD("ICARO", "RETENCIONES")

###Programas Cargados en ICARO
ProgramasICARO <- LeerBD("ICARO", "PROGRAMAS")

###Subprogamas Cargados en ICARO
SubprogramasICARO <- LeerBD("ICARO", "SUBPROGRAMAS")

###Proyectos Cargados en ICARO
ProyectosICARO <- LeerBD("ICARO", "PROYECTOS")

###Actividades Cargados en ICARO
ActividadesICARO <- LeerBD("ICARO", "ACTIVIDADES")

###Obras Cargados en ICARO
ObrasICARO <- LeerBD("ICARO", "OBRAS")

###Certificados Cargados en ICARO
CertificadosICARO <- LeerBD("ICARO", "CERTIFICADOS") %>% 
  filter(NroComprobanteSIIF != "")

###Rendiciones EPAM Cargados en ICARO
RendEPAMICARO <- LeerBD("ICARO", "EPAM") %>% 
  filter(NroComprobanteSIIF != "") %>% 
  mutate(FechaPago = zoo::as.Date(FechaPago))

##Exportamos
###Exportamos a SQLite


###Exportamos a CSV
writeCSV(CargaICARO, "ICARO Carga.csv")

writeCSV(RetencionesICARO, "ICARO Retenciones.csv")

writeCSV(ProgramasICARO, "ICARO Programas.csv")

writeCSV(SubprogramasICARO, "ICARO Subprogramas.csv")

writeCSV(ProyectosICARO, "ICARO Proyectos.csv")

writeCSV(ActividadesICARO, "ICARO Actividades.csv")

writeCSV(ObrasICARO, "ICARO Obras.csv")

writeCSV(CertificadosICARO, "ICARO Certificados SGF.csv")

writeCSV(RendEPAMICARO, "ICARO EPAM SGF.csv")


#BANCO REAL---------------------------------------

##MOVIMIENTOS MENSUALES BANCO REAL
###Importamos los archivos de movimiento mensuales BCOR
readMovBCOR <- function(archivoExcel){
  BD <- readxl::read_excel(archivoExcel,
                           col_names = paste("X", 1:7, sep = ""),
                           col_types = "text")
  BD <- BD %>% 
    select(-X5)
  names(BD) <- c("Fecha", "Monto", "NroCheque",
                 "Concepto", "Referencia","Saldo")
  BD <- BD %>% 
    mutate(Cuenta = str_split(Monto[7]," | ", simplify = T)[1,6])
  BD <- tail(BD, -9)
  
}
MovBCOR <- dir("Base de Datos/Movimientos Mensuales BANCO/Banco de Corrientes/",
               full.names = T) %>% map_df(readMovBCOR)
MovBCOR <- MovBCOR %>% 
  mutate(Fecha = dmy(Fecha),
         Monto = parse_number(Monto, 
                              locale = locale(decimal_mark = ",",
                                              grouping_mark = ".")),
         Saldo = parse_number(Saldo, 
                              locale = locale(decimal_mark = ",",
                                              grouping_mark = ".")),
         EsCheque = ifelse(NroCheque != "0" & Concepto != "Acred. Ch.Camara", TRUE, FALSE))

###Importamos los archivos de movimiento mensuales BNAC
readMovBNAC <- function(archivoExcel){
  BD <- readxl::read_excel(archivoExcel,
                           col_names = paste("X", 1:6, sep = ""),
                           col_types = "text")
  names(BD) <- c("FechaMov", "Fecha", "Monto",
                 "Referencia", "Concepto","Saldo")
  BD <- BD %>%
    mutate(Cuenta = str_split(Fecha[7]," | ", simplify = T)[1,6])
  BD <- tail(BD, -9)
  
}
MovBNAC <- dir("Base de Datos/Movimientos Mensuales BANCO/Banco Nacion/",
               full.names = T) %>% map_df(readMovBNAC)
MovBNAC <- MovBNAC %>% 
  mutate(FechaMov = as.Date(parse_integer(FechaMov), 
                            origin = "1899-12-30"),
         Fecha = as.Date(parse_integer(Fecha), 
                         origin = "1899-12-30"),
         Monto = parse_number(Monto, 
                              locale = locale(decimal_mark = ",",
                                              grouping_mark = ".")),
         Saldo = parse_number(Saldo, 
                              locale = locale(decimal_mark = ",",
                                              grouping_mark = ".")),
         NroCheque = as.character(parse_integer(Referencia)),
         EsCheque = ifelse((str_detect(Concepto,"CHEQ") | str_detect(Concepto,"CHQ")) & 
                             !str_detect(Concepto,"COM") & !str_detect(Concepto,"DEP"), T,
                           ifelse(str_ends(Referencia, str_sub(Concepto,-9)), T,
                                  ifelse(str_detect(Concepto,"COB"), T, F)))) #Concepto == "COBRADO POR CAJA" decía antes

###Combinamos Banco Nación con Provincia
MovBancoReal <- full_join(MovBNAC, MovBCOR)
rm(MovBCOR, MovBNAC)

##Exportamos
writeCSV(MovBancoReal, "Movimientos Bancos Ctes y Nac.csv")


#LISTADO PROVEEDORES INVICO---------------------------------------

##SGF
###Importamos el Listado de Proveedores INVICO SGF
ProveedoresINVICO <- read_csv("Base de Datos/Sistema Gestion Financiera/Otros Reportes/Listado de Proveedores.csv",
                             col_names = F, col_types = str_c(rep("c", 18), collapse = ""),
                             locale = locale(encoding = 'ISO-8859-1'))
ProveedoresINVICO <- ProveedoresINVICO[,10:16]
names(ProveedoresINVICO) <- c("Codigo","Descripcion","Domicilio", "Localidad",
                             "Telefono","CUIT","CondicionIVA")
ProveedoresINVICO <- mutate(ProveedoresINVICO, Codigo = parse_integer(Codigo))
ProveedoresINVICO$CUIT <- gsub('-', '', ProveedoresINVICO$CUIT)
ProveedoresINVICO <- ProveedoresINVICO %>% 
  mutate(CUIT = ifelse(!str_detect(Descripcion, "ARGOITIA NILDA"), CUIT, "27136933375"),
         CUIT = ifelse(!str_detect(Descripcion, "PEREZ, ELENA"), CUIT, "27249377290"),
         CUIT = ifelse(!str_detect(Descripcion, "LAZZARESCHI CLAUDIO"), CUIT, "20230733040"),
         CUIT = ifelse(!str_detect(Descripcion, "GALIANO MARIA"), CUIT, "27125290499"),
         CUIT = ifelse(!str_detect(Descripcion, "CUEVAS MARIA"), CUIT, "27263746975"),
         CUIT = ifelse(!str_detect(Descripcion, "YAÑEZ CALDERON"), CUIT, "27258769428"),
         CUIT = ifelse(!str_detect(Descripcion, "CABRAL JOSE"), CUIT, "20285911568"),
         CUIT = ifelse(!str_detect(Descripcion, "LOPEZ SILVANA"), CUIT, "23256066114"),
         CUIT = ifelse(!str_detect(Descripcion, "AYALA ORTIZ"), CUIT, "27236633581"),
         CUIT = ifelse(!str_detect(Descripcion, "COTORRUELO, MARIA"), CUIT, "27062388558"),
         CUIT = ifelse(!str_detect(Descripcion, "BURGOS ALICIA"), CUIT, "27177677367"),
         CUIT = ifelse(!str_detect(Descripcion, "SICARDI MARIA"), CUIT, "27166324594"))

##AFIP
###Importamos la BD AFIP con descripción 
AFIP <- read_fwf("Base de Datos/AFIP/AFIPconDenominacion.tmp", fwf_widths(c(11, 30, 2, 2, 2, 1, 1, 2),
                                                                            c("CUIT", "DenominacionAFIP", "Gcias", "IVA", "Monotributo",
                                                                              "IntegranteSoc", "Empleador", "ActividadEconomica")), 
                 col_types = "cccccccc", locale = locale(encoding = 'ISO-8859-1'))

###Combinamos tabla AFIP y Proveedores INVICO
ProveedoresINVICOAFIP <- left_join(ProveedoresINVICO, AFIP) %>% 
  filter(!is.na(CUIT))
rm(AFIP)

##Exportamos
###Exportamos SQLite
AgregarRegistrosBD("SGF", "ProveedoresSGF",
                   Data = ProveedoresINVICO, overwrite = TRUE)
AgregarRegistrosBD("ICARO", "PROVEEDORES",
                   Data = ProveedoresINVICO, overwrite = TRUE)

AgregarRegistrosBD("SGF", "ProveedoresSGFAFIP",
                   Data = ProveedoresINVICOAFIP, overwrite = TRUE)

###Exportamos CSV
writeCSV(ProveedoresINVICOAFIP, "Listado Provedores AFIP.csv")

writeCSV(ProveedoresINVICO, "Listado Provedores INVICO.csv")


#CUENTAS UNICAS---------------------------------------

##Clave Principal CUENTA
BancoSIIF <- MovContSIIF %>% 
  filter(CuentaContable == "1112-2-6")

CuentasBancarias <- cbind.fill(str_sort(unique(MovSSCC$Cuenta), decreasing = F), 
                               str_sort(unique(MovBancoReal$Cuenta), decreasing = F),
                               str_sort(unique(BancoSIIF$Auxiliar1), decreasing = F),
                               str_sort(unique(ComprobantesGtoSIIF$Cuenta), decreasing = F),
                               str_sort(unique(RecursosSIIF$Cuenta), decreasing = F),
                               str_sort(unique(ResumenRendSGF$Cuenta), decreasing = F),
                               str_sort(unique(ListadoCuentasCorrientesSIIF$Cuenta), decreasing = F),
                               str_sort(unique(CargaICARO$Cuenta), decreasing = F)) %>%
  rename(CuentasSSCC = X1, CuentasBcoReal = X2,  CuentasContabilidadSIIF = X3, 
         CuentasGastosSIIF = X4, CuentasRecursosSIIF = X5, CuentasSGF = X6, 
         CuentasSIIF = X7, CuentasICAROAnterior = X8)

##Exportamos
writeCSV(CuentasBancarias, "Cuentas Bancarias.csv")
