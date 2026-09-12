# C3 revisión 02 — expediente final

Abrir **C3_integral_revision02_final 1.dsb**. Incluye resultados anuales guardados.
XML de intercambio: C3_integral_revision02_final.xml.
Corrida válida: corrida-02. EnergyPlus 9.4: 324 advertencias, 0 errores severos.
Demanda total de enfriamiento: 65.767,88 kWh térmicos/año, reducción del 22,41 % frente al CB.

Los archivos inicial y estable son antecedentes descartados; NO usar para continuar.
La primera corrida no convergió con 25 días máximos de inicialización. La corrida final usa 100, sin relajar tolerancias.
Se conservan los archivos históricos; el informe de errores final está en corrida-02/eplusout.err.

8 W/m² en 19 zonas. Se configuraron 19 controles de luz natural, pero seis no actúan por ausencia de ventanas exteriores.
Los resultados no acreditan certificación: faltan confort horario, sDA/ASE, aire exterior, agua, EPD, selección comercial y otros documentos del plan de 16 criterios.

Reproducción desde los resultados archivados:
1. preparar_tablas.py: extrae ESO de CB y corrida-02; concilia demanda horaria/anual.
2. graficos_resultados.py: exporta tablas y figuras al repositorio principal.
3. temperaturas_ocupadas.py: contrasta oficinas con horario del IDF, 3.130 horas ocupadas.
Los scripts usan rutas del equipo de Juan Ortiz. validar_y_resguardar.py lee resultados LIVE de DesignBuilder: no ejecutarlo después de simular otro caso.
cerrar_documento.py es una migración de una sola ejecución; no repetir sobre un capítulo ya editado.

La tesis principal está en Desktop/Tesis de Maestria - Juan Ortiz/01_Documento_tesis/Repositorios/Trabajo_completo/Tesis-limpia.
Capítulos 3 y 4 conservados; capítulo 5 organizado y ampliado. El PDF completo se genera en main.pdf.
