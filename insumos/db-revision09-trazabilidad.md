# Revisión 09 — 12 de septiembre de 2026

Modelo nativo: CB_revision_cargas 1.dsb. Fuente de entradas: datos/db-caso-base-revision09.idf. Salidas resumidas: db-resultados-revision09.json.

EnergyPlus 9.4.0.002: ejecución anual completada en 3 min 4,66 s; 318 advertencias y 0 errores severos. Entorno climático SAN CRISTOBAL (01-01:31-12), 8760 registros horarios por serie. Los días de dimensionamiento no se incluyeron en la integración.

Energía térmica = suma de tasas horarias [W] por una hora / 1000. Se suman las 25 series Zone Ideal Loads Supply Air Sensible Cooling Rate y, por separado, Total Cooling Rate. No se agregan ambas magnitudes entre sí. Las temperaturas corresponden a Zone Operative Temperature y no a la variable de confort ponderada por ocupación.

Cambios respecto de la revisión 08: factor metabólico del SUM de 0,1 a 1, conservando actividad seleccionada de 120 W/persona; Timestep de 4 a 6. No se modificó la carga de 500 W/m² del DC sin confirmación del inventario. Persisten comprobaciones del día de invierno, de encuentros geométricos y de las aberturas horizontales AFN.

Las imágenes son capturas reales de DesignBuilder, recortadas en LaTeX para excluir la interfaz. La vista solar es ilustrativa y no es una predicción de ahorro. Las imágenes de iluminancia anteriores se identifican como antecedente pendiente de actualización.

El IDF incorporado al repositorio conserva los campos exportados y normaliza únicamente espacios finales y saltos de línea. El original permanece en la carpeta de la corrida.
