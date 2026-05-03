# Resumen de datos climaticos de San Cristobal

Fuente local: `datos/datos-climaticos-san-cristobal.csv`

Nota de uso: este CSV se conserva como resumen diario de apoyo. Para simulacion energetica y redaccion final de clima se debe usar como fuente principal el archivo EPW `datos/ECU_GA_San.Cristobal.Intl.AP.840080_TMYx.2011-2025.epw`, porque contiene 8760 registros horarios y corresponde al TMYx 2011-2025.

El archivo contiene 365 registros diarios, desde el 1 de enero de 2002 hasta el 31 de diciembre de 2002. La estructura original usa separador de punto y coma, coma decimal y una segunda fila con unidades.

## Variables disponibles

| Variable original | Unidad | Uso en la tesis |
|---|---:|---|
| Date/Time | fecha | Periodo diario del ano climatico de referencia |
| Outside Dry-Bulb Temperature | °C | Temperatura exterior para caracterizacion climatica y simulacion |
| Outside Dew-Point Temperature | °C | Estimacion de humedad relativa y condicion higrotermica |
| Direct Normal Solar | kWh/m2 | Radiacion solar directa |
| Diffuse Horizontal Solar | kWh/m2 | Radiacion solar difusa |
| Wind Speed | m/s | Potencial de ventilacion natural |
| Wind Direction | ° | Direccion predominante del viento |
| Atmospheric Pressure | Pa | Condicion atmosferica de entrada |
| Solar Altitude | ° | Geometria solar |
| Solar Azimuth | ° | Geometria solar |

## Sintesis anual

| Indicador | Valor |
|---|---:|
| Temperatura media anual | 24,28 °C |
| Temperatura minima diaria | 19,96 °C |
| Temperatura maxima diaria | 28,82 °C |
| Punto de rocio medio | 20,80 °C |
| Humedad relativa estimada media | 81,06 % |
| Radiacion directa normal anual | 2002,37 kWh/m2 |
| Radiacion difusa horizontal anual | 659,08 kWh/m2 |
| Radiacion global diaria media estimada por suma DNI+DHI | 7,29 kWh/m2 |
| Radiacion global anual estimada por suma DNI+DHI | 2661,45 kWh/m2 |
| Velocidad media del viento | 4,90 m/s |
| Direccion media del viento | 156,02° |
| Presion atmosferica media | 101092,89 Pa |

Nota tecnica: la humedad relativa se estimo a partir de la temperatura de bulbo seco y el punto de rocio mediante una aproximacion psicrometrica. La radiacion global del CSV se calculo como suma de radiacion directa normal y difusa horizontal solo para una lectura exploratoria; no reemplaza la radiacion global horizontal horaria del EPW.

## Lectura para la tesis

San Cristobal presenta una condicion calido-humeda, con temperatura media anual moderada, humedad relativa alta y radiacion solar significativa. Los meses con mayor temperatura media son febrero, marzo y abril; septiembre presenta la temperatura media mas baja del archivo. La velocidad de viento media es suficiente para justificar la evaluacion de ventilacion natural, siempre que el edificio permita captacion, recorrido y extraccion de aire.

Estos datos respaldan que la metodologia priorice control solar, ventilacion natural, reduccion de ganancias termicas en envolvente, seleccion de materiales de baja acumulacion de calor o alta pertinencia higrotermica, y evaluacion comparativa de escenarios mediante simulacion energetica.
