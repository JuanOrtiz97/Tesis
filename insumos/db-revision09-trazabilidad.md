# Revisión 09 — 12 de septiembre de 2026

Modelo nativo: CB_revision_cargas 1.dsb. Fuente de entradas: datos/db-caso-base-revision09.idf. Salidas resumidas: db-resultados-revision09.json.

EnergyPlus 9.4.0.002: ejecución anual completada en 3 min 4,66 s; 318 advertencias y 0 errores severos. Entorno climático SAN CRISTOBAL (01-01:31-12), 8760 registros horarios por serie. Los días de dimensionamiento no se incluyeron en la integración.

Energía térmica = suma de tasas horarias [W] por una hora / 1000. Se suman las 25 series Zone Ideal Loads Supply Air Sensible Cooling Rate y, por separado, Total Cooling Rate. No se agregan ambas magnitudes entre sí. Las temperaturas corresponden a Zone Operative Temperature y no a la variable de confort ponderada por ocupación.

Cambios respecto de la revisión 08: factor metabólico del SUM de 0,1 a 1, conservando actividad seleccionada de 120 W/persona; Timestep de 4 a 6. No se modificó la carga de 500 W/m² del DC sin confirmación del inventario. Persisten comprobaciones del día de invierno, de encuentros geométricos y de las aberturas horizontales AFN.

Las imágenes son capturas reales de DesignBuilder, recortadas en LaTeX para excluir la interfaz. La vista solar es ilustrativa y no es una predicción de ahorro. Las tres imágenes de iluminancia se sustituyeron por capturas del cálculo estático actualizado el 12 de septiembre de 2026. La cuadrícula de 19 zonas se transcribió con la precisión visible y se contrastó con su total; captura de evidencia: iluminancia-tabla-actual.png en la carpeta local de revisión. Las áreas redondeadas por zona suman 253,485 m² frente al total nativo 253,482 m² (diferencia de redondeo 0,003 m²).

El IDF incorporado al repositorio conserva los campos exportados y normaliza únicamente espacios finales y saltos de línea. El original permanece en la carpeta de la corrida.

## Actualización integral de datos, tablas y gráficos

- `datos/Datos Caso Base3.csv`: 365 fechas únicas, 30 variables, unidades y orden de columnas conservados. Exportación diaria nativa `datos-diarios-09.txt`, UTF-16, máxima precisión; el CSV utiliza punto y coma, coma decimal y fechas DD/MM/AAAA. Original externo actualizado con copia de respaldo.
- Enfriamiento sensible integrado del CSV: 59018,63313 kWh; ESO: 59018,633847 kWh. Diferencia inferior a 0,001 kWh por precisión de exportación. Total: 84759,41122 frente a 84759,410853 kWh.
- `scripts/actualizar_resultados_cb09.py` regenera tres tablas, seis gráficos vectoriales y sus PNG. Electricidad estimada y energía térmica se presentan por separado.
- `datos/iluminancia-designbuilder.csv`: cielo CIE cubierto especificado de 10000 lux; plano 0,76 m; malla 0,30 m; detalle bueno, cuatro rebotes. Cálculo puntual, no anual. Umbral FLD 2%; total nativo 68,366% del área y FLD promedio 3,816%.
- El inventario térmico incluye 28 zonas; la cuadrícula lumínica incluye 19 espacios. No confundir ambas superficies ni incorporar vacíos como área útil.
- Muro exterior: propiedades del IDF actual; R de capas 0,201760 m²K/W, masa 343,2 kg/m² y capacidad por superficie 338,304 kJ/m²K. Se retiraron de capítulo 4 las tres tablas Ubakus incompatibles; el archivo histórico se conserva.
- Clima: se recomprobaron los 8760 registros del EPW; las cifras climáticas existentes coinciden y sus gráficos permanecen vigentes.
- Pendientes físicos conservados: inventario DC, dimensionamiento de invierno, encuentros geométricos y representación AFN. No se proclama ahorro ni certificación definitiva.
