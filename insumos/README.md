# Insumos

Carpeta para guardar documentos fuente que alimentan la tesis antes de integrarlos al documento principal.

Aqui pueden colocarse denuncias de tesis, borradores, fichas, informes, apuntes, matrices, documentos oficiales del proyecto y otros materiales de trabajo.

Regla de uso:

- Los archivos en esta carpeta sirven como fuente de informacion.
- El contenido integrado a la tesis debe pasar a `main.tex` o a los archivos de `capitulos/`.
- No subir documentos con datos personales sensibles sin revisar antes si conviene limpiarlos o resumirlos.

## Documentos guardados

- `2026-02-23 Denuncia Tesis Juan Ortiz.docx`: denuncia de tesis usada como insumo base para estructurar resumen, problematica, objetivos, marco teorico, metodologia, plan de trabajo y anexos.
- `datos-climaticos-san-cristobal-resumen.md`: sintesis del archivo climatico diario de San Cristobal para integrar a la metodologia y al caso de estudio.
- `epw-san-cristobal-tmyx-2011-2025-resumen.md`: sintesis del archivo EPW horario TMYx 2011-2025 de San Cristobal, fuente climatica principal para simulacion.
- `graficos-epw-san-cristobal.md`: resumen de los graficos generados desde el EPW y tabla mensual usada para las figuras.
- `../figuras/epw-uniforme-temperatura-mensual.pdf`: grafico separado de temperatura del EPW con estilo grafico homogeneo.
- `../figuras/epw-uniforme-humedad-relativa.pdf`: grafico separado de humedad relativa del EPW con estilo grafico homogeneo.
- `../figuras/epw-uniforme-radiacion-solar.pdf`: grafico separado de radiacion solar del EPW con estilo grafico homogeneo.
- `../figuras/epw-uniforme-viento-mensual.pdf`: grafico separado de velocidad del viento del EPW con estilo grafico homogeneo.
- `../figuras/epw-uniforme-rosa-vientos.pdf`: grafico separado de direccion predominante del viento del EPW con estilo grafico homogeneo.
- `../figuras/epw-uniforme-mapa-horario-temperatura.pdf`: grafico separado de temperatura horaria del EPW con estilo grafico homogeneo.
- `idf-caso-base-1-3-resumen.md`: interpretacion tecnica del archivo IDF exportado desde DesignBuilder para el escenario base.
- `idf-zonas-caso-base.md` y `idf-zonas-caso-base.csv`: tabla de zonas termicas extraida del IDF del caso base.
- `marco-teorico-borrador-extraido.md`: extraccion del documento Word de marco teorico usado para reconstruir el capitulo 2 con citas BibLaTeX.
- `summary-espacios.md`, `summary-espacios.csv` y `summary-espacios-tablas.tex`: cuadros de geometria, envolvente y cargas internas por espacio extraidos del reporte Summary de EnergyPlus.
- `../datos/iluminancia-designbuilder.csv`: resultados tabulares de iluminancia y factor de luz dia por zona, exportados desde DesignBuilder.
- `iluminancia-resumen-tabla.tex`: tabla LaTeX con el resumen de iluminancia natural por espacio.
- `../datos/cooling-design-designbuilder.csv`: serie horaria del dia de diseno de enfriamiento exportada desde DesignBuilder.
- `cooling-design-resumen.md` y `cooling-design-resumen-tabla.tex`: resumen de componentes y condiciones criticas del dia de diseno de enfriamiento.
