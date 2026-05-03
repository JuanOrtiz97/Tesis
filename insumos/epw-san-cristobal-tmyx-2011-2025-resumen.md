# Resumen del archivo EPW de San Cristobal

Fuente local: `datos/ECU_GA_San.Cristobal.Intl.AP.840080_TMYx.2011-2025.epw`

Archivo original: `ECU_GA_San.Cristobal.Intl.AP.840080_TMYx.2011-2025.epw`

## Identificacion

| Campo | Valor |
|---|---:|
| Estacion | San.Cristobal.Intl.AP |
| Pais | Ecuador |
| Codigo WMO | 840080 |
| Latitud | -0,91700 |
| Longitud | -89,61700 |
| Zona horaria | -6 |
| Elevacion | 18,9 m |
| Fuente | SRC-TMYx |
| Periodo de registro | 2011-2025 |
| Registros climaticos | 8760 horas |

El archivo corresponde a un ano meteorologico tipico TMYx. El encabezado indica que cada mes representativo proviene de anos diferentes dentro del periodo 2011-2025: enero 2017, febrero 2014, marzo 2012, abril 2019, mayo 2011, junio 2021, julio 2025, agosto 2011, septiembre 2011, octubre 2011, noviembre 2016 y diciembre 2016.

## Sintesis anual

| Indicador | Valor |
|---|---:|
| Temperatura media anual de bulbo seco | 24,28 °C |
| Temperatura minima horaria | 15,70 °C |
| Temperatura maxima horaria | 32,90 °C |
| Punto de rocio medio | 20,80 °C |
| Humedad relativa media | 81,37 % |
| Presion atmosferica media | 101092,89 Pa |
| Radiacion global horizontal anual | 2150,50 kWh/m2 |
| Radiacion global horizontal media diaria | 5,89 kWh/m2-dia |
| Radiacion directa normal anual | 2002,37 kWh/m2 |
| Radiacion difusa horizontal anual | 666,57 kWh/m2 |
| Radiacion infrarroja horizontal media | 396,83 W/m2 |
| Velocidad media del viento | 4,90 m/s |
| Direccion media circular del viento | 155,53° |
| Cobertura total media de cielo | 7,27 octas |
| Precipitacion liquida anual registrada | 126,20 mm |

## Sintesis mensual

| Mes | Temp. media (°C) | HR media (%) | GHI (kWh/m2) | DNI (kWh/m2) | DHI (kWh/m2) | Viento (m/s) |
|---:|---:|---:|---:|---:|---:|---:|
| 01 | 25,61 | 84,5 | 187,8 | 196,1 | 49,1 | 3,26 |
| 02 | 26,68 | 80,1 | 174,3 | 173,3 | 47,5 | 4,98 |
| 03 | 27,10 | 80,9 | 207,9 | 224,2 | 42,2 | 2,27 |
| 04 | 26,75 | 85,3 | 190,7 | 193,9 | 43,0 | 3,88 |
| 05 | 25,96 | 81,4 | 179,6 | 175,7 | 49,4 | 5,38 |
| 06 | 24,18 | 80,7 | 164,0 | 159,3 | 48,5 | 5,73 |
| 07 | 23,11 | 83,8 | 163,2 | 149,5 | 57,7 | 5,44 |
| 08 | 22,11 | 80,2 | 170,6 | 140,5 | 65,1 | 5,69 |
| 09 | 21,73 | 82,0 | 167,7 | 122,2 | 69,3 | 5,82 |
| 10 | 22,14 | 74,6 | 183,0 | 138,8 | 75,1 | 5,21 |
| 11 | 22,49 | 78,3 | 179,5 | 155,2 | 64,3 | 6,02 |
| 12 | 23,69 | 84,5 | 182,3 | 173,7 | 55,3 | 5,15 |

## Lectura para la tesis

El EPW confirma una condicion calido-humeda con temperatura anual moderada, humedad elevada, cielo frecuentemente cubierto y radiacion solar importante. Marzo es el mes mas calido del ano meteorologico tipico, con 27,10 °C de temperatura media, mientras septiembre presenta la media mensual mas baja, con 21,73 °C.

La radiacion global horizontal anual de 2150,50 kWh/m2 y la radiacion media diaria de 5,89 kWh/m2-dia justifican que el control solar, el diseno de cubierta, el sombreamiento de vanos y la reduccion de ganancias por envolvente sean variables centrales del caso de estudio. La velocidad media del viento, 4,90 m/s, respalda la evaluacion de ventilacion natural, siempre que la arquitectura permita captacion, recorrido y extraccion de aire.

Para simulacion, este EPW debe considerarse la fuente principal frente al resumen CSV diario, porque mantiene resolucion horaria y contiene las variables completas requeridas por EnergyPlus.
